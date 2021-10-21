import sys

from PyQt5.QtWidgets import QApplication

from mainwindow import MainWindow


def main(args):
    app = QApplication(args)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main(sys.argv)
