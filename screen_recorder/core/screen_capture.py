"""屏幕捕获模块 - 使用mss库实现高性能屏幕捕获"""

import mss
import numpy as np
from typing import Optional, Dict, List, Tuple
import threading


class ScreenCapture:
    """高性能屏幕捕获类"""

    def __init__(self):
        """初始化屏幕捕获器"""
        self._monitor_cache = None
        self._lock = threading.Lock()

    def get_monitors(self) -> List[Dict]:
        """
        获取所有显示器信息

        Returns:
            List[Dict]: 显示器信息列表，每个字典包含:
                - top: 左上角Y坐标
                - left: 左上角X坐标
                - width: 宽度
                - height: 高度
        """
        with self._lock:
            # 每次创建新的mss实例来避免线程问题
            with mss.mss() as mss_instance:
                monitors = mss_instance.monitors
                # monitors[0] 是所有显示器合并的虚拟屏幕
                self._monitor_cache = monitors[1:]  # 返回物理显示器列表
                return self._monitor_cache

    def get_primary_monitor(self) -> Dict:
        """
        获取主显示器信息

        Returns:
            Dict: 主显示器信息
        """
        monitors = self.get_monitors()
        return monitors[0] if monitors else {}

    def capture_screen(self, monitor: Optional[Dict] = None) -> np.ndarray:
        """
        捕获屏幕或指定区域

        Args:
            monitor: 显示器信息字典或区域字典
                    格式: {'top': y, 'left': x, 'width': w, 'height': h}
                    如果为None，则捕获主显示器

        Returns:
            np.ndarray: 捕获的图像，RGB格式，shape为(height, width, 3)

        Raises:
            RuntimeError: 捕获失败时抛出
        """
        try:
            if monitor is None:
                monitor = self.get_primary_monitor()

            # 在每次捕获时创建新的mss实例以确保线程安全
            with mss.mss() as mss_instance:
                # mss返回BGRA格式，需要转换为RGB
                screenshot = mss_instance.grab(monitor)

                # 转换为numpy数组并转换为RGB格式
                img = np.array(screenshot)
                img = img[:, :, :3]  # 去除alpha通道
                img = np.flip(img, axis=2)  # BGR -> RGB

                return img

        except Exception as e:
            raise RuntimeError(f"屏幕捕获失败: {str(e)}")

    def capture_region(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        """
        捕获指定区域

        Args:
            x: 区域左上角X坐标
            y: 区域左上角Y坐标
            width: 区域宽度
            height: 区域高度

        Returns:
            np.ndarray: 捕获的图像，RGB格式
        """
        region = {
            'top': y,
            'left': x,
            'width': width,
            'height': height
        }
        return self.capture_screen(region)

    def get_virtual_screen_size(self) -> Tuple[int, int]:
        """
        获取虚拟屏幕（所有显示器合并）的尺寸

        Returns:
            Tuple[int, int]: (宽度, 高度)
        """
        with self._lock:
            virtual_screen = self.mss.monitors[0]
            return virtual_screen['width'], virtual_screen['height']

    def validate_region(self, x: int, y: int, width: int, height: int) -> bool:
        """
        验证区域是否有效

        Args:
            x: 区域左上角X坐标
            y: 区域左上角Y坐标
            width: 区域宽度
            height: 区域高度

        Returns:
            bool: 区域是否有效
        """
        if width <= 0 or height <= 0:
            return False

        virtual_width, virtual_height = self.get_virtual_screen_size()

        # 检查区域是否在虚拟屏幕范围内
        if x < 0 or y < 0:
            return False
        if x + width > virtual_width or y + height > virtual_height:
            return False

        return True

    def __del__(self):
        """清理资源"""
        if hasattr(self, 'mss'):
            self.mss.close()
