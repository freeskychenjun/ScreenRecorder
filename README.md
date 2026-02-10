# Windows Screen Recorder

一款基于Python的Windows屏幕录制软件，支持音视频同步录制。

## 功能特性

### 视频录制
- **多种录制模式**: 全屏录制、自定义区域录制
- **高质量编码**: 支持H.264、MJPG、XVID等多种编码格式
- **暂停/继续**: 录制过程中可暂停和继续
- **实时统计**: 显示帧数、时长、实际FPS等录制信息
- **轻量高效**: 使用mss库实现高性能屏幕捕获
- **录制历史**: 自动管理录制历史记录

### 音频录制 ✨ NEW
- **多音源支持**: 麦克风、系统音频或同时录制
- **Loopback录制**: 支持录制扬声器输出（系统声音）
- **音频混合**: 自动混合麦克风和系统音频
- **音视频同步**: FFmpeg自动合并，确保音画同步

### 其他功能
- **实时标注**: 支持画笔、文字、箭头等标注工具
- **鼠标追踪**: 录制时显示鼠标点击效果
- **系统托盘**: 最小化到托盘，录制时不干扰

## 快速开始

### 1. 安装依赖

```bash
# 进入项目目录
cd screen_recorder

# 安装基础依赖包
pip install -r requirements.txt

# Windows音频库（如果PyAudio安装失败）
pip install PyAudioWPatch
```

### 2. 安装FFmpeg（音视频合并必需）

**使用Chocolatey（推荐）**:
```bash
choco install ffmpeg
```

**手动安装**:
1. 访问 https://www.gyan.dev/ffmpeg/builds/
2. 下载 `ffmpeg-release-essentials.zip`
3. 解压到 `C:\ffmpeg`
4. 将 `C:\ffmpeg\bin` 添加到系统PATH

验证安装:
```bash
ffmpeg -version
```

### 3. 运行程序

```bash
# 启动应用
python main.py

# 或使用批处理文件
启动.bat
```

### 3. 使用指南

#### 录制屏幕（仅视频）

1. **选择录制区域**
   - 点击"📷 选择录制区域"按钮
   - 在弹出的透明窗口中拖拽鼠标选择区域
   - 或从下拉菜单选择预设分辨率（1920x1080、1280x720等）
   - 点击"确认选择"完成

2. **调整录制设置**
   - **帧率**: 使用滑块调整FPS（10-60）
   - **编码器**: 选择视频编码格式（H264、MJPG、XVID等）
   - **输出目录**: 点击"浏览"更改保存位置

3. **开始录制**
   - 点击"▶ 开始录制"按钮开始
   - 录制过程中可以点击"⏸ 暂停"按钮暂停
   - 点击"⏹ 停止"按钮结束录制

#### 录制带声音的视频 ✨

1. **启用音频录制**
   - 在"音频设置"区域勾选"启用音频录制"
   - 选择音频源：
     - **仅麦克风**: 录制您的声音（适合教学讲解）
     - **仅系统音频**: 录制扬声器输出（适合录制音乐、视频）
     - **麦克风 + 系统音频**: 同时录制两者（适合游戏解说）

2. **选择音频设备**
   - 从"麦克风"下拉列表选择要使用的设备
   - 带`[Loopback]`标记的是系统音频设备

3. **开始录制**
   - 点击"▶ 开始录制"
   - 程序会同时录制视频和音频
   - 停止后自动使用FFmpeg合并音视频

**注意**:
- 如需录制系统音频，Windows用户可能需要启用"立体声混音"设备
- 确保FFmpeg已安装并添加到PATH

4. **查看录制结果**
   - 录制完成后会自动保存到输出目录
   - 右侧"录制历史"表格显示所有录制文件
   - 右键点击文件可以打开或删除

#### 快捷键

- `Ctrl+O`: 打开输出文件夹
- `Ctrl+Q`: 退出程序
- `ESC`: 在区域选择器中取消选择

## 项目结构

```
screen_recorder/
├── main.py                 # 应用入口
├── gui/
│   ├── __init__.py
│   ├── main_window.py      # 主窗口界面
│   ├── region_selector.py  # 区域选择器
│   └── controls.py         # 录制控制面板
├── core/
│   ├── __init__.py
│   ├── recorder.py         # 核心录制引擎
│   ├── screen_capture.py   # 屏幕捕获模块
│   ├── audio_capture.py    # 音频捕获模块 ✨ NEW
│   └── video_writer.py     # 视频编码模块
├── utils/
│   ├── __init__.py
│   ├── annotations.py      # 实时标注工具
│   ├── settings.py         # 配置管理
│   └── audio_merger.py     # 音视频合并工具 ✨ NEW
├── requirements.txt        # 依赖包
├── 用户使用手册.md         # 详细使用文档 ✨ NEW
├── 快速入门.md            # 快速入门指南 ✨ NEW
├── AUDIO_FEATURE_README.md # 音频功能说明 ✨ NEW
└── README.md              # 说明文档
```

## 技术架构

### 核心技术

- **GUI框架**: PyQt5 - 成熟的桌面应用框架
- **屏幕捕获**: mss - 高性能跨平台屏幕捕获库
- **视频编码**: OpenCV - 支持多种视频编码格式
- **图像处理**: NumPy - 高效数组操作

### 录制流程

1. **屏幕捕获**: ScreenCapture类使用mss库捕获屏幕或指定区域
2. **帧处理**: 录制循环以设定的FPS持续捕获帧
3. **视频编码**: VideoWriter类使用OpenCV将帧编码为视频文件
4. **状态管理**: Recorder类管理录制状态（空闲/录制/暂停/停止）

### 多线程架构

- **主线程**: 运行GUI，处理用户交互
- **录制线程**: 独立线程执行录制循环，避免阻塞GUI
- **线程同步**: 使用Event和Lock进行线程间通信

## 系统要求

- **操作系统**: Windows 10/11
- **Python版本**: Python 3.8 或更高
- **内存**: 至少2GB可用内存
- **磁盘空间**: 根据录制时长和画质要求

### 性能建议

- **30 FPS**: 适合大多数录制场景
- **60 FPS**: 适合游戏录制或动态内容
- **H264编码**: 最佳压缩比和质量平衡
- **降低分辨率**: 可提升性能并减少文件大小

## 配置文件

配置文件自动保存在 `~/.screen_recorder/settings.json`

```json
{
    "fps": 30,
    "codec": "H264",
    "output_dir": "C:\\Users\\YourName\\Desktop\\Recordings",
    "last_region": null,
    "annotation_color": "红色",
    "show_click_effects": true
}
```

## 常见问题

### 通用问题

**Q: 录制的视频很大怎么办？**
A: 可以尝试：
- 降低帧率（如从60FPS降到30FPS）
- 使用H264编码器
- 减小录制区域

**Q: 录制时卡顿怎么办？**
A: 可能的原因：
- 硬盘写入速度慢，尝试使用SSD
- 关闭其他占用CPU的程序
- 降低录制帧率或分辨率

**Q: 支持哪些视频格式？**
A: 主要支持MP4格式（通过H264编码），其他格式可通过更改编码器实现。

### 音频录制问题 ✨

**Q: 无法录制音频？**
A: 检查：
1. 是否勾选"启用音频录制"
2. PyAudioWPatch是否已安装（`pip install PyAudioWPatch`）
3. 音频设备是否被其他程序占用

**Q: 无法录制系统音频？**
A: Windows用户需要：
1. 启用"立体声混音"设备
2. 或确保Loopback设备可用
3. 在"声音设置"→"录制"中显示禁用的设备

**Q: 音视频不同步？**
A: 可能原因：
- CPU性能不足 → 降低FPS
- 磁盘I/O瓶颈 → 使用SSD
- 录制时长过长 → 分段录制

**Q: FFmpeg相关错误？**
A: 解决方法：
1. 安装FFmpeg：`choco install ffmpeg`
2. 验证安装：`ffmpeg -version`
3. 确保FFmpeg在系统PATH中

## 高级功能

### 实时标注

虽然GUI中已预留接口，实时标注功能可在后续版本中使用：

```python
from utils.annotations import AnnotationTool

# 创建标注工具
annotation_tool = AnnotationTool()

# 在录制回调中应用标注
def on_frame_captured(frame):
    annotated_frame = annotation_tool.apply_annotations(frame)
    # 继续处理...
```

### 配置管理

```python
from utils.settings import SettingsManager

# 加载配置
settings = SettingsManager()
fps = settings.get('fps', 30)

# 保存配置
settings.set('fps', 60)
```

## 打包为EXE

使用PyInstaller打包：

```bash
# 安装PyInstaller
pip install pyinstaller

# 打包
pyinstaller --onefile --windowed main.py
```

生成的exe文件在 `dist/main.exe`

## 开发计划

### 已完成 ✅
- [x] 基础录制功能
- [x] 区域选择
- [x] 多编码器支持
- [x] 暂停/继续功能
- [x] 录制历史管理
- [x] 系统托盘最小化
- [x] **音频录制支持**（麦克风、系统音频、混合录制）✨ v1.1.0
- [x] **音视频自动合并**（基于FFmpeg）✨ v1.1.0

### 计划中 📋
- [ ] 实时标注工具GUI集成
- [ ] 鼠标点击效果可视化
- [ ] 录制预览窗口
- [ ] 视频剪辑功能
- [ ] 音频可视化（波形显示）
- [ ] 多音频设备同时录制

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 更新日志

### v1.1.0 (2025-02-10) ✨
- **新增音频录制功能**
  - 支持麦克风录制
  - 支持系统音频（Loopback）录制
  - 支持混合录制（麦克风+系统音频）
- **新增音视频自动合并**
  - 集成FFmpeg进行音视频合并
  - 自动处理临时文件
- **新增音频设置UI**
  - 音频启用开关
  - 音频源选择器
  - 音频设备列表
- **改进系统托盘功能**
  - 完整的托盘菜单
  - 托盘图标状态显示
- **新增用户文档**
  - 详细用户使用手册
  - 快速入门指南
  - 音频功能说明

### v1.0.0 (2025-02-09)
- 初始版本发布
- 实现核心录制功能
- 实现GUI界面
- 支持区域选择和多种编码格式
