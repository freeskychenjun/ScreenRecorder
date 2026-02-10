"""简单GUI测试 - 验证GUI能否成功初始化"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

print("[1/5] Importing PyQt5...")
from PyQt5.QtWidgets import QApplication

print("[2/5] Importing GUI modules...")
from gui.main_window import MainWindow

print("[3/5] Creating QApplication...")
app = QApplication(sys.argv)

print("[4/5] Creating MainWindow...")
try:
    window = MainWindow()
    print("     - MainWindow created successfully")
    print(f"     - Window title: {window.windowTitle()}")
    print(f"     - Window size: {window.width()}x{window.height()}")
    print(f"     - Recorder state: {window.recorder.get_state()}")
except Exception as e:
    print(f"     ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("[5/5] Test completed!")
print()
print("=" * 50)
print("SUCCESS: GUI initialized without errors!")
print("=" * 50)
print()
print("To run the full GUI application:")
print("  python main.py")
print()
