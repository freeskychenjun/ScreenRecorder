"""屏幕录制软件 - 主程序入口"""

import sys
import os
import traceback
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.main_window import MainWindow


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    全局异常处理器

    Args:
        exc_type: 异常类型
        exc_value: 异常值
        exc_traceback: 异常追踪信息
    """
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))

    # 显示错误对话框
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle("程序错误")
    msg_box.setText("程序发生未捕获的异常")
    msg_box.setDetailedText(error_msg)
    msg_box.exec_()

    # 同时打印到控制台
    print("Fatal error:", file=sys.stderr)
    print(error_msg, file=sys.stderr)


def main():
    """主函数"""
    # 设置高DPI支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("屏幕录制软件")
    app.setOrganizationName("ScreenRecorder")

    # 设置全局异常处理
    sys.excepthook = handle_exception

    try:
        # 创建并显示主窗口
        main_window = MainWindow()
        main_window.show()

        # 运行应用
        sys.exit(app.exec_())

    except Exception as e:
        error_msg = f"启动程序时发生错误:\n{str(e)}\n\n{traceback.format_exc()}"

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("启动错误")
        msg_box.setText("无法启动程序")
        msg_box.setDetailedText(error_msg)
        msg_box.exec_()

        sys.exit(1)


if __name__ == '__main__':
    main()
