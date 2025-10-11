import math

class Figure:
    def __init__(self):
        self.line_color = ""
        self.fill_color = ""

class Square(Figure):
    def __init__(self, side):
        super().__init__()
        self.side = side

    def get_area(self):
        area = self.side**2
        return area

class Rectangle(Figure):
    def __init__(self, length, width):
        super().__init__()
        self.length = length
        self.width = width

    def get_area(self):
        area = self.length * self.width
        return area

class Triangle(Figure):
    def __init__(self, a, b, c):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c

    def get_area(self):
        a = self.a
        b = self.b
        c = self.c
        p = (a + b + c) / 2
        area = (p*(p-a)*(p-b)*(p-c))**0.5
        return area

class Circle(Figure):
    def __init__(self, radius):
        super().__init__()
        self.radius = radius

    def get_area(self):
        area = self.radius**2 * math.pi
        return area