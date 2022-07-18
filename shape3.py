from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication, QWidget, QGridLayout
from random import randint, choice


class Shape(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shape")
        self.shapes = ['tee', 'zee', 'el', 'es', 'mirror_l', 'square', 'line']
        # self.shapes = ['line', 'square']
        self.coordinates = [
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0),
        ]
        self.coordinates_code = []
        self.coordinates_code_new = []

        # # 1 horizontal, 2 one turn, 3 two turns, 4 three turns
        # self.position = 1
        # here are the codes to create the 7 shapes
        self.zee = [(0, 0), (1, 0), (2, 1), (1, 1)]
        self.el = [(1, 0), (2, 2), (1, 2), (1, 1)]
        self.tee = [(0, 1), (1, 0), (2, 1), (1, 1)]
        self.square = [(0, 0), (1, 0), (0, 1), (1, 1)]
        self.line = [(0, 0), (0, 1), (0, 2), (0, 3)]
        self.mirror_l = [(1, 0), (0, 2), (1, 2), (1, 1)]
        self.es = [(2, 0), (1, 0), (0, 1), (1, 1)]

        self.shape = choice(self.shapes)
        print("shape selected:", self.shape)

        self.x = 0
        self.y = 0

        self.bottom_squares = []
        self.left_squares = []
        self.right_squares = []


    def initial_coords_selector(self, shape, my_x, my_y):
        """ creates the initial shape coordinates and returns them"""
        if shape == 'tee':
            for i in range(4):
                self.coordinates[i] = (my_x + self.tee[i][0] * 18, my_y + self.tee[i][1] * 18)

        if shape == 'zee':
            for i in range(4):
                self.coordinates[i] = (my_x + self.zee[i][0] * 18, my_y + self.zee[i][1] * 18)

        if shape == 'el':
            for i in range(4):
                self.coordinates[i] = (my_x + self.el[i][0] * 18, my_y + self.el[i][1] * 18)

        if shape == 'tee':
            for i in range(4):
                self.coordinates[i] = (my_x + self.tee[i][0] * 18, my_y + self.tee[i][1] * 18)

        if shape == 'square':
            for i in range(4):
                self.coordinates[i] = (my_x + self.square[i][0] * 18, my_y + self.square[i][1] * 18)

        if shape == 'mirror_l':
            for i in range(4):
                self.coordinates[i] = (my_x + self.mirror_l[i][0] * 18, my_y + self.mirror_l[i][1] * 18)

        if shape == 'line':
            for i in range(4):
                self.coordinates[i] = (my_x + self.line[i][0] * 18, my_y + self.line[i][1] * 18)

        if shape == 'es':
            for i in range(4):
                self.coordinates[i] = (my_x + self.es[i][0] * 18, my_y + self.es[i][1] * 18)

        return self.coordinates

    def coords_selector(self, coords, my_x, my_y):
        self.coordinates_code = self.calculate_coordinates_code(coords, my_x, my_y)
        for i in range(4):
            self.coordinates[i] = (my_x + self.coordinates_code[i][0] * 18, my_y + self.coordinates_code[i][1] * 18)
        return self.coordinates

    def select_shape(self, shape, new, coords, my_x, my_y):
        print("select_shape running")
        print("x and y provided:", my_x, my_y)
        print("coords provided:", coords)
        if new:
            new_coords = self.initial_coords_selector(shape, my_x, my_y)
            print("returning coords for new shape:", new_coords)
        else:
            new_coords = self.coords_selector(coords, my_x, my_y)
            print("returning coords for old shape:", new_coords)
        return new_coords

    def calculate_turn(self, coords, my_x, my_y):
        """calculates the new coordinates for a shape after a single clockwise rotation"""
        new_coordinates = []
        self.coordinates_code_new = []
        self.coordinates_code = self.calculate_coordinates_code(coords, my_x, my_y)
        new_coord = 0
        if self.shape != 'line':
            for coord in self.coordinates_code:
                if coord == (0, 1):
                    new_coord = (1, 0)
                if coord == (2, 1):
                    new_coord = (1, 2)
                if coord == (1, 0):
                    new_coord = (2, 1)
                if coord == (1, 2):
                    new_coord = (0, 1)
                if coord == (2, 2):
                    new_coord = (0, 2)
                if coord == (0, 2):
                    new_coord = (0, 0)
                if coord == (0, 0):
                    new_coord = (2, 0)
                if coord == (2, 0):
                    new_coord = (2, 2)
                if coord == (1, 1):
                    new_coord = (1, 1)
                self.coordinates_code_new.append(new_coord)
        else:
            for coord in self.coordinates_code:
                x_coord = coord[0]
                y_coord = coord[1]
                new_coord = (y_coord, x_coord)
                self.coordinates_code_new.append(new_coord)

        for i in range(4):
            new_x = self.coordinates_code_new[i][0] * 18 + my_x
            new_y = self.coordinates_code_new[i][1] * 18 + my_y
            new_tuple = (new_x, new_y)
            new_coordinates.append(new_tuple)
        print("updated coords after turn: ", new_coordinates)
        return new_coordinates

    def calculate_coordinates_code(self, coords, my_x, my_y):
        """takes the full coordinates and returns the skeleton code"""
        self.coordinates_code = []
        for coord in coords:
            code_x = int((coord[0] - my_x) / 18)
            code_y = int((coord[1] - my_y) / 18)
            tup_xy = (code_x, code_y)
            self.coordinates_code.append(tup_xy)
        return self.coordinates_code

    def min_y(self, coords):
        min_y = 0
        for i in range(4):
            if coords[i][1] > min_y:
                min_y = coords[i][1]
        return min_y

    def min_x(self, coords):
        min_x = 1000
        for i in range(4):
            if coords[i][0] < min_x:
                min_x = coords[i][0]
        return min_x

    def max_x(self, coords):
        max_x = 0
        for i in range(4):
            if coords[i][0] > max_x:
                max_x = coords[i][0]
        return max_x

