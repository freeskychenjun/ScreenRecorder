"""测试脚本 - 验证核心功能"""

import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from core.screen_capture import ScreenCapture
from core.video_writer import VideoWriter
from core.recorder import Recorder


def test_screen_capture():
    """测试屏幕捕获"""
    print("=" * 50)
    print("测试屏幕捕获模块")
    print("=" * 50)

    try:
        capture = ScreenCapture()

        # 测试获取显示器信息
        monitors = capture.get_monitors()
        print(f"✓ 检测到 {len(monitors)} 个显示器")
        for i, monitor in enumerate(monitors):
            print(f"  显示器 {i + 1}: {monitor['width']}x{monitor['height']}")

        # 测试捕获屏幕
        print("\n测试捕获屏幕...")
        frame = capture.capture_screen()
        print(f"✓ 成功捕获帧: {frame.shape}")

        # 测试获取虚拟屏幕尺寸
        width, height = capture.get_virtual_screen_size()
        print(f"✓ 虚拟屏幕尺寸: {width}x{height}")

        print("\n✅ 屏幕捕获模块测试通过！\n")
        return True

    except Exception as e:
        print(f"\n❌ 屏幕捕获模块测试失败: {e}\n")
        return False


def test_video_writer():
    """测试视频写入器"""
    print("=" * 50)
    print("测试视频写入模块")
    print("=" * 50)

    try:
        # 创建测试输出目录
        output_dir = Path.home() / "Desktop" / "Recordings"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = str(output_dir / "test_video.mp4")

        # 创建视频写入器
        writer = VideoWriter(output_path, fps=30, resolution=(1920, 1080), codec='H264')

        # 测试打开
        print("测试打开视频写入器...")
        if writer.open():
            print(f"✓ 成功创建视频文件: {output_path}")
        else:
            print("✗ 无法打开视频写入器")
            return False

        # 创建测试帧
        import numpy as np
        print("\n测试写入帧...")
        for i in range(90):  # 写入3秒的帧（30fps * 3秒）
            # 创建彩色渐变测试帧
            frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
            frame[:, :] = [i * 3 % 256, (i * 5) % 256, (i * 7) % 256]
            writer.write_frame(frame)

        print(f"✓ 成功写入 {writer.get_frame_count()} 帧")
        print(f"✓ 视频时长: {writer.get_duration():.2f} 秒")

        # 关闭写入器
        writer.close()

        # 检查文件大小
        file_size = VideoWriter.get_file_size_mb(output_path)
        print(f"✓ 文件大小: {file_size:.2f} MB")

        print("\n✅ 视频写入模块测试通过！\n")
        return True

    except Exception as e:
        print(f"\n❌ 视频写入模块测试失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_recorder():
    """测试录制器"""
    print("=" * 50)
    print("测试录制引擎模块")
    print("=" * 50)

    try:
        # 创建测试输出目录
        output_dir = Path.home() / "Desktop" / "Recordings"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = str(output_dir / "test_recording.mp4")

        # 创建录制器
        recorder = Recorder()

        # 设置回调
        def on_started():
            print("✓ 录制已开始")

        def on_stopped(path, frames, duration):
            print(f"✓ 录制已停止")
            print(f"  文件: {path}")
            print(f"  帧数: {frames}")
            print(f"  时长: {duration:.2f}秒")

        def on_error(msg):
            print(f"✗ 错误: {msg}")

        recorder.on_recording_started = on_started
        recorder.on_recording_stopped = on_stopped
        recorder.on_error = on_error

        # 测试录制
        print("\n测试录制3秒...")
        success = recorder.start_recording(
            output_path=output_path,
            fps=30,
            region=None  # 全屏
        )

        if not success:
            print("✗ 无法开始录制")
            return False

        # 等待3秒
        for i in range(3, 0, -1):
            print(f"  倒计时: {i}秒")
            time.sleep(1)

            # 显示统计信息
            stats = recorder.get_stats()
            print(f"    已录帧数: {stats['frame_count']}, 实际FPS: {stats['actual_fps']:.1f}")

        # 停止录制
        recorder.stop_recording()

        print("\n✅ 录制引擎模块测试通过！\n")
        return True

    except Exception as e:
        print(f"\n❌ 录制引擎模块测试失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n")
    print("╔" + "═" * 48 + "╗")
    print("║" + " " * 10 + "屏幕录制软件 - 功能测试" + " " * 14 + "║")
    print("╚" + "═" * 48 + "╝")
    print("\n")

    results = []

    # 测试各个模块
    results.append(("屏幕捕获模块", test_screen_capture()))
    results.append(("视频写入模块", test_video_writer()))
    results.append(("录制引擎模块", test_recorder()))

    # 输出测试结果汇总
    print("=" * 50)
    print("测试结果汇总")
    print("=" * 50)

    passed = 0
    failed = 0

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\n总计: {passed} 通过, {failed} 失败")
    print("=" * 50)

    if failed == 0:
        print("\n🎉 所有测试通过！程序已准备就绪。")
        print("\n运行以下命令启动GUI:")
        print("  python main.py")
    else:
        print("\n⚠️  部分测试失败，请检查错误信息。")

    print("\n")


if __name__ == '__main__':
    main()
