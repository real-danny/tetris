from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication, QMessageBox
import sys
from board3 import Board


class Tetris(QMainWindow):

    def __init__(self):
        super().__init__()

        self.t_board = Board()
        self.setCentralWidget(self.t_board)
        self.message_box = QMessageBox()
        self.start_message = QMessageBox()
        self.resize(180, 315)
        self.center()
        self.setWindowTitle('Tetris')
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("score: ")
        self.t_board.score_signal.send_status_message[str].connect(self.status_bar.showMessage)
        self.t_board.game_over_signal.send_game_over_signal.connect(self.show_message_box)
        self.message_box.buttonClicked.connect(self.message_box_action)
        self.show()

    def center(self):
        """centers the window on the screen"""

        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width())-50),
                  int((screen.height() - size.height()) / 2))
        print("main window coordinates: ", self.x(), self.y())

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Right:
            self.t_board.right()
        if key == Qt.Key_Left:
            self.t_board.left()
        if key == Qt.Key_Down:
            self.t_board.down()
        if key == Qt.Key_Up:
            self.t_board.turn()
        if key == Qt.Key_P:
            self.t_board.pause()
        if key == Qt.Key_Space:
            self.t_board.drop()
        # if key == Qt.Key_R:
        #     self.t_board.start_game()

    def show_message_box(self):
        self.message_box.setText("GAME OVER!")
        self.message_box.setInformativeText("OK to restart, Cancel to exit")
        self.message_box.move(self.x()-20, self.y())
        self.message_box.resize(100, 200)
        self.message_box.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
        x = self.message_box.exec_()

    def message_box_action(self, button):
        if button.text() == 'Cancel':
            self.close()
        else:
            self.t_board.start_game()

def main():
    app = QApplication([])
    tetris = Tetris()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()