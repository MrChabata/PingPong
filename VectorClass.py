class Vector2D:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_length(self):
        length = (self.x**2 + self.y**2)**0.5
        return length

    def add(self, other):
        self.x += other.x
        self.y += other.y

    def scale(self, k):
        self.x *= k
        self.y *= k

    def __str__(self):
        return f"x: {self.x}, y: {self.y}"


vector1 = Vector2D(2, 1)
vector2 = Vector2D(3, 5)
print(vector1.get_length(), vector2.get_length())
vector1.add(vector2)
print(vector1)
vector1.scale(2)
vector2.scale(2)
print(vector1)
print(vector2)