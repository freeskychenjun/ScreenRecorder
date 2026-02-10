import pyaudiowpatch as pyaudio

p = pyaudio.PyAudio()
count = p.get_device_count()

print('PyAudioWPatch loaded successfully!')
print(f'Available audio devices: {count}')
print()

for i in range(min(count, 15)):
    info = p.get_device_info_by_index(i)
    name = info['name']
    channels = info['maxInputChannels']
    is_loopback = 'Loopback' in name or 'WASAPI' in name
    print(f'{i}: {name[:60]} (Channels: {channels}, Loopback: {is_loopback})')

p.terminate()
