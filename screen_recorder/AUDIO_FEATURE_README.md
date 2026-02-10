# 音频录制功能说明

## 功能概述

本次更新为屏幕录制软件添加了同步音频录制功能，支持：
- **麦克风录制** - 录制麦克风输入
- **系统音频录制** - 录制系统扬声器输出
- **混合录制** - 同时录制麦克风和系统音频

## 安装步骤

### 1. 安装Python依赖

```bash
pip install pyaudio ffmpeg-python
```

### 2. 安装FFmpeg（Windows）

FFmpeg是音视频合并的必需工具。

**方法1：使用 Chocolatey**
```bash
choco install ffmpeg
```

**方法2：手动安装**
1. 下载FFmpeg：https://www.gyan.dev/ffmpeg/builds/
2. 下载 "ffmpeg-release-essentials.zip"
3. 解压到 `C:\ffmpeg`
4. 将 `C:\ffmpeg\bin` 添加到系统PATH环境变量

**验证安装**
```bash
ffmpeg -version
```

### 3. 启用Windows立体声混音（可选）

如需录制系统音频，需要启用"立体声混音"设备：

1. 右键任务栏音量图标 → "声音设置"
2. 滚动到"更多声音设置"或"录制设备"
3. 在空白处右键 → "显示已禁用的设备"
4. 找到"立体声混音" → 右键 → "启用"
5. 设为默认录制设备（可选）

## 使用方法

### 通过GUI使用

1. **启动程序**
   ```bash
   python main.py
   ```

2. **配置音频设置**
   - 在左侧控制面板找到"音频设置"
   - 勾选"启用音频录制"
   - 选择音频源：
     - **仅麦克风** - 只录制麦克风输入
     - **仅系统音频** - 只录制扬声器输出
     - **麦克风 + 系统音频** - 混合录制两者
   - 选择麦克风设备（如有多个）

3. **开始录制**
   - 点击"开始录制"按钮
   - 程序会自动录制视频和音频
   - 停止录制后，音视频会自动合并

### 音频设置说明

| 设置 | 说明 |
|------|------|
| 启用音频录制 | 是否开启音频录制功能 |
| 音频源 | 选择录制的音频来源 |
| 麦克风 | 选择麦克风设备（"默认设备"或具体设备） |

## 文件变更

### 新增文件

1. **core/audio_capture.py** - 音频捕获模块
   - `AudioCapture` 类：管理音频录制
   - 支持麦克风、系统音频、混合录制
   - 自动音频混合

2. **utils/audio_merger.py** - 音视频合并工具
   - `merge_audio_video()` - 使用FFmpeg合并音视频
   - `check_ffmpeg_available()` - 检查FFmpeg是否可用

### 修改文件

1. **core/recorder.py** - 核心录制引擎
   - 添加音频相关属性
   - `start_recording()` 方法增加音频参数
   - `stop_recording()` 方法增加音频合并逻辑

2. **gui/controls.py** - 控制面板
   - 添加音频设置UI（复选框、下拉框）
   - `get_settings()` 返回音频配置
   - 添加音频设备枚举功能

3. **gui/main_window.py** - 主窗口
   - `_start_recording()` 传递音频设置给录制器

4. **utils/settings.py** - 设置管理
   - 添加音频相关默认设置
   - 添加音频设置验证

5. **requirements.txt** - 依赖列表
   - 添加 `pyaudio>=0.2.13`
   - 添加 `ffmpeg-python>=0.2.0`

## API示例

### 编程方式使用

```python
from core.recorder import Recorder

# 创建录制器
recorder = Recorder()

# 设置回调
recorder.on_recording_stopped = lambda path, frames, dur: print(f"保存到: {path}")

# 开始录制（带音频）
recorder.start_recording(
    output_path="output.mp4",
    fps=30,
    region=None,
    codec='H264',
    enable_audio=True,
    audio_source='both',  # 'mic', 'system', 'both'
    audio_device=None
)

# ... 录制中 ...

# 停止录制
recorder.stop_recording()
```

### 仅使用音频捕获

```python
from core.audio_capture import AudioCapture

# 创建音频捕获器
audio = AudioCapture(sample_rate=44100, channels=2)

# 查看可用设备
devices = audio.get_audio_devices()
for device in devices:
    print(f"{device['name']} (Loopback: {device['is_loopback']})")

# 开始录制
audio.start_recording(source='both', mic_device_index=None)

# ... 录制中 ...

# 停止并保存
audio.stop_recording()
audio.save_to_file("audio.wav")
audio.cleanup()
```

### 合并音视频

```python
from utils.audio_merger import merge_audio_video, check_ffmpeg_available

# 检查FFmpeg
if check_ffmpeg_available():
    # 合并音视频
    success = merge_audio_video(
        video_path="video.mp4",
        audio_path="audio.wav",
        output_path="output.mp4"
    )
    print("合并成功" if success else "合并失败")
else:
    print("FFmpeg未安装")
```

## 常见问题

### Q: 找不到立体声混音设备？
**A:** Windows可能默认禁用了此设备：
1. 打开"声音控制面板" → "录制"选项卡
2. 右键空白处 → 勾选"显示已禁用的设备"
3. 找到"立体声混音"并启用

### Q: 录制的视频没有声音？
**A:** 检查：
1. 是否勾选了"启用音频录制"
2. FFmpeg是否正确安装并添加到PATH
3. 音频设备是否被其他程序占用
4. 查看控制台输出的错误信息

### Q: pyaudio安装失败？
**A:** Windows用户可能需要预编译的wheel包：
```bash
pip pip install pipwin
pipwin install pyaudio
```

或从 https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio 下载对应版本

### Q: 音视频不同步？
**A:** 可能原因：
1. CPU性能不足，降低FPS
2. 磁盘I/O瓶颈，使用SSD存储
3. 音频采样率不匹配，使用默认44100Hz

### Q: FFmpeg合并失败？
**A:** 检查：
1. FFmpeg是否正确安装：`ffmpeg -version`
2. 临时文件是否被删除
3. 查看控制台错误信息

## 技术细节

### 音频录制流程

```
开始录制
    ↓
启动音频捕获线程（如果启用）
    ↓
并行执行：
  - 视频线程：捕获屏幕帧 → 写入视频文件
  - 音频线程：捕获音频 → 存储在内存中
    ↓
停止录制
    ↓
1. 停止视频和音频捕获
2. 保存音频到临时WAV文件
3. 使用FFmpeg合并音视频
4. 删除临时文件
    ↓
完成
```

### 音频混合算法

使用numpy进行音频混合：
```python
mixed = np.clip(arr1 + arr2, -32768, 32767).astype(np.int16)
```
- 确保混合后不会溢出
- 自动处理不同长度的音频流

### FFmpeg命令

实际使用的FFmpeg命令：
```bash
ffmpeg -i video_temp.mp4 -i audio_temp.wav -c:v copy -c:a aac -strict experimental -y output.mp4
```
- `-c:v copy` - 不重新编码视频（快速）
- `-c:a aac` - 音频编码为AAC（兼容性好）
- `-strict experimental` - 允许使用实验性AAC编码器

## 性能建议

1. **FPS设置**
   - 普通屏幕录制：30 FPS
   - 游戏/高动态内容：60 FPS
   - 仅演示文稿：15-20 FPS

2. **编码器选择**
   - H264：文件小，兼容性好
   - MJPG：录制快，文件较大
   - XVID：平衡选择

3. **音频质量**
   - 默认44100Hz采样率（CD质量）
   - 可在`audio_capture.py`中调整
   - 更高采样率会增加CPU和文件大小

## 未来改进

可能的增强功能：
- [ ] 音频可视化（波形显示）
- [ ] 实时音量控制
- [ ] 音频格式选择（MP3、OGG等）
- [ ] 多轨音频录制
- [ ] 音频增强（降噪、增益）
- [ ] 录制过程中音频预览

## 支持

如有问题，请检查：
1. 控制台输出的错误信息
2. FFmpeg和pyaudio是否正确安装
3. 音频设备是否可用

---

版本: 1.1.0
更新日期: 2025
