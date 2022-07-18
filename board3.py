from PyQt5.QtCore import QBasicTimer, pyqtSignal, QObject
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QFrame
from PyQt5.QtMultimedia import QSound
from shape3 import Shape


class ScoreSignal(QObject):
    send_status_message = pyqtSignal(str)


class GameOverSignal(QObject):
    send_game_over_signal = pyqtSignal()


class Board(QFrame):

    def __init__(self):
        super().__init__()
        # coordinates of the four squares making each shape
        self.coords = [(0, 0), (0, 0), (0, 0), (0, 0)]
        # an array to hold all the coordinates and colors of the shapes that were placed
        self.bottom_matrix = []
        self.main_timer = QBasicTimer()
        self.minor_timer = QBasicTimer()
        # initial "speed" - in milliseconds. actual refresh rate
        self.speed = 750
        # this list is used to calculate the x values of each row
        self.rows = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        # counter for the number of rows removed each time
        self.counter = 0
        self.is_new = True
        self.top = 300

        # each shape receives its own color
        self.colorTable = {
            'none': (0,0,0),
            'line': (144,198,210),
            'tee': (183,99,237),
            'zee': (245,102,98),
            'es': (137,64,135),
            'el': (244, 195, 92),
            'mirror_l': (130,160,214),
            'square': (243, 253, 108)}

        self.levels = [
            {'score': 2000, 'speed': 650},
            {'score': 4000, 'speed': 550},
            {'score': 6000, 'speed': 450},
            {'score': 8000, 'speed': 350},

        ]
        # since y goes from 0 and up toward the bottom of the board, the min_y value
        # of a shape is actually the highest y value among the four squares making up the shape
        self.min_y = 0
        # min_x per shape is the smallest x value among the four squares making up the shape
        self.min_x = 0
        self.max_x = 0
        self.can_move_down = True
        self.can_move_left = True
        self.can_move_right = True

        self.main_timer.start(self.speed, self)
        # my_x and my_y is the starting position of each shape (0,0)
        self.my_x = 0
        self.my_y = 0
        # old_x and old_y are used to update the x and y values of the shape
        self.old_x = 0
        self.old_y = 0

        # starting the game - creating an instance of the shape class, setting the color
        self.newPiece = Shape()
        self.color = QColor(*self.colorTable[self.newPiece.shape])
        self.painter = QPainter()

        # populating the coordinates of the new shape. This is used to draw the shape.
        self.set_coordinates()

        self.scoring_table = {
            0: 0,
            1: 40,
            2: 100,
            3: 300,
            4: 1200,
        }
        self.score = 0
        self.score_signal = ScoreSignal()
        self.game_over_signal = GameOverSignal()

        self.game_on = True

        self.sound = QSound('sounds/start.wav')
        self.sound.play()

    def pause(self):
        if self.main_timer.isActive():
            self.main_timer.stop()
        else:
            self.main_timer.start(self.speed, self)

    def start_game(self):
        self.sound = QSound('sounds/start.wav')
        self.sound.play()
        self.game_on = True
        self.bottom_matrix = []
        self.remove_row()
        self.clean_matrix()
        self.score = 0
        self.coords = [(0, 0), (0, 0), (0, 0), (0, 0)]
        self.old_x = 0
        self.old_y = 0
        self.my_x = 0
        self.my_y = 0
        self.top = 300
        self.create_new_piece()
        self.main_timer.start(self.speed, self)

    def timerEvent(self, e):
        """the main timer calls the down method each time interval
        the minor timer is called when the bottom of the shape hits the pile,
        but the player still has time to move it left or right"""
        if self.game_on:
            if e.timerId() == self.main_timer.timerId():
                self.down()
            if e.timerId() == self.minor_timer.timerId():
                self.rest_block()
                self.minor_timer.stop()
                self.main_timer.start(self.speed, self)
        else:
            self.main_timer.stop()
            self.minor_timer.stop()

    def set_coordinates(self):
        shape = self.newPiece.shape
        self.coords = self.newPiece.select_shape(shape, self.is_new, self.coords, self.my_x, self.my_y)

    def update_coordinates(self):
        """this method updates the shape's coordinates when the shape moves in any direction or turns"""
        delta_x = self.my_x - self.old_x
        delta_y = self.my_y - self.old_y

        i = 0
        for coord in self.coords:
            coord_x = coord[0]
            coord_y = coord[1]
            coord_x += delta_x
            coord_y += delta_y
            new_tuple = (coord_x, coord_y)
            self.coords[i] = new_tuple
            i += 1
        self.old_x = self.my_x
        self.old_y = self.my_y

    def draw_all_shapes(self):
        """Renders the current shape, as well as the bottom pile of shapes"""
        self.painter.setPen(QColor(168, 34, 3))
        # paint the current shape:
        for i in range(4):
            self.painter.fillRect(*self.coords[i], 18, 18, self.color)
            self.painter.drawRect(*self.coords[i], 18, 18)

        # paint the bottom pile:
        if len(self.bottom_matrix) > 0:
            for square in self.bottom_matrix:
                self.painter.setPen(QColor(168, 34, 3))
                color = QColor(*square[2])
                self.painter.fillRect(square[0], square[1], 18, 18, color)
                self.painter.drawRect(square[0], square[1], 18, 18)

    def paintEvent(self, event):
        self.painter.begin(self)
        self.draw_all_shapes()
        self.painter.end()

    def create_new_piece(self):
        self.newPiece = Shape()
        self.remove_row()
        self.clean_matrix()
        self.my_x = 0
        self.my_y = 0
        self.old_x = 0
        self.old_y = 0
        self.coords = self.newPiece.initial_coords_selector(self.newPiece.shape, self.my_x, self.my_y)
        self.color = QColor(*self.colorTable[self.newPiece.shape])
        self.update()
        self.is_new = True

        # self.remove_row()
        # self.clean_matrix()

        self.can_move_down = True
        self.can_move_left = True
        self.can_move_right = True

    def end_game(self):
        self.sound = QSound('sounds/gameover.wav')
        self.sound.play()
        self.game_on = False
        self.main_timer.stop()
        self.minor_timer.stop()
        # sending the game over signal to the main window (tetris3.py)
        self.game_over_signal.send_game_over_signal.emit()

    def rest_block(self):
        """captures the last shape coordinates and colors and adds this to the bottom matrix list.
        then creates a new block"""
        self.sound = QSound('sounds/place.wav')
        self.sound.play()
        color = self.colorTable[self.newPiece.shape]
        for i in range(4):
            item = [self.coords[i][0], self.coords[i][1], color]
            self.bottom_matrix.append(item)

        for square in self.bottom_matrix:
            if square[1] < self.top:
                self.top = square[1]
        if self.top > 0:
            self.create_new_piece()
            for level in self.levels:
                if self.score > level['score']:
                    self.speed = level['speed']
        else:
            self.end_game()

    def turn(self):

        if self.newPiece.shape == 'square':
            return
        else:
            self.coords = self.newPiece.calculate_turn(self.coords, self.my_x, self.my_y)
            # self.is_new = False
            self.update_extreme_squares()
            self.update()

    def right(self):
        self.can_move()
        if self.max_x < 162 and self.can_move_right:
            self.my_x += 18
            self.update_coordinates()
            self.update_extreme_squares()
            self.update()

    def left(self):
        self.can_move()
        if self.min_x >= 18 and self.can_move_left:
            self.my_x -= 18
            self.update_coordinates()
            self.update_extreme_squares()
            self.update()

    def down(self):

        self.min_y = self.newPiece.min_y(coords=self.coords)
        self.can_move()
        if self.min_y < 270:
            if self.can_move_down:
                self.my_y += 18
                self.update_coordinates()
                self.newPiece.min_y(coords=self.coords)
                self.update_extreme_squares()
                self.update()
            else:
                # if block is not at the bottom of the board but cannot move down
                # check if block can move right or left
                # if yes, give it another time period before setting the block
                if self.can_move_right or self.can_move_left:
                    self.main_timer.stop()
                    self.minor_timer.start(300, self)
                    return

                else:
                    # if block cannot move in any direction, rest the block
                    self.rest_block()
        else:
            # if block is already at the bottom of the board - rest the block
            self.rest_block()

    def drop(self):
        # repeating the down motion until the block cannot move down
        self.sound = QSound('sounds/dropwoosh2.wav')
        self.sound.play()
        self.can_move()
        while self.can_move_down and self.my_y > 0:
            self.down()

    def print(self):
        print("my_x and my_y: ", self.my_x, ", ", self.my_y)
        print("self.coords----------------", self.coords)
        print("self.newPiece.coordinates: ", self.newPiece.coordinates)

    def update_extreme_squares(self):
        self.min_y = self.newPiece.min_y(coords=self.coords)
        self.min_x = self.newPiece.min_x(coords=self.coords)
        self.max_x = self.newPiece.max_x(coords=self.coords)

    def can_move(self):
        """checks if the block can move down, left and right"""
        self.update_extreme_squares()
        if self.min_y + 36 > self.top:
            if len(self.bottom_matrix) > 0:
                # check if the block can move right:
                self.can_move_right = True
                for square in self.coords:
                    for space in self.bottom_matrix:
                        if (square[0] + 18) == space[0] and square[1] == space[1]:
                            self.can_move_right = False
                            print("can't move right")
                # check if the block can move left:
                self.can_move_left = True
                for square in self.coords:
                    for space in self.bottom_matrix:
                        if (square[0] - 18) == space[0] and square[1] == space[1]:
                            self.can_move_left = False
                            print("can't move left")
                # check if the block can move down:
                self.can_move_down = True
                for square in self.coords:
                    for space in self.bottom_matrix:
                        if (square[1] + 18) == space[1] and square[0] == space[0]:
                            self.can_move_down = False
                            print("can't move down")

    def remove_row(self):
        self.rows = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        row_counter = 0
        for i in range(16):
            # for each of the 16 rows in the board, check which coordinates are "full"
            row_y = (i * 18)
            for square in self.bottom_matrix:
                if square[1] == row_y:
                    self.rows[i] += square[0]
                    # if a row's sum of x coordinates is at least 810, it means the row is full and should be removed
                    if self.rows[i] >= 810:
                        self.remove_from_matrix(row_y)
                        row_counter += 1
        if row_counter == 1:
            self.sound = QSound('sounds/oneline.wav')
            self.sound.play()
        if row_counter == 2:
            self.sound = QSound('sounds/twothreelines.wav')
            self.sound.play()
        if row_counter == 3:
            self.sound = QSound('sounds/twothreelines.wav')
            self.sound.play()
        if row_counter == 4:
            self.sound = QSound('sounds/fourlines.wav')
            self.sound.play()
        self.score += self.scoring_table[row_counter]
        self.score_signal.send_status_message.emit(str(f"Score: {self.score}"))

    def remove_from_matrix(self, row_y):
        """removing the row. Actually, technically pushing the row down
        where all the ys are 1000 so its invisible.
        The actual deletion of these values from bottom_matrix is done later."""
        self.bottom_matrix.sort(key=lambda x: x[1])
        for square in self.bottom_matrix:
            if square[1] == row_y:
                square[1] = 1000
                self.counter += 1
            if square[1] < row_y:
                square[1] += 18

    def clean_matrix(self):
        """removing all the items with a y value of 1,000 from bottom_matrix"""
        self.bottom_matrix.sort(key=lambda x: x[1])
        self.bottom_matrix = self.bottom_matrix[0:(len(self.bottom_matrix) - self.counter + 1)]
        self.counter = 0