"""
Main entry point for the MOCK Automatic Braking System simulation.

This script initializes the core components of the simulation:
- A `Vehicle` object from the `classes` module.
- A `DataBase` object from the `DB_class` module for logging.

It then creates and displays the main PyQt5 user interface (`AutoBrakeSystemUI`
from the `UI` module), passing the vehicle and database instances to it.
The application event loop is started, and the script will exit when the UI is closed.

The `light_detection` and `DES_class` modules are imported but not directly used
within this main script; their functionalities are likely invoked by other modules
(e.g., `UI` or `classes`). The `threading` module is imported but also not
directly used here, suggesting threading might be handled within the classes themselves.
"""
import classes
import light_detection # Imported but not directly used here. Likely used by other modules.
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









