# 项目结构说明

```
screen_recorder/                    # 项目根目录
│
├── main.py                         # 📱 应用程序入口点
│   └── 初始化Qt应用，显示主窗口
│
├── requirements.txt                # 📦 Python依赖包列表
│   ├── PyQt5          # GUI框架
│   ├── mss             # 屏幕捕获
│   ├── opencv-python   # 视频编码
│   ├── Pillow          # 图像处理
│   └── numpy           # 数组操作
│
├── README.md                       # 📖 项目文档
│   └── 功能介绍、安装说明、使用指南
│
├── QUICKSTART.md                   # 🚀 快速开始指南
│   └── 新手友好的使用教程
│
├── test_recorder.py                # 🧪 功能测试脚本
│   └── 测试各个模块是否正常工作
│
├── gui/                            # 🖼️  GUI界面模块
│   ├── __init__.py                # 模块初始化
│   │
│   ├── main_window.py             # 🏠 主窗口 (400行)
│   │   ├── 录制控制
│   │   ├── 录制历史管理
│   │   ├── 菜单栏和状态栏
│   │   └── 与Recorder核心集成
│   │
│   ├── region_selector.py         # 🎯 区域选择器 (350行)
│   │   ├── 全屏透明覆盖窗口
│   │   ├── 鼠标拖拽选择区域
│   │   ├── 实时尺寸显示
│   │   └── 预设分辨率支持
│   │
│   └── controls.py                # 🎛️  控制面板 (350行)
│       ├── 录制控制按钮
│       ├── FPS设置滑块
│       ├── 编码器选择
│       ├── 输出目录设置
│       └── 实时统计信息显示
│
├── core/                           # ⚙️  核心录制引擎
│   ├── __init__.py                # 模块初始化
│   │
│   ├── screen_capture.py          # 📸 屏幕捕获 (150行)
│   │   ├── 使用mss库捕获屏幕
│   │   ├── 多显示器支持
│   │   ├── 区域捕获
│   │   └── 线程安全操作
│   │
│   ├── video_writer.py            # 🎬 视频编码 (200行)
│   │   ├── OpenCV VideoWriter封装
│   │   ├── H264/MJPG/XVID编码器
│   │   ├── 帧写入和管理
│   │   └── 上下文管理器支持
│   │
│   └── recorder.py                # 🎥 录制引擎 (300行)
│       ├── 录制状态管理
│       ├── 多线程录制循环
│       ├── 暂停/继续功能
│       ├── 回调函数机制
│       └── 统计信息收集
│
└── utils/                          # 🔧 工具模块
    ├── __init__.py                # 模块初始化
    │
    ├── annotations.py             # ✏️  标注工具 (450行)
    │   ├── 画笔工具
    │   ├── 形状绘制（矩形、圆形、箭头）
    │   ├── 文字标注
    │   ├── 鼠标点击效果
    │   └── 帧标注应用
    │
    └── settings.py                # ⚙️  配置管理 (250行)
        ├── JSON配置文件
        ├── 设置验证
        ├── 默认值管理
        ├── 导入/导出配置
        └── 线程安全操作
```

## 模块依赖关系

```
main.py
  └─> gui.main_window.MainWindow
        ├─> gui.controls.ControlPanel
        ├─> gui.region_selector.RegionSelector
        └─> core.recorder.Recorder
              ├─> core.screen_capture.ScreenCapture
              └─> core.video_writer.VideoWriter

utils 模块被各个模块独立引用：
  ├─> utils.settings.SettingsManager (主窗口)
  └─> utils.annotations.AnnotationTool (未来扩展)
```

## 数据流

```
用户操作 (GUI)
    ↓
录制控制 (ControlPanel)
    ↓
录制引擎 (Recorder)
    ↓
屏幕捕获 (ScreenCapture) → 视频编码 (VideoWriter)
    ↓                          ↓
帧数据                    视频文件
```

## 线程架构

```
主线程 (GUI)
  ├── PyQt事件循环
  ├── 用户交互处理
  └── UI更新

录制线程 (独立)
  ├── 屏幕捕获循环
  ├── 帧处理
  └── 写入视频文件

线程同步
  ├── Event (停止信号)
  ├── Event (暂停信号)
  └── Lock (资源保护)
```

## 关键设计模式

1. **单例模式**: SettingsManager - 全局配置管理
2. **观察者模式**: Recorder回调机制 - 状态通知
3. **策略模式**: VideoWriter编码器选择
4. **状态模式**: Recorder录制状态管理
5. **工厂模式**: AnnotationTool标注创建

## 扩展点

### 添加新的标注类型
在 `utils/annotations.py` 中扩展 `AnnotationType` 枚举

### 添加新的编码器
在 `core/video_writer.py` 的 `CODECS` 字典中添加

### 自定义GUI主题
在各个GUI文件中修改样式表（QSS）

### 添加新的捕获源
继承 `ScreenCapture` 类实现新的捕获方式
