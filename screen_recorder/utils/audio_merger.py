"""音视频合并工具 - 使用FFmpeg合并音频和视频"""

import subprocess
import os
from typing import Optional


def merge_audio_video(video_path: str, audio_path: str, output_path: str, video_fps: float = None) -> bool:
    """
    使用FFmpeg合并音视频

    Args:
        video_path: 视频文件路径
        audio_path: 音频文件路径
        output_path: 输出文件路径
        video_fps: 视频实际帧率（可选），用于修正视频时间戳

    Returns:
        bool: 是否成功合并
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(video_path):
            print(f"视频文件不存在: {video_path}")
            return False

        if not os.path.exists(audio_path):
            print(f"音频文件不存在: {audio_path}")
            return False

        # 使用ffmpeg命令行合并
        command = [
            'ffmpeg',
            '-i', video_path,
            '-i', audio_path,
        ]

        # 如果提供了实际FPS，使用它来修正视频时间戳
        if video_fps is not None and video_fps > 0:
            # 使用 -r 参数设置输入帧率，然后用 -filter:v 设置输出帧率
            command.extend([
                '-r', str(video_fps),  # 设置视频帧率
                '-c:v', 'copy',  # 不重新编码视频
            ])
        else:
            command.extend([
                '-c:v', 'copy',  # 不重新编码视频
            ])

        command.extend([
            '-c:a', 'aac',   # 音频编码为AAC
            '-strict', 'experimental',
            '-shortest',    # 以较短的流为准
            '-y',            # 覆盖输出文件
            output_path
        ])

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60  # 60秒超时
        )

        if result.returncode == 0:
            return True
        else:
            error_msg = result.stderr.decode('utf-8', errors='ignore')
            print(f"FFmpeg合并错误: {error_msg}")
            return False

    except subprocess.TimeoutExpired:
        print("FFmpeg合并超时")
        return False
    except FileNotFoundError:
        print("未找到FFmpeg，请确保已安装并添加到PATH环境变量")
        return False
    except Exception as e:
        print(f"合并失败: {e}")
        return False


def check_ffmpeg_available() -> bool:
    """
    检查FFmpeg是否可用

    Returns:
        bool: FFmpeg是否可用
    """
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_ffmpeg_path() -> Optional[str]:
    """
    获取FFmpeg可执行文件路径

    Returns:
        Optional[str]: FFmpeg路径，未找到返回None
    """
    try:
        result = subprocess.run(
            ['where', 'ffmpeg'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout:
            # 返回第一个找到的路径
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    return None


def fix_video_fps(video_path: str, output_path: str, actual_fps: float) -> bool:
    """
    修正视频帧率（不重新编码，只修改容器时间戳）

    Args:
        video_path: 原视频文件路径
        output_path: 输出文件路径
        actual_fps: 实际帧率

    Returns:
        bool: 是否成功
    """
    try:
        command = [
            'ffmpeg',
            '-i', video_path,
            '-r', str(actual_fps),  # 设置正确的帧率
            '-c', 'copy',  # 不重新编码
            '-y',
            output_path
        ]

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60
        )

        if result.returncode == 0:
            return True
        else:
            error_msg = result.stderr.decode('utf-8', errors='ignore')
            print(f"修正视频FPS失败: {error_msg}")
            return False

    except Exception as e:
        print(f"修正视频FPS异常: {e}")
        return False


def merge_with_audio_only(video_path: str, output_path: str) -> bool:
    """
    创建仅包含音频静音的视频（当音频录制失败时使用）

    Args:
        video_path: 原视频文件路径
        output_path: 输出文件路径

    Returns:
        bool: 是否成功
    """
    try:
        # 直接复制视频（不添加音频）
        command = [
            'ffmpeg',
            '-i', video_path,
            '-c', 'copy',
            '-y',
            output_path
        ]

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30
        )

        return result.returncode == 0

    except Exception as e:
        print(f"处理视频失败: {e}")
        return False
