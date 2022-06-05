class Car:

    def __init__(self, listOptions):
        self.brand = []
        self.size = []
        self.fuelType = []
        self.urbanMileage = []
        self.extraUrbanMileage = []
        self.price = []
        self.power = []
        self.numberDoors = None
        self.listOptions = listOptions

    def setCharacteristic(self, questionIndex, optionIndex):
        if questionIndex == 0:
            self.size.append(self.listOptions[questionIndex]["sql_data"][optionIndex])
        elif questionIndex == 1:
            self.brand.append(self.listOptions[questionIndex]["sql_data"][optionIndex])
        elif questionIndex == 2:
            self.numberDoors = optionIndex
        elif questionIndex == 3:
            self.extraUrbanMileage.append(self.listOptions[questionIndex]["sql_data"][optionIndex - 1])
        elif questionIndex == 4:
            self.urbanMileage.append(self.listOptions[questionIndex]["sql_data"][optionIndex - 1])

    def isEmpty(self):
        empty = True
        if not bool(self.brand):
            empty = False
        if not bool(self.size):
            empty = False
        if not bool(self.fuelType):
            empty = False
        if not bool(self.urbanMileage):
            empty = False
        if not bool(self.extraUrbanMileage):
            empty = False
        if not bool(self.price):
            empty = False
        if not bool(self.power):
            empty = False
        if self.numberDoors is not None:
            empty = False

        return empty
