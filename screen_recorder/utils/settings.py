"""配置管理 - JSON格式的配置文件管理"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime


class SettingsManager:
    """设置管理器"""

    # 默认设置
    DEFAULT_SETTINGS = {
        # 录制设置
        'fps': 30,
        'codec': 'H264',
        'output_dir': '',  # 空字符串表示使用默认目录

        # 音频设置
        'enable_audio': False,
        'audio_source': 'both',  # 'mic', 'system', 'both'
        'audio_device': None,

        # 区域设置
        'last_region': None,  # 最后使用的录制区域

        # 界面设置
        'window_width': 900,
        'window_height': 600,
        'splitter_state': None,

        # 标注设置
        'annotation_color': '红色',
        'annotation_thickness': 2,
        'show_click_effects': True,
        'enable_annotations': True,

        # 其他设置
        'auto_open_output_folder': False,
        'minimize_to_tray': False,
        'check_updates': True,

        # 元数据
        'version': '1.0.0',
        'last_updated': None
    }

    def __init__(self, config_file: Optional[str] = None):
        """
        初始化设置管理器

        Args:
            config_file: 配置文件路径，如果为None则使用默认路径
        """
        if config_file is None:
            # 默认配置文件路径
            config_dir = Path.home() / '.screen_recorder'
            config_dir.mkdir(parents=True, exist_ok=True)
            config_file = str(config_dir / 'settings.json')

        self.config_file = Path(config_file)
        self.settings: Dict[str, Any] = {}

        # 加载设置
        self.load()

    def load(self) -> bool:
        """
        从文件加载设置

        Returns:
            bool: 是否成功加载
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)

                # 合并默认设置和加载的设置
                self.settings = self.DEFAULT_SETTINGS.copy()
                self.settings.update(loaded_settings)

                return True
            else:
                # 配置文件不存在，使用默认设置
                self.settings = self.DEFAULT_SETTINGS.copy()
                self.save()
                return True

        except Exception as e:
            print(f"加载配置文件失败: {e}")
            self.settings = self.DEFAULT_SETTINGS.copy()
            return False

    def save(self) -> bool:
        """
        保存设置到文件

        Returns:
            bool: 是否成功保存
        """
        try:
            # 更新时间戳
            self.settings['last_updated'] = datetime.now().isoformat()

            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取设置值

        Args:
            key: 设置键
            default: 默认值

        Returns:
            Any: 设置值
        """
        return self.settings.get(key, default)

    def set(self, key: str, value: Any, auto_save: bool = True) -> bool:
        """
        设置值

        Args:
            key: 设置键
            value: 设置值
            auto_save: 是否自动保存

        Returns:
            bool: 是否成功设置
        """
        try:
            # 验证设置
            if not self._validate_setting(key, value):
                print(f"无效的设置值: {key} = {value}")
                return False

            self.settings[key] = value

            if auto_save:
                return self.save()

            return True

        except Exception as e:
            print(f"设置值失败: {e}")
            return False

    def get_all(self) -> Dict[str, Any]:
        """
        获取所有设置

        Returns:
            Dict[str, Any]: 所有设置
        """
        return self.settings.copy()

    def set_multiple(self, settings: Dict[str, Any], auto_save: bool = True) -> bool:
        """
        批量设置值

        Args:
            settings: 设置字典
            auto_save: 是否自动保存

        Returns:
            bool: 是否成功设置
        """
        try:
            for key, value in settings.items():
                if self._validate_setting(key, value):
                    self.settings[key] = value

            if auto_save:
                return self.save()

            return True

        except Exception as e:
            print(f"批量设置失败: {e}")
            return False

    def reset(self) -> bool:
        """
        重置为默认设置

        Returns:
            bool: 是否成功重置
        """
        self.settings = self.DEFAULT_SETTINGS.copy()
        return self.save()

    def _validate_setting(self, key: str, value: Any) -> bool:
        """
        验证设置值

        Args:
            key: 设置键
            value: 设置值

        Returns:
            bool: 是否有效
        """
        # FPS验证
        if key == 'fps':
            return isinstance(value, int) and 1 <= value <= 120

        # 编码器验证
        if key == 'codec':
            return value in ['H264', 'MJPG', 'XVID', 'MP4V', 'AVC1']

        # 区域验证
        if key == 'last_region':
            if value is None:
                return True
            if isinstance(value, dict):
                required_keys = ['top', 'left', 'width', 'height']
                return all(k in value for k in required_keys)
            return False

        # 窗口大小验证
        if key in ['window_width', 'window_height']:
            return isinstance(value, int) and value >= 300

        # 标注粗细验证
        if key == 'annotation_thickness':
            return isinstance(value, int) and 1 <= value <= 10

        # 布尔值验证
        if key in ['show_click_effects', 'enable_annotations',
                   'auto_open_output_folder', 'minimize_to_tray', 'check_updates',
                   'enable_audio']:
            return isinstance(value, bool)

        # 音频源验证
        if key == 'audio_source':
            return value in ['mic', 'system', 'both']

        # 其他设置默认有效
        return True

    def export(self, file_path: str) -> bool:
        """
        导出设置到文件

        Args:
            file_path: 导出文件路径

        Returns:
            bool: 是否成功导出
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"导出设置失败: {e}")
            return False

    def import_settings(self, file_path: str) -> bool:
        """
        从文件导入设置

        Args:
            file_path: 导入文件路径

        Returns:
            bool: 是否成功导入
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)

            # 验证并导入设置
            for key, value in imported_settings.items():
                if self._validate_setting(key, value):
                    self.settings[key] = value

            return self.save()

        except Exception as e:
            print(f"导入设置失败: {e}")
            return False

    def get_output_directory(self) -> Path:
        """
        获取输出目录

        Returns:
            Path: 输出目录路径
        """
        output_dir = self.get('output_dir', '')

        if not output_dir:
            # 使用默认目录
            output_dir = Path.home() / 'Desktop' / 'Recordings'
        else:
            output_dir = Path(output_dir)

        # 确保目录存在
        output_dir.mkdir(parents=True, exist_ok=True)

        return output_dir

    def get_last_region(self) -> Optional[Dict]:
        """
        获取最后使用的录制区域

        Returns:
            Optional[Dict]: 区域字典
        """
        return self.get('last_region')

    def set_last_region(self, region: Optional[Dict]):
        """
        设置最后使用的录制区域

        Args:
            region: 区域字典
        """
        self.set('last_region', region)

    def __repr__(self) -> str:
        """字符串表示"""
        return f"SettingsManager(config_file='{self.config_file}')"
