"""GUI测试脚本"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

print("Creating QApplication...")
app = QApplication(sys.argv)

print("Creating MainWindow...")
window = MainWindow()

print("Showing window...")
window.show()

print("GUI initialized successfully!")
print("Window title:", window.windowTitle())
print("Window size:", window.size().width(), "x", window.size().height())

print("\nGUI is running. Close the window to exit.")
sys.exit(app.exec_())
