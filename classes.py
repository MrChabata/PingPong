#Класс, шаблон для объекта
class Human:

    #Конструктор класса
    def __init__(self, name, age, energy=100):
        print("Создали объект")

        # self.name = "" #задаем для всего класса
        # self.age = 0
        # self.energy = 100
        #Параметры, атрибуты, свойства
        self.name = name
        self.age = age
        self.energy = energy

    # Методы класса
    def work(self, hours):
        self.energy -= hours * 5

    def sleep(self, hours):
        self.energy += hours * 10

#Создаем объект, экземпляр класса
person = Human("Johny", 2, 90)
# person.name = "Johny"
# person.age = 2

#Вызов методов
person.work(12)
person.sleep(2)
print(person.name, person.age, person.energy)