"""实时标注工具 - 提供录制时的实时标注功能"""

import numpy as np
from typing import Tuple, List, Optional, Dict
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class AnnotationType(Enum):
    """标注类型"""
    PEN = "pen"           # 画笔
    RECTANGLE = "rectangle"  # 矩形
    CIRCLE = "circle"     # 圆形
    ARROW = "arrow"       # 箭头
    TEXT = "text"         # 文字


@dataclass
class Point:
    """点坐标"""
    x: int
    y: int


@dataclass
class ClickEffect:
    """鼠标点击效果"""
    position: Point
    timestamp: float
    color: Tuple[int, int, int] = (255, 0, 0)
    radius: int = 20
    duration: float = 0.5  # 效果持续时间（秒）


@dataclass
class Annotation:
    """标注数据"""
    type: AnnotationType
    points: List[Point]
    color: Tuple[int, int, int] = (255, 0, 0)
    thickness: int = 2
    text: Optional[str] = None
    timestamp: float = 0.0


class AnnotationTool:
    """标注工具类"""

    # 预设颜色
    COLORS = {
        '红色': (255, 0, 0),
        '绿色': (0, 255, 0),
        '蓝色': (0, 0, 255),
        '黄色': (255, 255, 0),
        '紫色': (255, 0, 255),
        '青色': (0, 255, 255),
        '白色': (255, 255, 255),
        '黑色': (0, 0, 0),
    }

    def __init__(self):
        """初始化标注工具"""
        # 当前设置
        self.current_color = (255, 0, 0)  # 默认红色
        self.current_thickness = 2
        self.current_type = AnnotationType.PEN
        self.current_text = ""

        # 标注历史
        self.annotations: List[Annotation] = []

        # 鼠标点击效果
        self.click_effects: List[ClickEffect] = []

        # 当前正在绘制的标注
        self.current_annotation: Optional[Annotation] = None

        # 是否启用标注
        self.enabled = True
        self.show_clicks = True  # 显示鼠标点击效果

    def set_color(self, color_name: str):
        """
        设置颜色

        Args:
            color_name: 颜色名称
        """
        if color_name in self.COLORS:
            self.current_color = self.COLORS[color_name]

    def set_thickness(self, thickness: int):
        """
        设置线条粗细

        Args:
            thickness: 线条粗细（1-10）
        """
        self.current_thickness = max(1, min(thickness, 10))

    def set_type(self, annotation_type: AnnotationType):
        """
        设置标注类型

        Args:
            annotation_type: 标注类型
        """
        self.current_type = annotation_type

    def set_text(self, text: str):
        """
        设置文字内容

        Args:
            text: 文字内容
        """
        self.current_text = text

    def start_annotation(self, x: int, y: int):
        """
        开始绘制标注

        Args:
            x: 起始X坐标
            y: 起始Y坐标
        """
        if not self.enabled:
            return

        self.current_annotation = Annotation(
            type=self.current_type,
            points=[Point(x, y)],
            color=self.current_color,
            thickness=self.current_thickness,
            text=self.current_text if self.current_type == AnnotationType.TEXT else None,
            timestamp=datetime.now().timestamp()
        )

    def add_point(self, x: int, y: int):
        """
        添加标注点

        Args:
            x: X坐标
            y: Y坐标
        """
        if self.current_annotation:
            self.current_annotation.points.append(Point(x, y))

    def finish_annotation(self):
        """完成标注"""
        if self.current_annotation:
            self.annotations.append(self.current_annotation)
            self.current_annotation = None

    def cancel_annotation(self):
        """取消当前标注"""
        self.current_annotation = None

    def add_click_effect(self, x: int, y: int):
        """
        添加鼠标点击效果

        Args:
            x: 点击X坐标
            y: 点击Y坐标
        """
        if not self.show_clicks:
            return

        self.click_effects.append(ClickEffect(
            position=Point(x, y),
            timestamp=datetime.now().timestamp(),
            color=self.current_color
        ))

    def apply_annotations(self, frame: np.ndarray) -> np.ndarray:
        """
        将所有标注应用到帧上

        Args:
            frame: 原始帧，RGB格式

        Returns:
            np.ndarray: 应用标注后的帧
        """
        if not self.enabled:
            return frame

        result = frame.copy()

        # 应用历史标注
        for annotation in self.annotations:
            self._draw_annotation(result, annotation)

        # 应用当前正在绘制的标注
        if self.current_annotation:
            self._draw_annotation(result, self.current_annotation)

        # 应用鼠标点击效果
        current_time = datetime.now().timestamp()
        self.click_effects = [
            effect for effect in self.click_effects
            if current_time - effect.timestamp < effect.duration
        ]

        for effect in self.click_effects:
            self._draw_click_effect(result, effect, current_time)

        return result

    def _draw_annotation(self, frame: np.ndarray, annotation: Annotation):
        """
        绘制单个标注

        Args:
            frame: 帧图像
            annotation: 标注数据
        """
        if len(annotation.points) < 1:
            return

        color = annotation.color
        thickness = annotation.thickness

        if annotation.type == AnnotationType.PEN:
            # 自由绘制
            for i in range(len(annotation.points) - 1):
                p1 = annotation.points[i]
                p2 = annotation.points[i + 1]
                self._draw_line(frame, p1, p2, color, thickness)

        elif annotation.type == AnnotationType.RECTANGLE:
            # 矩形
            if len(annotation.points) >= 2:
                p1 = annotation.points[0]
                p2 = annotation.points[-1]
                self._draw_rectangle(frame, p1, p2, color, thickness)

        elif annotation.type == AnnotationType.CIRCLE:
            # 圆形
            if len(annotation.points) >= 2:
                p1 = annotation.points[0]
                p2 = annotation.points[-1]
                self._draw_circle(frame, p1, p2, color, thickness)

        elif annotation.type == AnnotationType.ARROW:
            # 箭头
            if len(annotation.points) >= 2:
                p1 = annotation.points[0]
                p2 = annotation.points[-1]
                self._draw_arrow(frame, p1, p2, color, thickness)

        elif annotation.type == AnnotationType.TEXT:
            # 文字
            if annotation.text and annotation.points:
                p = annotation.points[0]
                self._draw_text(frame, p, annotation.text, color, thickness)

    def _draw_line(self, frame: np.ndarray, p1: Point, p2: Point,
                   color: Tuple[int, int, int], thickness: int):
        """绘制直线"""
        # 简化实现：使用Bresenham算法或直接使用OpenCV
        # 这里使用简单的插值
        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y

        distance = max(abs(x2 - x1), abs(y2 - y1))
        if distance == 0:
            return

        for i in range(distance + 1):
            t = i / distance
            x = int(x1 + (x2 - x1) * t)
            y = int(y1 + (y2 - y1) * t)

            if 0 <= y < frame.shape[0] and 0 <= x < frame.shape[1]:
                # 应用粗细
                r = thickness // 2
                for dy in range(-r, r + 1):
                    for dx in range(-r, r + 1):
                        nx, ny = x + dx, y + dy
                        if 0 <= ny < frame.shape[0] and 0 <= nx < frame.shape[1]:
                            if dx * dx + dy * dy <= r * r:
                                frame[ny, nx] = color

    def _draw_rectangle(self, frame: np.ndarray, p1: Point, p2: Point,
                        color: Tuple[int, int, int], thickness: int):
        """绘制矩形"""
        x1, y1 = min(p1.x, p2.x), min(p1.y, p2.y)
        x2, y2 = max(p1.x, p2.x), max(p1.y, p2.y)

        # 绘制四条边
        self._draw_line(frame, Point(x1, y1), Point(x2, y1), color, thickness)
        self._draw_line(frame, Point(x2, y1), Point(x2, y2), color, thickness)
        self._draw_line(frame, Point(x2, y2), Point(x1, y2), color, thickness)
        self._draw_line(frame, Point(x1, y2), Point(x1, y1), color, thickness)

    def _draw_circle(self, frame: np.ndarray, p1: Point, p2: Point,
                     color: Tuple[int, int, int], thickness: int):
        """绘制圆形"""
        import math

        center_x, center_y = p1.x, p1.y
        radius = int(math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2))

        for angle in range(0, 360, 2):
            rad = math.radians(angle)
            x = int(center_x + radius * math.cos(rad))
            y = int(center_y + radius * math.sin(rad))

            if 0 <= y < frame.shape[0] and 0 <= x < frame.shape[1]:
                r = thickness // 2
                for dy in range(-r, r + 1):
                    for dx in range(-r, r + 1):
                        nx, ny = x + dx, y + dy
                        if 0 <= ny < frame.shape[0] and 0 <= nx < frame.shape[1]:
                            if dx * dx + dy * dy <= r * r:
                                frame[ny, nx] = color

    def _draw_arrow(self, frame: np.ndarray, p1: Point, p2: Point,
                    color: Tuple[int, int, int], thickness: int):
        """绘制箭头"""
        # 绘制主线
        self._draw_line(frame, p1, p2, color, thickness)

        # 绘制箭头头部
        import math
        angle = math.atan2(p2.y - p1.y, p2.x - p1.x)
        arrow_length = 15
        arrow_angle = math.pi / 6  # 30度

        # 左箭头翼
        left_x = p2.x - arrow_length * math.cos(angle - arrow_angle)
        left_y = p2.y - arrow_length * math.sin(angle - arrow_angle)
        self._draw_line(frame, p2, Point(int(left_x), int(left_y)), color, thickness)

        # 右箭头翼
        right_x = p2.x - arrow_length * math.cos(angle + arrow_angle)
        right_y = p2.y - arrow_length * math.sin(angle + arrow_angle)
        self._draw_line(frame, p2, Point(int(right_x), int(right_y)), color, thickness)

    def _draw_text(self, frame: np.ndarray, p: Point, text: str,
                   color: Tuple[int, int, int], thickness: int):
        """绘制文字（简化版）"""
        # 简化实现：只在指定位置显示一个标记
        # 实际应用中可以使用PIL或OpenCV的文本绘制功能
        for dy in range(20):
            for dx in range(len(text) * 10):
                if dx < len(text) * 10 and dy < 20:
                    nx, ny = p.x + dx, p.y + dy
                    if 0 <= ny < frame.shape[0] and 0 <= nx < frame.shape[1]:
                        frame[ny, nx] = color

    def _draw_click_effect(self, frame: np.ndarray, effect: ClickEffect, current_time: float):
        """
        绘制鼠标点击效果

        Args:
            frame: 帧图像
            effect: 点击效果数据
            current_time: 当前时间
        """
        elapsed = current_time - effect.timestamp
        if elapsed >= effect.duration:
            return

        # 计算动画进度
        progress = elapsed / effect.duration
        alpha = int(255 * (1 - progress))
        radius = int(effect.radius * (1 + progress))

        x, y = effect.position.x, effect.position.y

        # 绘制渐变圆圈
        for r in range(radius, radius - 5, -1):
            if r <= 0:
                break

            current_alpha = max(0, alpha - (radius - r) * 50)

            for angle in range(0, 360, 5):
                import math
                rad = math.radians(angle)
                px = int(x + r * math.cos(rad))
                py = int(y + r * math.sin(rad))

                if 0 <= py < frame.shape[0] and 0 <= px < frame.shape[1]:
                    # 混合颜色
                    frame[py, px] = (
                        int(frame[py, px, 0] * (1 - current_alpha / 255) + effect.color[0] * (current_alpha / 255)),
                        int(frame[py, px, 1] * (1 - current_alpha / 255) + effect.color[1] * (current_alpha / 255)),
                        int(frame[py, px, 2] * (1 - current_alpha / 255) + effect.color[2] * (current_alpha / 255))
                    )

    def clear_annotations(self):
        """清空所有标注"""
        self.annotations.clear()
        self.click_effects.clear()
        self.current_annotation = None

    def undo_last_annotation(self):
        """撤销最后一个标注"""
        if self.annotations:
            self.annotations.pop()

    def get_annotation_count(self) -> int:
        """
        获取标注数量

        Returns:
            int: 标注数量
        """
        return len(self.annotations)
