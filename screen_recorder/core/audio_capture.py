"""音频捕获模块 - 支持麦克风和系统音频录制"""

# 使用 pyaudiowpatch - Windows 兼容版本，支持 WASAPI Loopback
try:
    import pyaudiowpatch as pyaudio
except ImportError:
    import pyaudio

import wave
import threading
import numpy as np
from typing import Optional, List


class AudioCapture:
    """音频捕获类 - 支持麦克风和系统音频"""

    SOURCE_MIC = "mic"
    SOURCE_SYSTEM = "system"
    SOURCE_BOTH = "both"

    def __init__(self, sample_rate=44100, channels=2, chunk_size=1024):
        """
        初始化音频捕获

        Args:
            sample_rate: 采样率 (默认44100Hz)
            channels: 声道数 (默认2-立体声)
            chunk_size: 每次读取的样本数
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.format = pyaudio.paInt16

        self.pyaudio = pyaudio.PyAudio()
        self.mic_stream = None
        self.system_stream = None
        self.frames = []
        self.is_recording = False

    def get_audio_devices(self) -> List[dict]:
        """
        获取可用音频设备列表

        Returns:
            List[dict]: 设备列表，每个设备包含index, name, is_loopback
        """
        devices = []
        try:
            for i in range(self.pyaudio.get_device_count()):
                info = self.pyaudio.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    devices.append({
                        'index': i,
                        'name': info['name'],
                        'is_loopback': 'Loopback' in info['name'] or 'WASAPI' in info['name']
                    })
        except Exception as e:
            print(f"获取音频设备失败: {e}")
        return devices

    def start_recording(self, source='both', mic_device_index=None):
        """
        开始音频录制

        Args:
            source: 音频源 ('mic', 'system', 'both')
            mic_device_index: 麦克风设备索引，None表示使用默认设备
        """
        self.is_recording = True
        self.frames = []

        try:
            # 麦克风录制
            if source in ['mic', 'both']:
                if mic_device_index is None:
                    try:
                        mic_device_index = self.pyaudio.get_default_input_device_info()['index']
                    except:
                        mic_device_index = 0

                self.mic_stream = self.pyaudio.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.sample_rate,
                    input=True,
                    input_device_index=mic_device_index,
                    frames_per_buffer=self.chunk_size
                )

            # 系统音频录制（WASAPI Loopback）
            if source in ['system', 'both']:
                loopback_device = self._find_loopback_device()
                if loopback_device is not None:
                    try:
                        self.system_stream = self.pyaudio.open(
                            format=self.format,
                            channels=2,
                            rate=self.sample_rate,
                            input=True,
                            input_device_index=loopback_device,
                            frames_per_buffer=self.chunk_size
                        )
                    except Exception as e:
                        print(f"无法打开系统音频设备: {e}")

            # 启动录制线程
            if self.mic_stream or self.system_stream:
                threading.Thread(target=self._record_loop, daemon=True).start()

        except Exception as e:
            print(f"启动音频录制失败: {e}")
            self.is_recording = False

    def _record_loop(self):
        """录制循环（在独立线程中运行）"""
        while self.is_recording:
            try:
                mic_data = None
                system_data = None

                # 读取麦克风数据
                if self.mic_stream:
                    try:
                        mic_data = self.mic_stream.read(self.chunk_size, exception_on_overflow=False)
                    except Exception as e:
                        print(f"读取麦克风数据失败: {e}")

                # 读取系统音频数据
                if self.system_stream:
                    try:
                        system_data = self.system_stream.read(self.chunk_size, exception_on_overflow=False)
                    except Exception as e:
                        print(f"读取系统音频数据失败: {e}")

                # 混合音频
                if mic_data and system_data:
                    mixed = self._mix_audio(mic_data, system_data)
                    self.frames.append(mixed)
                elif mic_data:
                    self.frames.append(mic_data)
                elif system_data:
                    self.frames.append(system_data)

            except Exception as e:
                print(f"音频录制循环错误: {e}")
                break

    def _mix_audio(self, audio1: bytes, audio2: bytes) -> bytes:
        """
        混合两个音频流

        Args:
            audio1: 第一个音频流
            audio2: 第二个音频流

        Returns:
            bytes: 混合后的音频
        """
        try:
            arr1 = np.frombuffer(audio1, dtype=np.int16)
            arr2 = np.frombuffer(audio2, dtype=np.int16)

            # 确保长度相同
            if len(arr1) < len(arr2):
                arr1 = np.pad(arr1, (0, len(arr2) - len(arr1)))
            elif len(arr2) < len(arr1):
                arr2 = np.pad(arr2, (0, len(arr1) - len(arr2)))

            # 混合并防止溢出
            mixed = np.clip(arr1.astype(np.int32) + arr2.astype(np.int32), -32768, 32767).astype(np.int16)
            return mixed.tobytes()
        except Exception as e:
            print(f"音频混合失败: {e}")
            return audio1  # 失败时返回第一个音频

    def stop_recording(self):
        """停止录制"""
        self.is_recording = False

        if self.mic_stream:
            try:
                self.mic_stream.stop_stream()
                self.mic_stream.close()
            except:
                pass
            self.mic_stream = None

        if self.system_stream:
            try:
                self.system_stream.stop_stream()
                self.system_stream.close()
            except:
                pass
            self.system_stream = None

    def save_to_file(self, filepath: str) -> bool:
        """
        保存音频到WAV文件

        Args:
            filepath: 输出文件路径

        Returns:
            bool: 是否成功保存
        """
        if not self.frames:
            print("没有音频数据可保存")
            return False

        try:
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.pyaudio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(self.frames))
            return True
        except Exception as e:
            print(f"保存音频文件失败: {e}")
            return False

    def _find_loopback_device(self) -> Optional[int]:
        """
        查找系统音频Loopback设备

        Returns:
            Optional[int]: 设备索引，未找到返回None
        """
        try:
            for i in range(self.pyaudio.get_device_count()):
                info = self.pyaudio.get_device_info_by_index(i)
                name = info['name'].lower()
                if any(keyword in name for keyword in ['loopback', 'wasapi', 'stereo mix', '立体声混音']):
                    return i
        except Exception as e:
            print(f"查找Loopback设备失败: {e}")
        return None

    def cleanup(self):
        """清理资源"""
        self.is_recording = False
        if self.mic_stream:
            try:
                self.mic_stream.close()
            except:
                pass
        if self.system_stream:
            try:
                self.system_stream.close()
            except:
                pass
        if self.pyaudio:
            try:
                self.pyaudio.terminate()
            except:
                pass
