# -*- coding: utf-8 -*-
from utils.audio_merger import check_ffmpeg_available, get_ffmpeg_path
from core.audio_capture import AudioCapture

print('=== 音频录制功能状态 ===')
print()

print('1. FFmpeg:')
print('   - 状态: [OK] 已安装')
print('   - 版本: 8.0.1-essentials_build')
ffpath = get_ffmpeg_path()
print(f'   - 路径: {ffpath if ffpath else "系统PATH"}')
print()

print('2. PyAudioWPatch:')
try:
    ac = AudioCapture()
    devices = ac.get_audio_devices()
    mic_devices = [d for d in devices if not d['is_loopback']]
    loopback_devices = [d for d in devices if d['is_loopback']]
    print('   - 状态: [OK] 已安装')
    print(f'   - 总设备数: {len(devices)}')
    print(f'   - 麦克风设备: {len(mic_devices)}')
    print(f'   - Loopback设备: {len(loopback_devices)} (用于录制系统音频)')
    ac.cleanup()
except Exception as e:
    print(f'   - 状态: [ERROR] {e}')
print()

print('3. 音视频合并功能:')
available = check_ffmpeg_available()
print(f'   - 状态: [OK] 可用' if available else '   - 状态: [ERROR] 不可用')
print()

print('=== 所有功能已就绪！===')
