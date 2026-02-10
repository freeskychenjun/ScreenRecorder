"""主窗口 - 应用程序主界面"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QMenuBar, QMenu, QAction, QStatusBar, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox, QSplitter,
                             QLabel, QPushButton, QFrame, QGroupBox, QFormLayout,
                             QComboBox, QSpinBox, QSlider, QFileDialog, QSystemTrayIcon)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QEvent
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import os

from gui.controls import ControlPanel
from gui.region_selector import RegionSelector
from core.recorder import Recorder, RecorderState


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        """初始化主窗口"""
        super().__init__()

        # 录制器
        self.recorder = Recorder()
        # 设置回调函数（直接赋值，不使用connect）
        self.recorder.on_frame_captured = self._on_frame_captured
        self.recorder.on_recording_started = self._on_recording_started
        self.recorder.on_recording_stopped = self._on_recording_stopped
        self.recorder.on_error = self._on_recording_error

        # 录制区域
        self.record_region: Optional[Dict] = None

        # 录制历史
        self.recording_history: List[Dict] = []

        # 定时器（用于更新统计信息）
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self._update_stats)

        # 关闭标志（用于区分关闭窗口和退出程序）
        self._is_closing = False

        # UI初始化
        self._init_ui()
        self._create_menu_bar()
        self._create_status_bar()

        # 初始化系统托盘
        self._init_system_tray()

        # 确保输出目录存在
        self._ensure_output_directory()

    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("屏幕录制软件")
        self.setMinimumSize(900, 600)

        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)

        # 左侧控制面板
        self.control_panel = ControlPanel()
        self.control_panel.start_clicked.connect(self._start_recording)
        self.control_panel.pause_clicked.connect(self._pause_recording)
        self.control_panel.stop_clicked.connect(self._stop_recording)
        self.control_panel.region_select_clicked.connect(self._show_region_selector)
        self.control_panel.setMinimumWidth(300)
        self.control_panel.setMaximumWidth(400)

        # 右侧录制历史
        history_widget = self._create_history_widget()

        splitter.addWidget(self.control_panel)
        splitter.addWidget(history_widget)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)

    def _create_history_widget(self) -> QWidget:
        """创建录制历史部件"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # 标题
        title = QLabel("录制历史")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        layout.addWidget(title)

        # 历史表格
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(
            ["文件名", "分辨率", "时长", "帧数", "大小"]
        )

        # 设置列宽
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        # 设置表格样式
        self.history_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #cccccc;
                border-radius: 5px;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #cccccc;
            }
        """)

        # 设置右键菜单
        self.history_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_table.customContextMenuRequested.connect(
            self._show_history_context_menu
        )

        layout.addWidget(self.history_table)

        # 按钮布局
        button_layout = QHBoxLayout()

        refresh_button = QPushButton("刷新")
        refresh_button.clicked.connect(self._refresh_history)
        button_layout.addWidget(refresh_button)

        button_layout.addStretch()

        open_folder_button = QPushButton("打开文件夹")
        open_folder_button.clicked.connect(self._open_output_folder)
        button_layout.addWidget(open_folder_button)

        layout.addLayout(button_layout)
        widget.setLayout(layout)

        return widget

    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件")

        open_folder_action = QAction("打开输出文件夹", self)
        open_folder_action.setShortcut("Ctrl+O")
        open_folder_action.triggered.connect(self._open_output_folder)
        file_menu.addAction(open_folder_action)

        file_menu.addSeparator()

        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 设置菜单
        settings_menu = menubar.addMenu("设置")

        clear_history_action = QAction("清空历史记录", self)
        clear_history_action.triggered.connect(self._clear_history)
        settings_menu.addAction(clear_history_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助")

        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

    def _ensure_output_directory(self):
        """确保输出目录存在"""
        settings = self.control_panel.get_settings()
        output_dir = Path(settings['output_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)

    def _create_tray_icon(self):
        """创建系统托盘图标"""
        # 创建一个32x32的图标
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制圆形背景
        painter.setBrush(QColor("#2196F3"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(2, 2, 28, 28)

        # 绘制录制符号（红色圆点）
        painter.setBrush(QColor("#F44336"))
        painter.drawEllipse(12, 12, 8, 8)

        painter.end()

        return QIcon(pixmap)

    def _init_system_tray(self):
        """初始化系统托盘"""
        # 创建托盘图标（使用应用程序样式图标）
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self._create_tray_icon())

        # 创建托盘菜单
        tray_menu = QMenu()

        # 显示/隐藏窗口
        self.show_action = tray_menu.addAction("显示窗口")
        self.show_action.triggered.connect(self._show_window)

        # 开始/停止录制
        self.record_action = tray_menu.addAction("开始录制")
        self.record_action.triggered.connect(self._toggle_recording)

        # 暂停/恢复录制
        self.pause_action = tray_menu.addAction("暂停录制")
        self.pause_action.triggered.connect(self._toggle_pause)
        self.pause_action.setEnabled(False)  # 初始禁用

        tray_menu.addSeparator()

        # 打开输出文件夹
        open_folder_action = tray_menu.addAction("打开输出文件夹")
        open_folder_action.triggered.connect(self._open_output_folder)

        tray_menu.addSeparator()

        # 退出
        exit_action = tray_menu.addAction("退出")
        exit_action.triggered.connect(self._really_close)

        self.tray_icon.setContextMenu(tray_menu)

        # 双击托盘图标显示窗口
        self.tray_icon.activated.connect(self._on_tray_activated)

        # 显示托盘图标
        self.tray_icon.show()

        # 设置托盘提示
        self.tray_icon.setToolTip("屏幕录制软件")

        # 更新托盘状态
        self._update_tray_state()

    def _show_window(self):
        """显示主窗口"""
        self.show()
        self.raise_()
        self.activateWindow()

    def _toggle_recording(self):
        """切换录制状态（托盘菜单用）"""
        is_recording = self.recorder.is_recording()

        if is_recording:
            # 如果正在录制，先暂停再询问是否停止
            was_recording = self.recorder.get_state() == RecorderState.RECORDING
            if was_recording:
                self.recorder.pause_recording()

            # 询问是否停止
            reply = QMessageBox.question(
                self,
                "停止录制",
                "确定要停止当前录制吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # 确认停止
                self._stop_recording()
            else:
                # 取消停止，恢复录制
                if was_recording:
                    self.recorder.resume_recording()
        else:
            # 如果未录制，开始录制
            self._start_recording()
            # 隐藏窗口
            self.hide()

    def _toggle_pause(self):
        """切换暂停/恢复录制（托盘菜单用）"""
        state = self.recorder.get_state()

        if state == RecorderState.RECORDING:
            # 暂停录制
            self.recorder.pause_recording()
            self.control_panel.set_recording_state('paused')
            self.status_bar.showMessage("录制已暂停")
        elif state == RecorderState.PAUSED:
            # 恢复录制
            self.recorder.resume_recording()
            self.control_panel.set_recording_state('recording')
            self.status_bar.showMessage("录制继续...")

        # 更新托盘状态
        self._update_tray_state()

    def _on_tray_activated(self, reason):
        """托盘图标被激活（双击或单击）"""
        if reason == QSystemTrayIcon.DoubleClick:
            # 双击显示/隐藏窗口
            if self.isVisible():
                self.hide()
            else:
                self._show_window()

    def _update_tray_state(self):
        """更新托盘图标状态"""
        state = self.recorder.get_state()

        if state == RecorderState.IDLE:
            # 未录制
            self.record_action.setText("开始录制")
            self.pause_action.setEnabled(False)
            self.pause_action.setText("暂停录制")
            self.tray_icon.setToolTip("屏幕录制软件")
        elif state == RecorderState.RECORDING:
            # 录制中
            self.record_action.setText("停止录制")
            self.pause_action.setEnabled(True)
            self.pause_action.setText("暂停录制")
            self.tray_icon.setToolTip("屏幕录制软件 - 录制中")
        elif state == RecorderState.PAUSED:
            # 已暂停
            self.record_action.setText("停止录制")
            self.pause_action.setEnabled(True)
            self.pause_action.setText("恢复录制")
            self.tray_icon.setToolTip("屏幕录制软件 - 已暂停")

    def _really_close(self):
        """真正关闭程序"""
        self._is_closing = True
        self.close()

    def changeEvent(self, event):
        """窗口状态改变事件"""
        if event.type() == QEvent.WindowStateChange:
            if self.isMinimized():
                # 最小化时隐藏到托盘
                event.ignore()
                self.hide()
        super().changeEvent(event)

    def _show_region_selector(self):
        """显示区域选择器"""
        # 传入 None 作为 parent，确保它是独立的顶级窗口
        self.region_selector = RegionSelector(None)
        self.region_selector.region_selected.connect(self._on_region_selected)
        # 连接关闭信号以重新显示主窗口
        self.region_selector.window_closed.connect(self.show)
        
        # 隐藏主窗口并显示选择器
        self.hide()
        self.region_selector.show()

    def _on_region_selected(self, region: Dict):
        """
        区域选择完成事件

        Args:
            region: 选中的区域字典
        """
        self.record_region = region
        self.control_panel.set_region(region)
        self.status_bar.showMessage(f"已选择录制区域: {region['width']}x{region['height']}")

    def _start_recording(self):
        """开始录制"""
        # 生成输出文件名
        settings = self.control_panel.get_settings()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.mp4"
        output_path = str(Path(settings['output_dir']) / filename)

        # 开始录制（添加音频参数）
        success = self.recorder.start_recording(
            output_path=output_path,
            fps=settings['fps'],
            region=self.record_region,
            codec=settings['codec'],
            enable_audio=settings.get('enable_audio', False),
            audio_source=settings.get('audio_source', 'both'),
            audio_device=settings.get('audio_device')
        )

        if success:
            self.control_panel.set_recording_state('recording')
            self.stats_timer.start(100)  # 每100ms更新一次统计
            self.status_bar.showMessage("录制已开始...")
            # 隐藏主窗口
            self.hide()
            # 更新托盘状态
            self._update_tray_state()

    def _pause_recording(self):
        """暂停/继续录制"""
        state = self.recorder.get_state()

        if state == RecorderState.RECORDING:
            self.recorder.pause_recording()
            self.control_panel.set_recording_state('paused')
            self.status_bar.showMessage("录制已暂停")
            self._update_tray_state()
        elif state == RecorderState.PAUSED:
            self.recorder.resume_recording()
            self.control_panel.set_recording_state('recording')
            self.status_bar.showMessage("录制继续...")
            self._update_tray_state()

    def _stop_recording(self):
        """停止录制"""
        self.stats_timer.stop()
        self.recorder.stop_recording()
        self.control_panel.set_recording_state('idle')
        self.status_bar.showMessage("录制已停止")
        self._update_tray_state()

    def _on_recording_started(self):
        """录制开始回调"""
        pass

    def _on_recording_stopped(self, output_path: str, frame_count: int, duration: float):
        """
        录制停止回调

        Args:
            output_path: 输出文件路径
            frame_count: 帧数
            duration: 时长
        """
        # 停止统计定时器
        self.stats_timer.stop()

        # 更新控制面板状态
        self.control_panel.set_recording_state('idle')

        # 更新托盘状态
        self._update_tray_state()

        # 显示主窗口
        self._show_window()

        # 添加到历史记录
        self._add_to_history(output_path, frame_count, duration)

        # 刷新历史表格
        self._refresh_history()

        # 显示完成消息
        file_size = self._get_file_size(output_path)
        self.status_bar.showMessage(
            f"录制完成: {Path(output_path).name} | "
            f"{frame_count}帧 | {self._format_duration(duration)} | {file_size:.1f}MB"
        )

        # 显示托盘通知
        self.tray_icon.showMessage(
            "录制完成",
            f"已保存 {frame_count} 帧视频\n时长: {duration:.1f}秒",
            QSystemTrayIcon.Information,
            3000
        )

        QMessageBox.information(
            self,
            "录制完成",
            f"视频已保存到:\n{output_path}\n\n"
            f"帧数: {frame_count}\n"
            f"时长: {self._format_duration(duration)}\n"
            f"大小: {file_size:.1f}MB"
        )

    def _on_frame_captured(self, frame):
        """帧捕获回调（可用于预览）"""
        pass

    def _on_recording_error(self, error_message: str):
        """
        录制错误回调

        Args:
            error_message: 错误消息
        """
        QMessageBox.critical(self, "录制错误", error_message)
        self.status_bar.showMessage(f"错误: {error_message}")

    def _update_stats(self):
        """更新统计信息"""
        stats = self.recorder.get_stats()
        self.control_panel.update_stats(
            stats['frame_count'],
            stats['duration'],
            stats['actual_fps']
        )

    def _add_to_history(self, output_path: str, frame_count: int, duration: float):
        """
        添加到历史记录

        Args:
            output_path: 输出文件路径
            frame_count: 帧数
            duration: 时长
        """
        file_path = Path(output_path)

        # 获取视频分辨率（简化处理，实际应该读取视频文件）
        resolution = "未知"

        record = {
            'filename': file_path.name,
            'path': str(file_path),
            'resolution': resolution,
            'duration': duration,
            'frame_count': frame_count,
            'size': self._get_file_size(output_path),
            'timestamp': datetime.now()
        }

        self.recording_history.insert(0, record)

    def _refresh_history(self):
        """刷新历史表格"""
        # 清空表格
        self.history_table.setRowCount(0)

        # 重新扫描输出目录
        settings = self.control_panel.get_settings()
        output_dir = Path(settings['output_dir'])

        if output_dir.exists():
            for file_path in sorted(output_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True):
                row = self.history_table.rowCount()
                self.history_table.insertRow(row)

                self.history_table.setItem(row, 0, QTableWidgetItem(file_path.name))
                self.history_table.setItem(row, 1, QTableWidgetItem("未知"))
                self.history_table.setItem(row, 2, QTableWidgetItem("00:00"))
                self.history_table.setItem(row, 3, QTableWidgetItem("0"))
                self.history_table.setItem(row, 4, QTableWidgetItem(f"{self._get_file_size(str(file_path)):.1f}MB"))

    def _show_history_context_menu(self, pos):
        """显示历史表格右键菜单"""
        from PyQt5.QtWidgets import QMenu

        item = self.history_table.itemAt(pos)
        if not item:
            return

        row = item.row()
        filename = self.history_table.item(row, 0).text()

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #cccccc;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #2196F3;
            }
        """)

        open_action = QAction("打开", menu)
        open_action.triggered.connect(lambda: self._open_video_file(filename))
        menu.addAction(open_action)

        delete_action = QAction("删除", menu)
        delete_action.triggered.connect(lambda: self._delete_video_file(filename, row))
        menu.addAction(delete_action)

        menu.exec_(self.history_table.mapToGlobal(pos))

    def _open_video_file(self, filename: str):
        """打开视频文件"""
        settings = self.control_panel.get_settings()
        file_path = Path(settings['output_dir']) / filename

        if file_path.exists():
            os.startfile(str(file_path))

    def _delete_video_file(self, filename: str, row: int):
        """删除视频文件"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除 {filename} 吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            settings = self.control_panel.get_settings()
            file_path = Path(settings['output_dir']) / filename

            if file_path.exists():
                file_path.unlink()
                self.history_table.removeRow(row)
                self.status_bar.showMessage(f"已删除: {filename}")

    def _open_output_folder(self):
        """打开输出文件夹"""
        settings = self.control_panel.get_settings()
        output_dir = Path(settings['output_dir'])

        if output_dir.exists():
            os.startfile(str(output_dir))

    def _clear_history(self):
        """清空历史记录"""
        reply = QMessageBox.question(
            self,
            "确认清空",
            "确定要清空历史记录吗？\n（不会删除文件）",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.recording_history.clear()
            self.history_table.setRowCount(0)
            self.status_bar.showMessage("历史记录已清空")

    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于屏幕录制软件",
            "<h3>屏幕录制软件</h3>"
            "<p>版本: 1.0.0</p>"
            "<p>一款基于Python的Windows屏幕录制工具</p>"
            "<p><b>功能特性:</b></p>"
            "<ul>"
            "<li>全屏/区域录制</li>"
            "<li>暂停/继续录制</li>"
            "<li>多种编码格式支持</li>"
            "<li>录制历史管理</li>"
            "</ul>"
        )

    def _get_file_size(self, file_path: str) -> float:
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

    def _format_duration(self, seconds: float) -> str:
        """
        格式化时长

        Args:
            seconds: 秒数

        Returns:
            str: 格式化的时长 (MM:SS)
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def closeEvent(self, event):
        """窗口关闭事件"""
        # 如果正在录制，询问用户
        if self.recorder.get_state() != RecorderState.IDLE:
            reply = QMessageBox.question(
                self,
                "确认退出",
                "正在录制中，确定要退出吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.recorder.stop_recording()
                self.tray_icon.hide()
                event.accept()
            else:
                event.ignore()
        else:
            # 如果不是真的退出（只是关闭窗口），隐藏到托盘
            if not self._is_closing:
                event.ignore()
                self.hide()
                # 显示托盘提示
                self.tray_icon.showMessage(
                    "屏幕录制软件",
                    "程序已最小化到系统托盘",
                    QSystemTrayIcon.Information,
                    2000
                )
            else:
                self.tray_icon.hide()
                event.accept()
