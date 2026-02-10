"""测试悬浮控制球"""

import sys
from PyQt5.QtWidgets import QApplication
from gui.floating_ball import FloatingControlBall


def main():
    app = QApplication(sys.argv)

    # 创建悬浮球
    floating_ball = FloatingControlBall()

    # 连接信号
    floating_ball.pause_clicked.connect(lambda: print("暂停/继续按钮被点击"))
    floating_ball.stop_clicked.connect(lambda: print("停止按钮被点击"))
    floating_ball.ball_hidden.connect(lambda: print("悬浮球被隐藏"))

    # 显示悬浮球
    floating_ball.show_ball()

    print("悬浮控制球测试")
    print("- 单击球体展开/收起控制面板")
    print("- 双击球体隐藏悬浮球")
    print("- 拖动球体移动位置")
    print("- 按 ESC 键收起控制面板")
    print("- 按 Ctrl+C 退出")

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
