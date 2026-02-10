"""悬浮控制球 - 录制时的快速控制界面"""

from PyQt5.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QVBoxLayout,
                             QApplication, QFrame)
from PyQt5.QtCore import Qt, QPoint, QTimer, pyqtSignal, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QRadialGradient
from typing import Optional
import math


class FloatingControlBall(QWidget):
    """悬浮控制球窗口"""

    # 信号定义
    pause_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    ball_hidden = pyqtSignal()

    # 配置
    BALL_SIZE = 60  # 球体直径（收起状态）
    PANEL_WIDTH = 180  # 控制面板宽度
    PANEL_HEIGHT = 60  # 控制面板高度
    ANIMATION_SPEED = 100  # 动画刷新间隔（ms）

    def __init__(self, parent=None):
        """初始化悬浮控制球"""
        super().__init__(parent)

        # 状态
        self._is_expanded = False
        self._recording_state = 'idle'  # idle, recording, paused
        self._animation_step = 0  # 脉动动画步数
        self._pulse_direction = 1  # 脉动方向

        # 拖动相关
        self._dragging = False
        self._drag_start_pos: Optional[QPoint] = None
        self._drag_start_window_pos: Optional[QPoint] = None

        # UI初始化
        self._init_ui()

        # 动画定时器（用于脉动效果）
        self._animation_timer = QTimer()
        self._animation_timer.timeout.connect(self._update_animation)
        self._animation_timer.start(self.ANIMATION_SPEED)

        # 设置窗口大小（收起状态）
        self._update_window_size()

    def _init_ui(self):
        """初始化UI"""
        # 窗口属性（透明背景、置顶、无边框）
        self.setWindowFlags(
            Qt.Window |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)

        # 创建控制面板（展开时显示）
        self._control_panel = QFrame()
        self._control_panel.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 40, 40, 230);
                border-radius: 8px;
            }
        """)

        panel_layout = QHBoxLayout()
        panel_layout.setContentsMargins(8, 8, 8, 8)
        panel_layout.setSpacing(8)

        # 暂停/继续按钮
        self._pause_button = QPushButton()
        self._pause_button.setFixedSize(60, 45)
        self._pause_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
            QPushButton:pressed {
                background-color: #c27800;
            }
        """)
        self._pause_button.setText("⏸")
        self._pause_button.clicked.connect(self._on_pause_clicked)
        panel_layout.addWidget(self._pause_button)

        # 停止按钮
        self._stop_button = QPushButton()
        self._stop_button.setFixedSize(60, 45)
        self._stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #b9150a;
            }
        """)
        self._stop_button.setText("⏹")
        self._stop_button.clicked.connect(self._on_stop_clicked)
        panel_layout.addWidget(self._stop_button)

        panel_layout.addStretch()
        self._control_panel.setLayout(panel_layout)

        # 初始隐藏控制面板
        self._control_panel.hide()

        # 主布局
        self._main_layout = QHBoxLayout()
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        # 添加球体容器（用于点击区域）
        self._ball_container = QWidget()
        self._ball_container.setMinimumSize(self.BALL_SIZE, self.BALL_SIZE)
        self._ball_container.setMaximumSize(self.BALL_SIZE, self.BALL_SIZE)

        self._main_layout.addWidget(self._ball_container)
        self._main_layout.addWidget(self._control_panel)

        self.setLayout(self._main_layout)

        # 设置初始位置（屏幕右下角）
        self._move_to_default_position()

    def _update_window_size(self):
        """更新窗口大小"""
        if self._is_expanded:
            # 展开状态：球体 + 控制面板
            total_width = self.BALL_SIZE + self.PANEL_WIDTH + 5
            total_height = max(self.BALL_SIZE, self.PANEL_HEIGHT)
            self.setFixedSize(total_width, total_height)
            self._control_panel.show()
        else:
            # 收起状态：只有球体
            self.setFixedSize(self.BALL_SIZE, self.BALL_SIZE)
            self._control_panel.hide()

    def _move_to_default_position(self):
        """移动到默认位置（屏幕右下角）"""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            x = screen_geometry.right() - self.BALL_SIZE - 50
            y = screen_geometry.bottom() - self.BALL_SIZE - 50
            self.move(x, y)

    def _constrain_to_screen(self, pos: QPoint) -> QPoint:
        """
        限制位置在屏幕范围内

        Args:
            pos: 目标位置

        Returns:
            QPoint: 调整后的位置
        """
        screen = QApplication.primaryScreen()
        if not screen:
            return pos

        screen_geometry = screen.geometry()
        x, y = pos.x(), pos.y()

        # 获取窗口大小
        if self._is_expanded:
            window_width = self.BALL_SIZE + self.PANEL_WIDTH + 5
        else:
            window_width = self.BALL_SIZE

        window_height = self.height()

        # 限制在屏幕范围内
        x = max(screen_geometry.left(), min(x, screen_geometry.right() - window_width))
        y = max(screen_geometry.top(), min(y, screen_geometry.bottom() - window_height))

        return QPoint(x, y)

    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制球体
        self._draw_ball(painter)

    def _draw_ball(self, painter: QPainter):
        """
        绘制控制球

        Args:
            painter: QPainter对象
        """
        # 计算脉动效果
        pulse_scale = 0
        if self._recording_state == 'recording':
            # 录制时脉动
            pulse_scale = self._animation_step * 0.3
        elif self._recording_state == 'paused':
            # 暂停时静态缩放
            pulse_scale = 0.1

        # 球体半径（包括脉动）
        radius = (self.BALL_SIZE // 2) - 5 + pulse_scale
        center = QPoint(self.BALL_SIZE // 2, self.BALL_SIZE // 2)

        # 绘制半透明圆形背景
        if self._recording_state == 'recording':
            # 录制中：深红色渐变
            gradient = QRadialGradient(center, radius)
            gradient.setColorAt(0, QColor(60, 20, 20, 230))
            gradient.setColorAt(1, QColor(40, 10, 10, 230))
            painter.setBrush(QBrush(gradient))
        elif self._recording_state == 'paused':
            # 暂停中：深橙色渐变
            gradient = QRadialGradient(center, radius)
            gradient.setColorAt(0, QColor(60, 40, 20, 230))
            gradient.setColorAt(1, QColor(40, 30, 10, 230))
            painter.setBrush(QBrush(gradient))
        else:
            # 空闲：深蓝色渐变
            gradient = QRadialGradient(center, radius)
            gradient.setColorAt(0, QColor(33, 150, 243, 230))
            gradient.setColorAt(1, QColor(13, 71, 161, 230))
            painter.setBrush(QBrush(gradient))

        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, radius, radius)

        # 绘制状态图标
        painter.setPen(QPen(Qt.white, 3))
        painter.setFont(QFont("Arial", 16, QFont.Bold))

        if self._recording_state == 'recording':
            # 绘制录制圆点
            icon_radius = 8
            painter.setBrush(QBrush(QColor(244, 67, 54)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(center, icon_radius, icon_radius)
        elif self._recording_state == 'paused':
            # 绘制暂停符号
            bar_width = 4
            bar_height = 14
            x_offset = center.x() - bar_width - 2

            painter.setBrush(QBrush(QColor(255, 152, 0)))
            painter.setPen(Qt.NoPen)

            # 左竖线
            painter.drawRect(QRect(
                x_offset,
                center.y() - bar_height // 2,
                bar_width,
                bar_height
            ))

            # 右竖线
            painter.drawRect(QRect(
                x_offset + bar_width + 4,
                center.y() - bar_height // 2,
                bar_width,
                bar_height
            ))
        else:
            # 空闲状态：绘制圆圈
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(QColor(255, 255, 255, 180), 3))
            painter.drawEllipse(center, 10, 10)

    def _update_animation(self):
        """更新动画状态"""
        if self._recording_state == 'recording':
            # 脉动动画
            self._animation_step += self._pulse_direction * 2

            if self._animation_step >= 10:
                self._pulse_direction = -1
            elif self._animation_step <= 0:
                self._pulse_direction = 1

            self.update()  # 触发重绘
        elif self._recording_state == 'paused':
            # 暂停时不需要动画，只更新一次
            if self._animation_step != 5:
                self._animation_step = 5
                self.update()

    def _on_pause_clicked(self):
        """暂停按钮点击事件"""
        self.pause_clicked.emit()
        # 收起面板
        self.collapse()

    def _on_stop_clicked(self):
        """停止按钮点击事件"""
        self.stop_clicked.emit()
        # 停止后不需要收起，主窗口会显示

    def mousePressEvent(self, event):
        """鼠标按下事件（处理拖动和点击）"""
        if event.button() == Qt.LeftButton and self._is_on_ball(event.pos()):
            self._dragging = True
            self._drag_start_pos = event.globalPos()
            self._drag_start_window_pos = self.pos()
            self._click_start_pos = event.pos()  # 记录点击起始位置
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """鼠标移动事件（拖动）"""
        if self._dragging and self._drag_start_pos and self._drag_start_window_pos:
            # 计算新位置
            delta = event.globalPos() - self._drag_start_pos
            new_pos = self._drag_start_window_pos + delta

            # 限制在屏幕范围内
            new_pos = self._constrain_to_screen(new_pos)

            # 移动窗口
            self.move(new_pos)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件（处理点击展开/收起）"""
        if event.button() == Qt.LeftButton and self._is_on_ball(event.pos()):
            # 检查是否是点击（移动距离小于5像素）
            if hasattr(self, '_click_start_pos'):
                move_distance = (event.pos() - self._click_start_pos).manhattanLength()
                if move_distance < 5:
                    # 视为点击，切换展开/收起状态
                    if self._is_expanded:
                        self.collapse()
                    else:
                        self.expand()

            self._dragging = False
            self._drag_start_pos = None
            self._drag_start_window_pos = None
            if hasattr(self, '_click_start_pos'):
                delattr(self, '_click_start_pos')
        else:
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件"""
        if event.button() == Qt.LeftButton and self._is_on_ball(event.pos()):
            # 双击隐藏
            self.hide()
            self.ball_hidden.emit()

    def _is_on_ball(self, pos: QPoint) -> bool:
        """
        检查位置是否在球体区域内

        Args:
            pos: 位置坐标

        Returns:
            bool: 是否在球体内
        """
        center_x = self.BALL_SIZE // 2
        center_y = self.BALL_SIZE // 2
        radius = self.BALL_SIZE // 2

        dx = pos.x() - center_x
        dy = pos.y() - center_y

        return (dx * dx + dy * dy) <= (radius * radius)

    def keyPressEvent(self, event):
        """键盘事件"""
        if event.key() == Qt.Key_Escape:
            # ESC键收起面板
            self.collapse()

    def expand(self):
        """展开控制面板"""
        if not self._is_expanded:
            self._is_expanded = True
            self._update_window_size()
            # 重新定位，确保面板在屏幕内
            current_pos = self.pos()
            new_pos = self._constrain_to_screen(current_pos)
            if new_pos != current_pos:
                self.move(new_pos)

    def collapse(self):
        """收起控制面板"""
        if self._is_expanded:
            self._is_expanded = False
            self._update_window_size()

    def set_recording_state(self, state: str):
        """
        设置录制状态

        Args:
            state: 状态字符串 (idle, recording, paused)
        """
        self._recording_state = state

        # 更新暂停按钮显示
        if state == 'paused':
            self._pause_button.setText("▶")
        else:
            self._pause_button.setText("⏸")

        # 触发更新
        self.update()

    def show_ball(self):
        """显示悬浮球"""
        self.show()
        self.raise_()
        self.activateWindow()

    def hide_ball(self):
        """隐藏悬浮球"""
        self.hide()

    def cleanup(self):
        """清理资源"""
        self._animation_timer.stop()
