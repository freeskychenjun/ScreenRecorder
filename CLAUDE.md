# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Windows screen recorder application built with Python and PyQt5. It captures screen recordings using the `mss` library and encodes them to video files using OpenCV. The application supports multiple recording modes, codecs, and includes annotation tools.

**Audio Recording:** The application supports synchronized audio recording from microphone, system audio (speakers), or both.

## Common Commands

### Running the Application

```bash
# Navigate to the project directory first
cd screen_recorder

# Install dependencies (first time only)
pip install -r requirements.txt

# Run the main application
python main.py

# Or use the Windows batch script
启动.bat
```

### Testing

```bash
# Run all functional tests
python test_recorder.py

# Test GUI only
python test_gui.py
```

### Building Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build single-file executable
pyinstaller --onefile --windowed main.py
```

The executable is generated in `dist/main.exe`.

## Project Structure

The codebase is organized into three main layers:

```
screen_recorder/
├── main.py                 # Application entry point
├── gui/                    # PyQt5 GUI layer
│   ├── main_window.py      # Main window with recording controls
│   ├── region_selector.py  # Transparent overlay for area selection
│   └── controls.py         # Control panel (buttons, sliders, settings)
├── core/                   # Recording engine layer
│   ├── recorder.py         # Main recorder with state machine
│   ├── screen_capture.py   # Screen capture using mss
│   ├── video_writer.py     # Video encoding with OpenCV
│   └── audio_capture.py    # Audio capture (microphone/system audio)
└── utils/                  # Utilities
    ├── annotations.py      # Annotation/drawing tools
    ├── settings.py         # Configuration management (JSON)
    └── audio_merger.py     # Audio/video merging with FFmpeg
```

## Architecture Overview

### Threading Model

The application uses a multi-thread architecture:

- **Main Thread**: Runs the PyQt5 GUI event loop, handles user interactions
- **Recording Thread**: Independent thread that performs the screen capture loop
- **Audio Thread**: Independent thread that performs audio capture (when enabled)

Thread synchronization uses:
- `threading.Event` for stop/pause signals
- `threading.Lock` for resource protection
- PyQt5 signals/slots for cross-thread communication

### Recording Pipeline

```
User Action (GUI)
    ↓
MainWindow / ControlPanel
    ↓
Recorder.start_recording()
    ↓
[Recording Thread Loop]      [Audio Thread Loop (if enabled)]
    ↓                              ↓
ScreenCapture.capture_screen()    AudioCapture (mic/system)
    ↓                              ↓
VideoWriter.write_frame()         Audio frames stored in memory
    ↓                              ↓
Video File (.mp4)                  ↓
                            On Stop:
                            1. Save audio to temp WAV
                            2. Merge with FFmpeg
                            3. Clean up temp files
```

### Key Classes

**core/recorder.py:Recorder**
- Manages recording state (idle/recording/paused/stopped)
- Spawns recording thread and audio capture thread
- Provides callbacks: `on_recording_started`, `on_recording_stopped`, `on_error`
- Methods: `start_recording()`, `stop_recording()`, `pause_recording()`, `resume_recording()`
- Parameters: `enable_audio`, `audio_source`, `audio_device`

**core/audio_capture.py:AudioCapture**
- Audio recording using PyAudio
- Supports three modes: microphone only, system audio only, both
- Automatic audio mixing when recording both sources
- Methods: `start_recording()`, `stop_recording()`, `save_to_file()`, `get_audio_devices()`

**utils/audio_merger.py**
- FFmpeg-based audio/video merger
- Functions: `merge_audio_video()`, `check_ffmpeg_available()`
- Handles graceful degradation if FFmpeg is not available

**core/screen_capture.py:ScreenCapture**
- Wraps the `mss` library for screen capture
- Handles multi-monitor setups
- Methods: `capture_screen(region=None)`, `get_monitors()`, `get_virtual_screen_size()`

**core/video_writer.py:VideoWriter**
- Wraps OpenCV's `VideoWriter`
- Supports codecs: H264, MJPG, XVID, MP4V, AVC1
- Context manager support (`with` statement)
- Methods: `open()`, `write_frame()`, `close()`, `get_frame_count()`, `get_duration()`

### GUI Structure

**gui/main_window.py:MainWindow**
- Central hub integrating all components
- Layout: Controls panel on left, recording history table on right
- Menu bar with Open Output Folder and Exit actions
- Status bar showing current state
- Passes audio settings from ControlPanel to Recorder

**gui/region_selector.py:RegionSelector**
- Transparent full-screen overlay window
- Mouse drag to select capture region
- Preset resolution dropdown (1080p, 720p, etc.)
- Returns `dict` with region coordinates: `{'top': y, 'left': x, 'width': w, 'height': h}`

**gui/controls.py:ControlPanel**
- Recording control buttons (Start, Pause, Stop)
- FPS slider (10-60)
- Codec selector dropdown
- Output directory browser
- Real-time statistics display
- Audio settings (checkbox, source selector, device dropdown)

### Configuration

Settings are stored in `~/.screen_recorder/settings.json` and managed by `utils/settings.py:SettingsManager`.

Key settings:
- `fps`: Recording frame rate (10-60, default 30)
- `codec`: Video codec (H264, MJPG, XVID, etc.)
- `output_dir`: Default output directory
- `last_region`: Last selected recording region
- `show_click_effects`: Show mouse click animations
- `enable_audio`: Enable audio recording (default False)
- `audio_source`: Audio source - 'mic', 'system', or 'both'
- `audio_device`: Microphone device index (None = default)

## Development Notes

### Audio Recording Requirements

The audio recording feature requires:
1. **pyaudio** - Python audio library (install via `pip install pyaudio`)
2. **FFmpeg** - Command-line tool for audio/video merging
   - Windows: Install via `choco install ffmpeg` or download from https://ffmpeg.org
   - Verify installation: `ffmpeg -version`

### System Audio Capture

Windows requires enabling "Stereo Mix" or "WASAPI Loopback" to capture system audio:
1. Open Sound Control Panel → Recording tab
2. Right-click in blank space → Show Disabled Devices
3. Enable "Stereo Mix" or look for devices with "Loopback" in the name

### Codec Selection

- **H264**: Best compression/quality balance (recommended)
- **MJPG**: Better compatibility, no encoder tag warnings
- **XVID/MP4V**: Alternative codecs

Note: OpenCV may show encoder tag warnings with H264. These can be ignored as the video is still generated correctly.

### Performance Considerations

- **30 FPS**: Suitable for most recording scenarios
- **60 FPS**: Use for gaming or high-motion content
- **Lower FPS** (10-15): Reduces file size for static content
- **SSD**: Recommended for output to prevent frame drops during write
- **Audio overhead**: Audio recording adds minimal CPU overhead (~2-5%)

### Region Format

The `region` parameter uses the `mss` library format:
```python
region = {
    'top': int,      # Y coordinate
    'left': int,     # X coordinate
    'width': int,    # Width in pixels
    'height': int    # Height in pixels
}
```

### Callback Pattern

The Recorder uses callbacks for event handling:
```python
recorder.on_recording_started = lambda: print("Started")
recorder.on_recording_stopped = lambda path, frames, dur: print(f"Saved to {path}")
recorder.on_error = lambda msg: print(f"Error: {msg}")
```

### Audio Recording Example

```python
from core.recorder import Recorder

recorder = Recorder()

# Start recording with audio
recorder.start_recording(
    output_path="output.mp4",
    fps=30,
    region=None,
    codec='H264',
    enable_audio=True,
    audio_source='both',  # 'mic', 'system', or 'both'
    audio_device=None     # None = default microphone
)

# ... recording ...

recorder.stop_recording()
```

## Testing Strategy

Run `test_recorder.py` to verify:
1. Screen capture module functionality
2. Video writer encoding capability
3. Full recording pipeline
4. Audio capture functionality (if dependencies installed)

The test creates sample videos in `~/Desktop/Recordings/`.

## Known Issues

1. **H264 encoder warnings**: OpenCV may print tag warnings. These are benign and the video file is still valid.
2. **Multi-threading on some systems**: May have compatibility issues; context manager pattern in ScreenCapture helps mitigate.
3. **FFmpeg required**: Audio recording requires FFmpeg to be installed and in PATH. If not available, only video will be recorded.
4. **System audio on Windows**: May require enabling "Stereo Mix" or using WASAPI Loopback devices.
5. **PyAudio installation**: On Windows, may need to install from wheel packages or use `pipwin install pyaudio`.
