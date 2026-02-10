"""录制控制面板 - 提供录制控制按钮和设置"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSpinBox, QComboBox, QFileDialog, QGroupBox,
                             QFormLayout, QSlider, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from pathlib import Path
from typing import Optional


class ControlPanel(QWidget):
    """录制控制面板"""

    # 信号定义
    start_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    region_select_clicked = pyqtSignal()
    settings_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        """
        初始化控制面板

        Args:
            parent: 父窗口
        """
        super().__init__(parent)

        # 设置参数
        self.fps = 30
        self.output_dir = str(Path.home() / "Desktop" / "Recordings")
        self.codec = 'XVID'
        self.region_text = "全屏"

        # 音频设置
        self.enable_audio = False
        self.audio_source = 'both'
        self.audio_device = None

        # UI初始化
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 录制控制组
        control_group = self._create_control_group()
        main_layout.addWidget(control_group)

        # 录制设置组
        settings_group = self._create_settings_group()
        main_layout.addWidget(settings_group)

        # 状态信息组
        status_group = self._create_status_group()
        main_layout.addWidget(status_group)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def _create_control_group(self) -> QGroupBox:
        """创建录制控制组"""
        group = QGroupBox("录制控制")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        # 区域选择按钮
        self.region_button = QPushButton("📷 选择录制区域")
        self.region_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        self.region_button.clicked.connect(self.region_select_clicked.emit)
        layout.addWidget(self.region_button)

        # 当前区域显示
        self.region_label = QLabel(f"当前区域: {self.region_text}")
        self.region_label.setStyleSheet("font-size: 12px; padding: 5px;")
        layout.addWidget(self.region_label)

        # 控制按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # 开始按钮
        self.start_button = QPushButton("▶ 开始录制")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.start_button.clicked.connect(self.start_clicked.emit)
        button_layout.addWidget(self.start_button)

        # 暂停按钮
        self.pause_button = QPushButton("⏸ 暂停")
        self.pause_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.pause_button.clicked.connect(self.pause_clicked.emit)
        self.pause_button.setEnabled(False)
        button_layout.addWidget(self.pause_button)

        # 停止按钮
        self.stop_button = QPushButton("⏹ 停止")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.stop_button.clicked.connect(self.stop_clicked.emit)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)
        group.setLayout(layout)
        return group

    def _create_settings_group(self) -> QGroupBox:
        """创建录制设置组"""
        group = QGroupBox("录制设置")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QFormLayout()
        layout.setSpacing(10)

        # FPS设置
        fps_layout = QHBoxLayout()

        self.fps_slider = QSlider(Qt.Horizontal)
        self.fps_slider.setMinimum(10)
        self.fps_slider.setMaximum(60)
        self.fps_slider.setValue(self.fps)
        self.fps_slider.setTickPosition(QSlider.TicksBelow)
        self.fps_slider.setTickInterval(10)
        self.fps_slider.valueChanged.connect(self._on_fps_changed)

        self.fps_label = QLabel(f"{self.fps} FPS")
        self.fps_label.setMinimumWidth(60)

        fps_layout.addWidget(self.fps_slider, 1)
        fps_layout.addWidget(self.fps_label)

        layout.addRow("帧率:", fps_layout)

        # 编码器选择
        codec_layout = QHBoxLayout()

        self.codec_combo = QComboBox()
        self.codec_combo.addItems(['XVID', 'MJPG', 'H264', 'MP4V'])
        self.codec_combo.setCurrentText(self.codec)
        self.codec_combo.currentTextChanged.connect(self._on_codec_changed)

        codec_layout.addWidget(self.codec_combo, 1)

        # 编码器说明标签
        self.codec_info_label = QLabel()
        self.codec_info_label.setStyleSheet("font-size: 10px; color: #666;")
        self.codec_info_label.setWordWrap(True)
        self._update_codec_info(self.codec)
        codec_layout.addWidget(self.codec_info_label, 2)

        layout.addRow("编码器:", codec_layout)

        # 输出目录
        dir_layout = QHBoxLayout()

        self.dir_label = QLabel(self.output_dir)
        self.dir_label.setStyleSheet("font-size: 11px;")
        self.dir_label.setWordWrap(True)
        dir_layout.addWidget(self.dir_label, 1)

        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self._browse_output_dir)
        dir_layout.addWidget(browse_button)

        layout.addRow("输出目录:", dir_layout)

        # ========== 音频设置 ==========
        audio_group = QGroupBox("音频设置")
        audio_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        audio_layout = QVBoxLayout()
        audio_layout.setSpacing(8)

        # 音频开关
        self.audio_enable_checkbox = QCheckBox("启用音频录制")
        self.audio_enable_checkbox.setChecked(False)
        self.audio_enable_checkbox.stateChanged.connect(self._on_audio_enable_changed)
        audio_layout.addWidget(self.audio_enable_checkbox)

        # 音频源选择
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("音频源:"))
        self.audio_source_combo = QComboBox()
        self.audio_source_combo.addItems(["仅麦克风", "仅系统音频", "麦克风 + 系统音频"])
        self.audio_source_combo.setCurrentIndex(2)
        self.audio_source_combo.currentIndexChanged.connect(self._on_audio_setting_changed)
        self.audio_source_combo.setEnabled(False)
        source_layout.addWidget(self.audio_source_combo, 1)
        audio_layout.addLayout(source_layout)

        # 麦克风设备选择
        mic_layout = QHBoxLayout()
        mic_layout.addWidget(QLabel("麦克风:"))
        self.mic_device_combo = QComboBox()
        self._populate_audio_devices()
        mic_layout.addWidget(self.mic_device_combo, 1)
        audio_layout.addLayout(mic_layout)

        audio_group.setLayout(audio_layout)
        layout.addRow(audio_group)

        group.setLayout(layout)
        return group

    def _create_status_group(self) -> QGroupBox:
        """创建状态信息组"""
        group = QGroupBox("录制状态")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QFormLayout()
        layout.setSpacing(5)

        # 状态显示
        self.state_label = QLabel("空闲")
        self.state_label.setStyleSheet("""
            QLabel {
                background-color: #e0e0e0;
                padding: 5px;
                border-radius: 3px;
                font-weight: bold;
            }
        """)
        layout.addRow("状态:", self.state_label)

        # 帧数显示
        self.frames_label = QLabel("0")
        layout.addRow("已录帧数:", self.frames_label)

        # 时长显示
        self.duration_label = QLabel("00:00")
        layout.addRow("时长:", self.duration_label)

        # 实际FPS显示
        self.actual_fps_label = QLabel("0.0")
        layout.addRow("实际FPS:", self.actual_fps_label)

        group.setLayout(layout)
        return group

    def _on_fps_changed(self, value: int):
        """
        FPS滑块值改变事件

        Args:
            value: FPS值
        """
        self.fps = value
        self.fps_label.setText(f"{value} FPS")
        self._emit_settings_changed()

    def _on_codec_changed(self, codec: str):
        """
        编码器改变事件

        Args:
            codec: 编码器名称
        """
        self.codec = codec
        self._update_codec_info(codec)
        self._emit_settings_changed()

    def _update_codec_info(self, codec: str):
        """
        更新编码器说明

        Args:
            codec: 编码器名称
        """
        codec_info = {
            'XVID': '⭐ 推荐 - 兼容性好，平衡画质和文件大小',
            'MJPG': '⚡ 最快 - 适合短视频和后期编辑',
            'H264': '📦 最小 - 长时间录制，文件最小（需系统支持）',
            'MP4V': '🔧 备选 - 基础编码器'
        }
        self.codec_info_label.setText(codec_info.get(codec, ''))

    def _browse_output_dir(self):
        """浏览输出目录"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择输出目录",
            self.output_dir
        )

        if directory:
            self.output_dir = directory
            self.dir_label.setText(directory)
            self._emit_settings_changed()

    def _emit_settings_changed(self):
        """发射设置改变信号"""
        settings = {
            'fps': self.fps,
            'output_dir': self.output_dir,
            'codec': self.codec,
            'enable_audio': self.audio_enable_checkbox.isChecked(),
            'audio_source': ['mic', 'system', 'both'][self.audio_source_combo.currentIndex()],
            'audio_device': self.mic_device_combo.currentData()
        }
        self.settings_changed.emit(settings)

    def set_recording_state(self, state: str):
        """
        设置录制状态

        Args:
            state: 状态字符串 (idle, recording, paused, stopping)
        """
        # 更新状态标签
        state_text = {
            'idle': '空闲',
            'recording': '录制中',
            'paused': '已暂停',
            'stopping': '停止中'
        }.get(state, state)

        self.state_label.setText(state_text)

        # 更新按钮状态
        is_recording = state == 'recording'
        is_paused = state == 'paused'
        is_idle = state == 'idle'

        self.start_button.setEnabled(is_idle)
        self.pause_button.setEnabled(is_recording or is_paused)
        self.stop_button.setEnabled(is_recording or is_paused)
        self.region_button.setEnabled(is_idle)

        # 更新暂停按钮文本
        if is_paused:
            self.pause_button.setText("▶ 继续")
        else:
            self.pause_button.setText("⏸ 暂停")

        # 更新状态标签样式
        if state == 'recording':
            color = '#4CAF50'  # 绿色
        elif state == 'paused':
            color = '#FF9800'  # 橙色
        else:
            color = '#e0e0e0'  # 灰色

        self.state_label.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: {'white' if state != 'idle' else 'black'};
                padding: 5px;
                border-radius: 3px;
                font-weight: bold;
            }}
        """)

    def update_stats(self, frame_count: int, duration: float, fps: float):
        """
        更新统计信息

        Args:
            frame_count: 帧数
            duration: 时长（秒）
            fps: 实际FPS
        """
        self.frames_label.setText(str(frame_count))
        self.duration_label.setText(self._format_duration(duration))
        self.actual_fps_label.setText(f"{fps:.1f}")

    def set_region(self, region: Optional[dict]):
        """
        设置录制区域

        Args:
            region: 区域字典，如果为None则为全屏
        """
        if region is None:
            self.region_text = "全屏"
        else:
            width = region.get('width', 0)
            height = region.get('height', 0)
            self.region_text = f"{width} x {height}"

        self.region_label.setText(f"当前区域: {self.region_text}")

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

    def get_settings(self) -> dict:
        """
        获取当前设置

        Returns:
            dict: 设置字典
        """
        return {
            'fps': self.fps,
            'output_dir': self.output_dir,
            'codec': self.codec,
            'enable_audio': self.audio_enable_checkbox.isChecked(),
            'audio_source': ['mic', 'system', 'both'][self.audio_source_combo.currentIndex()],
            'audio_device': self.mic_device_combo.currentData()
        }

    def _populate_audio_devices(self):
        """填充音频设备列表"""
        try:
            from core.audio_capture import AudioCapture
            audio_cap = AudioCapture()
            devices = audio_cap.get_audio_devices()

            self.mic_device_combo.clear()
            self.mic_device_combo.addItem("默认设备", None)

            for device in devices:
                if not device['is_loopback']:
                    self.mic_device_combo.addItem(device['name'], device['index'])

            audio_cap.cleanup()
        except ImportError as e:
            # pyaudio 未安装，禁用音频功能
            print("音频功能不可用：未安装 pyaudio")
            self.audio_enable_checkbox.setEnabled(False)
            self.audio_enable_checkbox.setChecked(False)
            self.audio_enable_checkbox.setToolTip("需要安装 pyaudio：pip install pyaudio")
            self.mic_device_combo.clear()
            self.mic_device_combo.addItem("未安装 pyaudio", None)
            self.mic_device_combo.setEnabled(False)
        except Exception as e:
            print(f"获取音频设备失败: {e}")
            self.mic_device_combo.clear()
            self.mic_device_combo.addItem("音频设备不可用", None)
            self.mic_device_combo.setEnabled(False)

    def _on_audio_enable_changed(self, state):
        """音频启用状态改变"""
        enabled = (state == Qt.Checked)
        self.audio_source_combo.setEnabled(enabled)
        self._emit_settings_changed()

    def _on_audio_setting_changed(self):
        """音频设置改变"""
        self._emit_settings_changed()
