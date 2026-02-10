"""核心录制引擎 - 管理整个录制流程"""

import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Callable, Tuple
import numpy as np

from core.screen_capture import ScreenCapture
from core.video_writer import VideoWriter


class RecorderState:
    """录制状态枚举"""
    IDLE = "idle"          # 空闲
    RECORDING = "recording" # 录制中
    PAUSED = "paused"      # 已暂停
    STOPPING = "stopping"   # 停止中


class Recorder:
    """核心录制引擎"""

    def __init__(self):
        """初始化录制器"""
        self.state = RecorderState.IDLE
        self.screen_capture = ScreenCapture()
        self.video_writer: Optional[VideoWriter] = None

        # 录制参数
        self.fps = 30
        self.region: Optional[Dict] = None
        self.output_path: Optional[str] = None
        self.codec = 'H264'

        # 音频相关
        self.enable_audio = False
        self.audio_source = 'both'
        self.audio_device_index = None
        self.audio_capture = None
        self.temp_audio_path = None

        # 线程控制
        self._record_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()

        # 统计信息
        self._start_time: Optional[float] = None
        self._frame_count = 0
        self._actual_fps = 0.0
        self._recording_duration = 0.0  # 实际录制时长（秒）

        # 回调函数
        self.on_frame_captured: Optional[Callable[[np.ndarray], None]] = None
        self.on_recording_started: Optional[Callable[[], None]] = None
        self.on_recording_stopped: Optional[Callable[[str, int, float], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None

    def start_recording(self,
                       output_path: str,
                       fps: int = 30,
                       region: Optional[Dict] = None,
                       codec: str = 'H264',
                       enable_audio: bool = False,
                       audio_source: str = 'both',
                       audio_device: Optional[int] = None) -> bool:
        """
        开始录制

        Args:
            output_path: 输出文件路径
            fps: 帧率
            region: 录制区域字典 {'top': y, 'left': x, 'width': w, 'height': h}
                   如果为None，则录制主显示器全屏
            codec: 视频编码器
            enable_audio: 是否启用音频录制
            audio_source: 音频源 ('mic', 'system', 'both')
            audio_device: 麦克风设备索引

        Returns:
            bool: 是否成功开始录制
        """
        if self.state != RecorderState.IDLE:
            self._trigger_error("录制器正在运行，请先停止当前录制")
            return False

        try:
            # 保存音频设置
            self.enable_audio = enable_audio
            self.audio_source = audio_source
            self.audio_device_index = audio_device

            # 如果启用音频，启动音频录制
            if enable_audio:
                from core.audio_capture import AudioCapture
                self.audio_capture = AudioCapture()
                self.audio_capture.start_recording(audio_source, audio_device)
                # 生成临时音频文件路径
                self.temp_audio_path = output_path.replace('.mp4', '_temp.wav')

            # 设置参数
            self.output_path = output_path
            self.fps = max(1, min(fps, 120))  # 限制FPS在1-120之间
            self.region = region
            self.codec = codec

            # 确定录制区域
            if region is None:
                monitor = self.screen_capture.get_primary_monitor()
            else:
                monitor = region

            resolution = (monitor['width'], monitor['height'])

            # 创建视频写入器
            self.video_writer = VideoWriter(
                self.output_path,
                self.fps,
                resolution,
                self.codec
            )

            if not self.video_writer.open():
                self._trigger_error(f"无法创建视频文件: {self.output_path}")
                return False

            # 重置状态
            self._stop_event.clear()
            self._pause_event.clear()
            self._frame_count = 0
            self._start_time = time.time()

            # 启动录制线程
            self._record_thread = threading.Thread(
                target=self._record_loop,
                args=(monitor,),
                daemon=True
            )
            self.state = RecorderState.RECORDING
            self._record_thread.start()

            # 触发回调
            if self.on_recording_started:
                self.on_recording_started()

            return True

        except Exception as e:
            self.state = RecorderState.IDLE
            self._trigger_error(f"启动录制失败: {str(e)}")
            return False

    def pause_recording(self) -> bool:
        """
        暂停录制

        Returns:
            bool: 是否成功暂停
        """
        if self.state != RecorderState.RECORDING:
            return False

        self.state = RecorderState.PAUSED
        self._pause_event.set()
        return True

    def resume_recording(self) -> bool:
        """
        继续录制

        Returns:
            bool: 是否成功继续
        """
        if self.state != RecorderState.PAUSED:
            return False

        self.state = RecorderState.RECORDING
        self._pause_event.clear()
        return True

    def stop_recording(self) -> bool:
        """
        停止录制

        Returns:
            bool: 是否成功停止
        """
        if self.state == RecorderState.IDLE:
            return False

        self.state = RecorderState.STOPPING
        self._stop_event.set()

        # 等待录制线程结束
        if self._record_thread and self._record_thread.is_alive():
            self._record_thread.join(timeout=5.0)

        # 关闭视频写入器
        if self.video_writer:
            self.video_writer.close()

        # 计算实际录制时长和实际FPS
        recording_duration = time.time() - self._start_time if self._start_time else 0
        actual_fps = self._frame_count / recording_duration if recording_duration > 0 else self.fps

        # 停止音频录制并合并
        if self.enable_audio and self.audio_capture:
            self.audio_capture.stop_recording()
            audio_saved = False

            # 保存音频到临时文件
            if self.temp_audio_path:
                audio_saved = self.audio_capture.save_to_file(self.temp_audio_path)

            # 如果音频保存成功，进行合并
            if audio_saved:
                temp_video_path = self.output_path.replace('.mp4', '_temp_video.mp4')

                # 重命名原视频
                import os
                try:
                    if os.path.exists(self.output_path):
                        os.rename(self.output_path, temp_video_path)

                    # 合并音视频，使用实际FPS修正视频时间戳
                    from utils.audio_merger import merge_audio_video
                    success = merge_audio_video(
                        temp_video_path,
                        self.temp_audio_path,
                        self.output_path,
                        video_fps=actual_fps
                    )

                    # 清理临时文件
                    try:
                        if os.path.exists(temp_video_path):
                            os.remove(temp_video_path)
                        if os.path.exists(self.temp_audio_path):
                            os.remove(self.temp_audio_path)
                    except:
                        pass

                    if not success:
                        # 合并失败，恢复原视频
                        if os.path.exists(temp_video_path):
                            os.rename(temp_video_path, self.output_path)

                except Exception as e:
                    print(f"音视频合并失败: {e}")

            # 清理音频捕获器
            try:
                self.audio_capture.cleanup()
            except:
                pass
            self.audio_capture = None

        # 如果没有音频录制，但实际FPS与设定FPS差异较大，需要修正视频
        elif not self.enable_audio and self._frame_count > 0:
            # 只有当实际FPS与设定FPS差异超过5%时才修正
            if abs(actual_fps - self.fps) / self.fps > 0.05:
                import os
                try:
                    temp_video_path = self.output_path.replace('.mp4', '_temp_video.mp4')
                    if os.path.exists(self.output_path):
                        os.rename(self.output_path, temp_video_path)

                    # 使用实际FPS重新封装视频
                    from utils.audio_merger import fix_video_fps
                    fix_video_fps(temp_video_path, self.output_path, actual_fps)

                    # 清理临时文件
                    try:
                        if os.path.exists(temp_video_path):
                            os.remove(temp_video_path)
                    except:
                        pass
                except Exception as e:
                    print(f"修正视频FPS失败: {e}")

        # 触发回调
        if self.on_recording_stopped:
            duration = time.time() - self._start_time if self._start_time else 0
            self.on_recording_stopped(
                self.output_path,
                self._frame_count,
                duration
            )

        # 重置状态
        self.state = RecorderState.IDLE
        self._record_thread = None
        return True

    def _record_loop(self, monitor: Dict):
        """
        录制循环（在独立线程中运行）

        Args:
            monitor: 录制区域/显示器信息
        """
        frame_interval = 1.0 / self.fps  # 目标帧间隔（秒）
        next_frame_time = time.time()  # 下一帧的目标时间

        while not self._stop_event.is_set():
            # 检查暂停状态
            if self._pause_event.is_set():
                time.sleep(0.1)
                next_frame_time = time.time()  # 暂停后重置时间基准
                continue

            try:
                # 捕获帧
                frame = self.screen_capture.capture_screen(monitor)

                # 写入帧
                if self.video_writer:
                    self.video_writer.write_frame(frame)
                    self._frame_count += 1

                # 触发帧回调
                if self.on_frame_captured:
                    self.on_frame_captured(frame)

                # 计算实际FPS
                current_time = time.time()
                elapsed = current_time - self._start_time if self._start_time else 1
                self._actual_fps = self._frame_count / elapsed if elapsed > 0 else 0

                # 计算下一帧的目标时间
                next_frame_time += frame_interval

                # 控制帧率：等待直到下一帧的目标时间
                remaining_time = next_frame_time - time.time()
                if remaining_time > 0:
                    time.sleep(remaining_time)
                # 如果处理时间超过了帧间隔，立即继续（丢帧以保证时间准确）

            except Exception as e:
                self._trigger_error(f"录制过程中出错: {str(e)}")
                break

    def get_state(self) -> str:
        """
        获取当前状态

        Returns:
            str: 状态字符串
        """
        return self.state

    def is_recording(self) -> bool:
        """
        判断是否正在录制（包括暂停状态）

        Returns:
            bool: 是否正在录制
        """
        return self.state in (RecorderState.RECORDING, RecorderState.PAUSED)

    def get_stats(self) -> Dict:
        """
        获取录制统计信息

        Returns:
            Dict: 包含以下键的字典:
                - state: 当前状态
                - frame_count: 已录制帧数
                - duration: 录制时长（秒）
                - actual_fps: 实际帧率
                - output_path: 输出文件路径
        """
        duration = 0.0
        if self._start_time and self.state == RecorderState.RECORDING:
            duration = time.time() - self._start_time

        return {
            'state': self.state,
            'frame_count': self._frame_count,
            'duration': duration,
            'actual_fps': self._actual_fps,
            'output_path': self.output_path
        }

    def _trigger_error(self, message: str):
        """触发错误回调"""
        if self.on_error:
            self.on_error(message)

    def cleanup(self):
        """清理资源"""
        if self.state != RecorderState.IDLE:
            self.stop_recording()

    def __del__(self):
        """析构函数"""
        self.cleanup()
