"""区域选择器 - 全屏透明覆盖窗口用于选择录制区域"""

from PyQt5.QtWidgets import (QWidget, QApplication, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QFrame, QComboBox)
from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont
from typing import Optional, Dict, Tuple


class RegionSelector(QWidget):
    """区域选择器窗口"""

    # 信号：区域选择完成
    region_selected = pyqtSignal(dict)

    # 信号：窗口关闭
    window_closed = pyqtSignal()

    # 预设分辨率
    PRESETS = {
        '全屏': None,
        '1920x1080': (1920, 1080),
        '1280x720': (1280, 720),
        '854x480': (854, 480),
        '640x360': (640, 360),
        '自定义': None
    }

    def __init__(self, parent=None):
        """
        初始化区域选择器

        Args:
            parent: 父窗口
        """
        super().__init__(parent)

        # 窗口属性
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)

        # 选择状态
        self._selecting = False
        self._start_pos: Optional[QPoint] = None
        self._current_pos: Optional[QPoint] = None
        self._selected_region: Optional[QRect] = None

        # UI初始化
        self._init_ui()

        # 全屏显示
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.geometry()
            self.setGeometry(geometry)

    def _init_ui(self):
        """初始化UI"""
        # 主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # 顶部工具栏
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # 内容区域（用于显示选择框）
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.addStretch()
        layout.addWidget(self.content_widget, 1)

        # 底部信息栏
        self.info_label = QLabel("拖动鼠标选择录制区域，或选择预设分辨率")
        self.info_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
        """)
        self.info_label.setAlignment(Qt.AlignCenter)

        info_layout = QHBoxLayout()
        info_layout.addStretch()
        info_layout.addWidget(self.info_label)
        info_layout.addStretch()

        layout.addLayout(info_layout)
        self.setLayout(layout)

    def _create_toolbar(self) -> QFrame:
        """创建工具栏"""
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 40, 40, 200);
                border-radius: 5px;
                padding: 5px;
            }
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)

        # 预设分辨率下拉框
        preset_label = QLabel("预设:")
        preset_label.setStyleSheet("color: white; font-size: 12px;")
        layout.addWidget(preset_label)

        self.preset_combo = QComboBox()
        self.preset_combo.addItems(self.PRESETS.keys())
        self.preset_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                padding: 3px;
                border-radius: 3px;
                min-width: 100px;
            }
        """)
        self.preset_combo.currentTextChanged.connect(self._on_preset_changed)
        layout.addWidget(self.preset_combo)

        layout.addStretch()

        # 确认按钮
        self.ok_button = QPushButton("确认选择")
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 5px 15px;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.ok_button.clicked.connect(self._confirm_selection)
        self.ok_button.setEnabled(False)
        layout.addWidget(self.ok_button)

        # 取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 5px 15px;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        cancel_button.clicked.connect(self.close)
        layout.addWidget(cancel_button)

        toolbar.setLayout(layout)
        return toolbar

    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制半透明背景
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))

        # 绘制选择区域
        if self._selected_region:
            # 清除选择区域的背景（使其透明）
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(self._selected_region, Qt.transparent)

            # 绘制选择框边框
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            pen = QPen(QColor(0, 255, 0), 2)
            painter.setPen(pen)
            painter.drawRect(self._selected_region)

            # 绘制尺寸标签
            self._draw_size_label(painter, self._selected_region)

        # 绘制当前拖拽区域
        elif self._selecting and self._start_pos and self._current_pos:
            rect = QRect(self._start_pos, self._current_pos).normalized()

            # 清除拖拽区域的背景
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(rect, Qt.transparent)

            # 绘制边框
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            pen = QPen(QColor(0, 255, 0), 2, Qt.DashLine)
            painter.setPen(pen)
            painter.drawRect(rect)

            # 绘制尺寸标签
            self._draw_size_label(painter, rect)

    def _draw_size_label(self, painter: QPainter, rect: QRect):
        """
        绘制尺寸标签

        Args:
            painter: QPainter对象
            rect: 区域矩形
        """
        width = rect.width()
        height = rect.height()
        text = f"{width} x {height}"

        # 计算标签位置（在矩形下方）
        label_x = rect.x() + (rect.width() - 100) // 2
        label_y = rect.bottom() + 5
        label_rect = QRect(label_x, label_y, 100, 25)

        # 绘制标签背景
        painter.setBrush(QBrush(QColor(0, 0, 0, 200)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(label_rect, 3, 3)

        # 绘制文字
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 10))
        painter.drawText(label_rect, Qt.AlignCenter, text)

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self._selecting = True
            self._start_pos = event.pos()
            self._current_pos = event.pos()
            self._selected_region = None
            self.ok_button.setEnabled(False)
            self.preset_combo.setCurrentText("自定义")
            self.update()

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self._selecting:
            self._current_pos = event.pos()
            self.update()

            # 更新信息标签
            if self._start_pos:
                rect = QRect(self._start_pos, self._current_pos).normalized()
                self.info_label.setText(
                    f"起始: ({self._start_pos.x()}, {self._start_pos.y()}) | "
                    f"尺寸: {rect.width()} x {rect.height()}"
                )

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton and self._selecting:
            self._selecting = False
            self._current_pos = event.pos()

            # 创建选择区域
            if self._start_pos:
                rect = QRect(self._start_pos, self._current_pos).normalized()

                # 确保区域有效
                if rect.width() > 10 and rect.height() > 10:
                    self._selected_region = rect
                    self.ok_button.setEnabled(True)
                    self.info_label.setText(
                        f"已选择区域: {rect.width()} x {rect.height()} | 点击'确认选择'继续"
                    )
                else:
                    self._selected_region = None
                    self.ok_button.setEnabled(False)
                    self.info_label.setText("区域太小，请重新选择")

            self.update()

    def _on_preset_changed(self, preset_name: str):
        """
        预设分辨率改变事件

        Args:
            preset_name: 预设名称
        """
        if preset_name not in self.PRESETS:
            return

        size = self.PRESETS[preset_name]

        if size is None:
            # 全屏或自定义，清除选择
            self._selected_region = None
            self.ok_button.setEnabled(preset_name == "全屏")
        else:
            # 创建居中的预设区域
            width, height = size
            center_x = self.width() // 2
            center_y = self.height() // 2

            self._selected_region = QRect(
                center_x - width // 2,
                center_y - height // 2,
                width,
                height
            )
            self.ok_button.setEnabled(True)
            self.info_label.setText(f"已选择预设: {preset_name}")

        self.update()

    def _confirm_selection(self):
        """确认选择"""
        region = None

        if self._selected_region:
            region = {
                'top': self._selected_region.top(),
                'left': self._selected_region.left(),
                'width': self._selected_region.width(),
                'height': self._selected_region.height()
            }
            self.info_label.setText(
                f"已选择: {self._selected_region.width()} x {self._selected_region.height()}"
            )
        else:
            # 全屏
            screen = QApplication.primaryScreen()
            if screen:
                geometry = screen.geometry()
                region = {
                    'top': geometry.top(),
                    'left': geometry.left(),
                    'width': geometry.width(),
                    'height': geometry.height()
                }
                self.info_label.setText("已选择: 全屏")

        if region:
            self.region_selected.emit(region)
            self.close()

    def get_selected_region(self) -> Optional[Dict]:
        """
        获取选中的区域

        Returns:
            Optional[Dict]: 区域字典，如果未选择则返回None
        """
        if self._selected_region:
            return {
                'top': self._selected_region.top(),
                'left': self._selected_region.left(),
                'width': self._selected_region.width(),
                'height': self._selected_region.height()
            }
        return None

    def keyPressEvent(self, event):
        """键盘事件"""
        if event.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        """关闭事件"""
        self.window_closed.emit()
        super().closeEvent(event)
