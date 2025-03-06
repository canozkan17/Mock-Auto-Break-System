import classes
import light_detection
import DB_class
from DES_class import *
import UI
from PyQt5.QtWidgets import QApplication
import sys

import threading





car = classes.Vehicle()


print(f"car speed: {car.speed_kmh} km/h")
db = DB_class.DataBase()
db.create_DB()

app = QApplication(sys.argv)
window = UI.AutoBrakeSystemUI(car,db)
window.show()


sys.exit(app.exec_())









