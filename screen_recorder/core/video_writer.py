"""视频编码模块 - 使用OpenCV进行视频编码"""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import threading


class VideoWriter:
    """视频写入器，支持H.264编码"""

    # 支持的编解码器
    CODECS = {
        'H264': 'H264',      # H.264编码，广泛支持
        'MJPG': 'MJPG',      # Motion JPEG，兼容性好
        'XVID': 'XVID',      # XVID MPEG-4
        'MP4V': 'MP4V',      # MPEG-4 Part 2
        'AVC1': 'AVC1',      # 另一种H.264实现
    }

    def __init__(self, output_path: str, fps: int, resolution: Tuple[int, int], codec: str = 'H264'):
        """
        初始化视频写入器

        Args:
            output_path: 输出文件路径
            fps: 帧率
            resolution: 分辨率 (width, height)
            codec: 编码器名称，默认H.264

        Raises:
            ValueError: 参数无效时抛出
        """
        self.output_path = Path(output_path)
        self.fps = fps
        self.width, self.height = resolution
        self.codec = codec
        self.writer: Optional[cv2.VideoWriter] = None
        self._lock = threading.Lock()
        self._frame_count = 0
        self._is_open = False

        # 验证参数
        if self.fps <= 0:
            raise ValueError(f"无效的帧率: {fps}")
        if self.width <= 0 or self.height <= 0:
            raise ValueError(f"无效的分辨率: {resolution}")

        # 确保输出目录存在
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def open(self) -> bool:
        """
        打开视频写入器

        Returns:
            bool: 是否成功打开
        """
        try:
            with self._lock:
                if self._is_open:
                    return True

                # 选择编解码器
                fourcc = self._get_fourcc(self.codec)

                # 创建VideoWriter对象
                self.writer = cv2.VideoWriter(
                    str(self.output_path),
                    fourcc,
                    self.fps,
                    (self.width, self.height)
                )

                if not self.writer.isOpened():
                    raise RuntimeError(f"无法打开视频写入器: {self.output_path}")

                self._is_open = True
                self._frame_count = 0
                return True

        except Exception as e:
            print(f"打开视频写入器失败: {e}")
            return False

    def write_frame(self, frame: np.ndarray) -> bool:
        """
        写入一帧

        Args:
            frame: 图像帧，RGB格式

        Returns:
            bool: 是否成功写入
        """
        try:
            with self._lock:
                if not self._is_open:
                    return False

                # 转换RGB到BGR (OpenCV使用BGR)
                if len(frame.shape) == 3 and frame.shape[2] == 3:
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                else:
                    frame_bgr = frame

                # 写入帧
                self.writer.write(frame_bgr)
                self._frame_count += 1
                return True

        except Exception as e:
            print(f"写入帧失败: {e}")
            return False

    def get_frame_count(self) -> int:
        """
        获取已写入的帧数

        Returns:
            int: 帧数
        """
        return self._frame_count

    def get_duration(self) -> float:
        """
        获取视频时长（秒）

        Returns:
            float: 时长
        """
        if self.fps > 0:
            return self._frame_count / self.fps
        return 0.0

    def close(self):
        """关闭视频写入器"""
        with self._lock:
            if self.writer is not None:
                self.writer.release()
                self.writer = None
            self._is_open = False

    def _get_fourcc(self, codec_name: str) -> int:
        """
        获取FourCC编解码器代码

        Args:
            codec_name: 编解码器名称

        Returns:
            int: FourCC代码
        """
        codec_upper = codec_name.upper()
        if codec_upper in self.CODECS:
            return cv2.VideoWriter_fourcc(*self.CODECS[codec_upper])
        # 默认使用H.264
        return cv2.VideoWriter_fourcc(*'H264')

    @staticmethod
    def get_supported_codecs() -> list:
        """
        获取支持的编解码器列表

        Returns:
            list: 编解码器名称列表
        """
        return list(VideoWriter.CODECS.keys())

    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """
        获取文件大小（MB）

        Args:
            file_path: 文件路径

        Returns:
            float: 文件大小（MB）
        """
        path = Path(file_path)
        if path.exists():
            return path.stat().st_size / (1024 * 1024)
        return 0.0

    def __enter__(self):
        """上下文管理器入口"""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()

    def __del__(self):
        """析构函数"""
        self.close()
