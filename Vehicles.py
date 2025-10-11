class Vehicle:
    def __init__(self, typo, age, weight, cost, color, condition=100):
        self.typo = typo
        self.age = age
        self.condition = condition
        self.weight = weight
        self.color = color
        self.cost = cost

    def change_color(self, color):
        self.color = color

    def explode(self):
        del self

    def get_older(self, years):
        self.age -= years
        self.cost -= 100000
        self.condition -= 10

    def upgrade(self):
        if self.condition < 100:
            self.condition += 5
            self.cost += 20000

class Car(Vehicle):
    def __init__(self, typo, age, weight, cost, color, drive):
        super().__init__(typo, age, weight, cost, color)
        self.drive = drive


class Motorcycle(Vehicle):
    def __init__(self):
        super().__init__()

class Boat(Vehicle):
    def __init__(self):
        super().__init__()

car = Car(1, 2, 2, 10000000000, "Red", "Front")
print()