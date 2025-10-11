class SmartDevice:

    def __init__(self):
        self.is_on = False
        self.room = None

    def OnOff(self):
        self.is_on = not self.is_on

#Наследование от класса SmartDevice
class SmartLamp(SmartDevice):

    def __init__(self):
        #Вызов конструктора родительского класса
        super().__init__()
        self.brightness = 100

class SmartConditioner(SmartDevice):
    def __init__(self):
        super().__init__()
        self.temperature = 18

lamp = SmartLamp()
lamp.OnOff()