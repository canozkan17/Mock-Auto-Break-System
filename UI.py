"""
This module defines the User Interface for the MOCK Automatic Braking System
simulation using PyQt5.

It includes the main application window (`AutoBrakeSystemUI`) which displays
various information like speed, sensor data, and traffic light status.
Custom widgets `TrafficLightWidget` and `SpeedometerWidget` are used for
visual representation. The `light_operations` class handles the logic
related to traffic light interactions and braking decisions based on light status
and distance.
"""
import sys
import time
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFrame, QMessageBox, QInputDialog, QVBoxLayout, QDialog
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QFontMetrics, QRadialGradient, QPalette,QPainterPathStroker, QIcon
from PyQt5.QtCore import Qt, QTimer, QRect, QUrl, QEasingCurve, QRectF, QPointF, pyqtSignal, QProcess, QObject
from PyQt5.QtMultimedia import QSoundEffect 
import classes
from DES_class import *
import classes
import subprocess


class AutoBrakeSystemUI(QMainWindow):
    """
    Main window for the MOCK Automatic Braking System simulation.

    This class sets up the user interface, including displays for speed,
    environmental conditions, braking distances, and a traffic light.
    It handles user interactions like starting a new run or entering admin mode
    to view decrypted logs. It also manages the simulation flow, including
    playing sound effects and updating the display based on data from the
    vehicle and light operations classes.

    Attributes:
        car ('classes.Vehicle'): An instance of the vehicle class containing its state.
        db ('DB_class.DataBase'): An instance of the database class for logging.
        light_operations_inst ('light_operations'): Instance for traffic light logic.
        current_speed (int): Current speed of the vehicle (UI state, possibly redundant if car.speed_kmh used).
        brake_countdown (int): Countdown for braking (UI state).
        light_color (str): Current color of the traffic light (UI state).
        key (str): Master key for encryption/decryption.
        engine_sound (QSoundEffect): Sound effect for a running engine.
        braking_sound (QSoundEffect): Sound effect for braking (Note: configured for infinite loop).
        timer (QTimer): Timer to update the display periodically (Note: set to a high frequency of 1ms).
        processing_thread (threading.Thread): Thread for running the main simulation logic.
        theme_mode (str): Indicates the current UI theme (e.g., "dark").
        start (float): Timestamp for the start of a simulation run.
        end (float): Timestamp for the end of a simulation run.
    """

    def __init__(self,vehicle:'classes.Vehicle',database:'DB_class.DataBase'):
        """
        Initializes the AutoBrakeSystemUI.

        Sets up the window title, geometry, and icon. Initializes references to the
        vehicle and database objects. Configures the UI theme, state variables (like
        current speed, light color, master key), data display labels through `init_ui()`,
        and sound effects. It also retrieves or sets up the master key for DES encryption.
        A QTimer is started for frequent UI updates, and the main simulation logic
        (`run_main_process`) is started in a separate thread.

        Args:
            vehicle ('classes.Vehicle'): The vehicle object for the simulation.
            database ('DB_class.DataBase'): The database object for logging data.
        """

        super().__init__()
        self.setWindowTitle("MOCK Automatic Braking System")
        self.setGeometry(200, 200, 1200, 800)    
        self.setWindowIcon(QIcon("brake_icon.png"))  
        
        # Initialize car and database 
        self.car = vehicle
        self.db = database
        self.light_operations_inst = light_operations(self.car,self)
                

        # Set up UI background to match system theme
        self.update_theme()
                
        # Initialize state variables
        self.current_speed = 0 # UI state, possibly mirrors car.speed_kmh
        self.brake_countdown = 0 # UI state, purpose might need review
        self.light_color = "" # Current traffic light color for UI
        self.is_blurred = False # This attribute is initialized but seems unused.
        self.key = "" # Master key for encryption

        self.start = time.time() # For timing simulation runs.
        self.end = 0


        # Initialize data display labels
        self.init_ui()


        # Initialize master key for encryption and decryption of data
        connection = sqlite3.connect("Loggs.db")
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT * FROM user_master_key")
            self.key = cursor.fetchone()[0]

        except sqlite3.OperationalError: # Table probably doesn't exist
            self.master_key()

        connection.commit()
        connection.close()      

        # Initialize sound effects
        self.engine_sound = QSoundEffect()
        self.engine_sound.setSource(QUrl.fromLocalFile("car_running.wav"))
        self.engine_sound.setLoopCount(QSoundEffect.Infinite)
        self.engine_sound.setVolume(0.5)
        

        self.braking_sound = QSoundEffect()
        self.braking_sound.setSource(QUrl.fromLocalFile("car_stopping.wav"))
        self.braking_sound.setLoopCount(QSoundEffect.Infinite) # Note: Braking sound set to loop infinitely.
        self.braking_sound.setVolume(0.5)
        
        # Start data update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1)  # UI updates every 1ms - this is very frequent and might impact performance.
        
        # Start the main processing in a separate thread
        self.processing_thread = threading.Thread(target=self.run_main_process)
        # self.processing_thread.daemon = True # Consider implications of daemon thread if main GUI exits unexpectedly.
        self.processing_thread.start()
    
    def master_key(self):
        """
        Prompts the user to enter a master key if one is not found in the database.

        This method displays an input dialog to get the master key from the user.
        The entered key is then stored in the 'user_master_key' table in the database.
        If the user cancels the dialog, the application exits.
        """

        #self.timer.stop() # Consider if stopping the main UI timer is necessary here.
        # Getting the master key for encryption and decryption
        dialog = QInputDialog(self)
        dialog.setWindowTitle('Enter your Master Key Below:')
        dialog.setLabelText('Enter your text:')
        dialog.resize(400, 200) 
        ok = dialog.exec_()
        if ok:
            self.key = dialog.textValue()

            connection = sqlite3.connect("Loggs.db")
            cursor = connection.cursor()
            
            cursor.execute("CREATE TABLE IF NOT EXISTS user_master_key (Master_Key TEXT)")
            cursor.execute("INSERT INTO user_master_key (Master_Key) VALUES (?)",(self.key,))

            connection.commit()
            connection.close()
        else: # User cancelled
            sys.exit()

        #self.timer.start(1) # Restart timer if stopped.
        
    def run_main_process(self):
        """
        Runs the main simulation logic in a separate thread.

        This involves starting engine sounds and initiating the traffic light
        interaction sequence via `self.light_operations_inst.light()`.
        Warning: `self.light_operations_inst.light()` might attempt to update UI
        elements directly or indirectly from this non-main thread, which is generally
        unsafe in PyQt. Consider using signals and slots for thread-safe UI updates.
        """
        self.engine_sound.play()
        self.light_operations_inst.light() # This call blocks until the light sequence is complete.
        

    def update_display (self):
        """
        Updates the UI elements with the current simulation data.

        This method is called periodically by a QTimer. It refreshes:
        - Date, time, and sensor data labels (humidity, rainfall, road/tire conditions).
        - Calculated distances (brake distance, stopping distance).
        - Speedometer display.
        - Traffic light distance and color.
        - Time to brake/intervention messages and values.
        - Braking status messages (driver applied, auto applied).
        - Handles the end-of-run scenario (light distance < 0), prompting the user
          to continue or exit, and encrypting data before exiting or restarting.
        """
        if hasattr (self.car, "collected_data"):
            self.date_time_value.setText(self.car.collected_data["Date_Time_Start"])
            self.humidity_value.setText(f"{self.car.collected_data["humidity"]}%<br>{self.car.collected_data["humidity situation"]}")
            self.rainfall_value.setText(f"{self.car.collected_data["rainfall"]}")
            self.road_value.setText(f"{self.car.collected_data["road_wetness"]}mm - {self.car.collected_data["road_temperature"]}°C")
            self.tire_value.setText(f"{self.car.collected_data["tire_temperature"]}°C - {self.car.collected_data["tire_pressure"]}kPa")
            self.brake_distance_value.setText(f"{self.car.collected_data["brake_distance"]} m")
            self.stopping_distance_value.setText(f"{self.car.collected_data["stopping_distance"]} m")
           
            
        self.speedometer.set_speed(self.car.speed_kmh)
        
           
        #Light Part
        self.light_distance_value.setText(f"{str(self.light_operations_inst.light_distance)} m")
        self.light_operations_inst.light_distance_cal() # Recalculates distance

        time_to_intervene = self.light_operations_inst.time_to_intervene_cal()

        if self.light_operations_inst.changed_light_color != "":
            self.light_color = self.light_operations_inst.changed_light_color   
        else:
            self.light_color = self.light_operations_inst.light_color 
        
        # Update UI based on whether the system thinks the car should stop
        if self.light_operations_inst.to_stop == True:
            self.time_to_brake_label.show()
            if time_to_intervene <= 0:
                self.time_to_brake_value.setText("0")  
            else:
                self.time_to_brake_value.setText(str(time_to_intervene))  
        
        # Update UI if auto-braking is imminent or active
        if self.light_operations_inst.to_brake == True:
            self.time_to_brake_label.setText("Auto Brake in")
            self.time_to_brake_value.setFont(QFont("Monad", 15))

        if self.car.user_brake_applied == True:
            self.braking_message.setText("BRAKES APPLIED BY DRIVER")
            self.careful_message.hide()
            self.braking_message.show()
            self.engine_sound.stop()
            if not self.braking_sound.isPlaying():
                self.braking_sound.play()

        if self.car.auto_brake_applied == True:
                self.careful_message.hide()
                self.braking_message.show()
                self.engine_sound.stop()
                if not self.braking_sound.isPlaying():
                    self.braking_sound.play()
                                
        self.traffic_light.set_color(self.light_color) 

        # End of run condition
        if self.light_operations_inst.light_distance < 0:
            self.braking_sound.stop()
            self.engine_sound.stop() # Ensure engine sound also stops
            self.timer.stop() # Stop updates during dialog

            self.end = time.time()
            print(f"Run duration: {self.end - self.start} seconds")
            print(f"Final self.light_color: {self.light_color}")
            print(f"Final self.light_operations_inst.light_color: {self.light_operations_inst.light_color}")
            print(f"Final self.light_operations_inst.changed_light_color: {self.light_operations_inst.changed_light_color}")

            msg_box = QMessageBox(self)
            msg_box.setWindowTitle('Simulation Ended: Continue?')
            msg_box.setText("The current simulation run has ended.")
            msg_box.setInformativeText("Do you want to start a new run?")
            msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg_box.setDefaultButton(QMessageBox.Ok)
            msg_box.setMinimumSize(400, 200) # Consider if this is necessary

            if msg_box.exec_() == QMessageBox.Ok:
                self.toggle_run_again()
            else:
                # Encrypting the run before exiting
                if hasattr(self.car, "collected_data"): # Ensure data exists
                    DES_Encryption_Decryption().Encrypt_to_db(self.car, self.key)
                    self.db.insert_db(self.car.collected_data)
                sys.exit()

    def toggle_run_again(self):
        """
        Handles the logic for restarting the simulation.

        Encrypts the data from the completed run, then quits the current
        application instance and starts a new one.
        """
        # Encrypting the previous run before proceeding to the next. 
        if hasattr(self.car, "collected_data"): # Ensure data exists
            DES_Encryption_Decryption().Encrypt_to_db(self.car, self.key)
            self.db.insert_db(self.car.collected_data)
        
        QApplication.quit()
        # Restart the program
        QProcess.startDetached(sys.executable, sys.argv)        

    def toggle_admin_mode(self):
        """
        Activates admin mode, allowing decryption and viewing of logs.

        Prompts for the master key. If correct, it decrypts the database content
        using `DES_Encryption_Decryption().Decrypt_from_db()`, then attempts to open
        a new command prompt window (Windows-specific) to display the decrypted data
        by executing a Python script snippet that calls `DB_class.DataBase().read_from_db()`.
        It also offers an option to reset (drop) the decrypted data and master key tables.
        """
        
        self.timer.stop() # Pause UI updates during dialogs
        
        dialog = QInputDialog(self)
        dialog.setWindowTitle('Enter Master Key for Admin Mode:')
        dialog.setLabelText('Master Key:')
        dialog.resize(400, 200)      

        ok = dialog.exec_()
        if ok:
            entered_key = dialog.textValue() # Use a different variable for clarity
            try:
                connection = sqlite3.connect("Loggs.db")
                cursor = connection.cursor()
                
                cursor.execute("SELECT Master_Key FROM user_master_key LIMIT 1") # More specific query
                result_tuple = cursor.fetchone()
                
                if result_tuple and result_tuple[0] == entered_key:
                    self.key = entered_key # Set the class key if it's correct
                    DES_Encryption_Decryption().Decrypt_from_db(self.db,self.key)
                    # Command to open new cmd (Windows-specific) and run python script to read DB.
                    # This approach has platform limitations.
                    command = f'start cmd /k "python -c ^"from DB_class import DataBase; DataBase().read_from_db(); input(\'Press Enter to close...\')^""'
                    try:
                        subprocess.Popen(command, shell=True)
                    except FileNotFoundError:
                        QMessageBox.warning(self, "Command Error", "Could not open command prompt. Ensure you are on Windows or adapt the command.")


                    msg_box_reset = QMessageBox(self) # Use a different name
                    msg_box_reset.setWindowTitle("Reset Decrypted Data?")
                    msg_box_reset.setText("Do you want to delete all decrypted data and the stored master key?")
                    msg_box_reset.setInformativeText("This action cannot be undone.")
                    msg_box_reset.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    msg_box_reset.setDefaultButton(QMessageBox.No)
                    if msg_box_reset.exec_() == QMessageBox.Yes:
                        cursor.execute("DROP TABLE IF EXISTS user_master_key")
                        cursor.execute("DROP TABLE IF EXISTS decrypted_data")
                        self.key = "" # Clear current key
                        QMessageBox.information(self, "Reset Complete", "Decrypted data and master key have been removed.")
                        # Prompt for new key or exit? For now, just informs.
                    connection.commit() # Commit changes (drops)
                else:
                    QMessageBox.warning(self, "Admin Access Denied", "Incorrect master key.")
                    
            except sqlite3.Error as e: # Catch specific SQLite errors
                print(f"Database error in admin mode: {e}")
                QMessageBox.critical(self, "Database Error", f"Could not access database: {e}")
            except Exception as e: # Catch other potential errors
                print(f"An unexpected error occurred in admin mode: {e}")
                QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            finally:
                if 'connection' in locals() and connection: # Ensure connection exists before closing
                    connection.close()
                
        self.timer.start(1) # Restart UI updates

    def update_theme(self):
        """
        Sets the UI theme. Currently hardcoded to a dark theme.
        """
        # Detect system theme using QPalette - This part is commented out or incomplete.
        # app = QApplication.instance()
        # palette = app.palette()

        # Check if background color is dark or light - This logic is missing.

        # Hardcoded dark theme
        self.setStyleSheet("""
            QMainWindow { background-color: #121212; color: white; }
            QLabel { color: white; }
            QPushButton { background-color: #3D4956; color: white; border-radius: 5px; padding: 10px; }
            QPushButton:hover { background-color: #4D5966; }
        """)
        self.theme_mode = "dark" # Explicitly set theme mode
        
    def init_ui(self):
        """
        Initializes and places all UI widgets on the main window.

        This includes labels for displaying data (date/time, sensor readings,
        distances), buttons (Admin Mode, Run Again), frames for grouping info,
        and custom widgets (TrafficLightWidget, SpeedometerWidget).
        """
        # Date and Time
        self.date_time_label = QLabel("Date Time: ",self)
        self.date_time_label.setGeometry(30, 30, 300, 50)
        self.date_time_label.setFont(QFont("Monad", 14))
        self.date_time_label.setAlignment(Qt.AlignVCenter)

        self.date_time_value = QLabel("", self)
        self.date_time_value.setGeometry(200, 30, 300, 50)
        self.date_time_value.setFont(QFont("Monad", 12))
        self.date_time_value.setAlignment(Qt.AlignVCenter)
        
        # Distance to Light
        self.light_distance_label = QLabel("Distance to Light",self)
        self.light_distance_label.setGeometry(825, 30, 300, 30)
        self.light_distance_label.setFont(QFont("Monad", 13))
        self.light_distance_label.setAlignment(Qt.AlignLeft)

        self.light_distance_value = QLabel("200 m", self) # Initial placeholder
        self.light_distance_value.setGeometry(950, 30, 180, 30)
        self.light_distance_value.setFont(QFont("Monad", 12))
        self.light_distance_value.setAlignment(Qt.AlignRight)
       
        # Stopping Distance
        self.stopping_distance_title = QLabel("Stopping Distance", self)
        self.stopping_distance_title.setGeometry(825, 100, 300, 30)
        self.stopping_distance_title.setFont(QFont("Monad", 13))
        self.stopping_distance_title.setAlignment(Qt.AlignLeft)
        
        self.stopping_distance_value = QLabel("", self)
        self.stopping_distance_value.setGeometry(950, 100, 200, 30)
        self.stopping_distance_value.setFont(QFont("Monad", 12))
        self.stopping_distance_value.setAlignment(Qt.AlignRight)
                
        # Brake Distance
        self.brake_distance_title = QLabel("Brake Distance", self)
        self.brake_distance_title.setGeometry(825, 170, 300, 30)
        self.brake_distance_title.setFont(QFont("Monad", 13))
        self.brake_distance_title.setAlignment(Qt.AlignLeft)
        
        self.brake_distance_value = QLabel("", self)
        self.brake_distance_value.setGeometry(950, 170, 200, 30)
        self.brake_distance_value.setFont(QFont("Monad", 12))
        self.brake_distance_value.setAlignment(Qt.AlignRight)

        # Time to Brake
        self.time_to_brake_label = QLabel("Time to Brake",self)
        self.time_to_brake_label.setGeometry(850, 300, 200, 30)
        self.time_to_brake_label.setFont(QFont("Monad", 14))
        self.time_to_brake_label.setAlignment(Qt.AlignRight)
        self.time_to_brake_label.hide() # Initially hidden

        self.time_to_brake_value = QLabel("", self)
        self.time_to_brake_value.setGeometry(1100, 300, 100, 30)
        self.time_to_brake_value.setFont(QFont("Monad", 12))
        self.time_to_brake_value.setAlignment(Qt.AlignLeft)

        # Admin Mode Button
        self.admin_button = QPushButton("ADMIN MODE", self)
        self.admin_button.setGeometry(940, 730, 220, 50)
        self.admin_button.setFont(QFont("Monad", 12, QFont.Bold))
        self.admin_button.clicked.connect(self.toggle_admin_mode)
        
        # Run Again Mode Button
        self.run_button = QPushButton("Run Again", self) # Changed text for clarity
        self.run_button.setGeometry(940, 670, 220, 50) # Adjusted position
        self.run_button.setFont(QFont("Monad", 12, QFont.Bold))
        self.run_button.clicked.connect(self.toggle_run_again)

        # Weather Info Frame
        self.weather_frame = QFrame(self)
        self.weather_frame.setGeometry(30, 250, 400, 500)
        # self.weather_frame.setFrameShape(QFrame.StyledPanel) # Optional: add border for visibility
        
        # Humidity
        self.humidity_title = QLabel("Humidity", self.weather_frame)
        self.humidity_title.setGeometry(0, 0, 150, 30)
        self.humidity_title.setFont(QFont("Monad", 14))
        
        self.humidity_value = QLabel("", self.weather_frame)
        self.humidity_value.setGeometry(0, 40, 150, 60) # Increased height for multiline
        self.humidity_value.setFont(QFont("Monad", 12))
        self.humidity_value.setWordWrap(True) # Allow word wrap
        
        # Rainfall
        self.rainfall_title = QLabel("Rainfall", self.weather_frame)
        self.rainfall_title.setGeometry(0, 140, 150, 30)
        self.rainfall_title.setFont(QFont("Monad", 12))
        
        self.rainfall_value = QLabel("", self.weather_frame)
        self.rainfall_value.setGeometry(0, 180, 150, 30)
        self.rainfall_value.setFont(QFont("Monad", 12))
        
        # Road Wetness & Temp
        self.road_title = QLabel("R. Wetness & Temp", self.weather_frame)
        self.road_title.setGeometry(0, 280, 220, 30)
        self.road_title.setFont(QFont("Monad", 12))

        self.road_value = QLabel("", self.weather_frame)
        self.road_value.setGeometry(0, 320, 180, 30)
        self.road_value.setFont(QFont("Monad", 12))
        
        # Tire Temp & Pressure
        self.tire_title = QLabel("T. Temp & Pressure", self.weather_frame)
        self.tire_title.setGeometry(0, 420, 220, 30)
        self.tire_title.setFont(QFont("Monad", 12))
        
        self.tire_value = QLabel("", self.weather_frame)
        self.tire_value.setGeometry(0, 460, 180, 30)
        self.tire_value.setFont(QFont("Monad", 12))

        # Traffic Light
        self.traffic_light = TrafficLightWidget(self)
        self.traffic_light.setGeometry(525, 40, 175, 175)

        # Braking Message
        self.braking_message = QLabel("BRAKES APPLIED AUTOMATICALLY",self)
        self.braking_message.setGeometry(450, 250, 450, 30) # Centered better
        self.braking_message.setFont(QFont("Monad", 14, QFont.Bold))
        self.braking_message.setAlignment(Qt.AlignCenter)
        self.braking_message.hide()
        
        # Allowing Message
        self.allowing_message = QLabel("LIGHT ALLOWS PASSAGE",self)
        self.allowing_message.setGeometry(450, 250, 450, 30) # Centered better
        self.allowing_message.setFont(QFont("Monad", 14, QFont.Bold))
        self.allowing_message.setAlignment(Qt.AlignCenter)
        self.allowing_message.hide()
        
        # Careful Message
        self.careful_message = QLabel("Be Ready to Brake",self)
        self.careful_message.setGeometry(450, 250, 450, 30) # Centered better
        self.careful_message.setFont(QFont("Monad", 14, QFont.Bold))
        self.careful_message.setAlignment(Qt.AlignCenter)
        # self.careful_message.hide() # Decide initial visibility

        
        # Speedometer
        self.speedometer = SpeedometerWidget(self)
        self.speedometer.setGeometry(350, 300, 500, 500)

    def sound_effect(self):
        """
        Plays the engine sound.
        Note: This method seems redundant as engine sound is played in `run_main_process`
        and managed elsewhere. Consider removing or integrating its logic if unique.
        """
        self.engine_sound.play()
        

class TrafficLightWidget(QFrame):
    """
    A custom widget to display a traffic light.

    The widget draws a circle that changes color (Red, Yellow, Green)
    based on the simulation's traffic light state. It includes a simple
    glow effect.

    Attributes:
        color (str): The current color of the traffic light ("Red", "Yellow", "Green").
    """
    def __init__(self, parent: QMainWindow = None): # More generic type hint for parent
        """
        Initializes the TrafficLightWidget.

        Args:
            parent (QMainWindow, optional): The parent widget. Defaults to None.
                                            It expects parent to have `light_color` if provided.
        """
        super().__init__(parent)
        self.color = parent.light_color if parent and hasattr(parent, 'light_color') else "Green" # Default color
        
    def set_color(self,color: str):
        """
        Sets the color of the traffic light and triggers a repaint.

        Args:
            color (str): The new color ("Red", "Yellow", or "Green").
        """
        self.color = color
        self.update() # Schedules a paint event
        
        
    def paintEvent(self, event: 'QPaintEvent'):
        """
        Handles the painting of the traffic light widget.

        Draws a colored circle with a glow effect corresponding to the
        current `self.color`.

        Args:
            event (QPaintEvent): The paint event.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw traffic light circle
        rect = self.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) / 2 - 5
        
        # Set color based on traffic light state
        if self.color == "Red":
            current_color = QColor(255, 0, 0) # Use local var
        elif self.color == "Yellow":
            current_color = QColor(255, 255, 0)
        else:  # Green or any other state
            current_color = QColor(0, 255, 0)
            
        # Create glow effect
        glow_gradient = QRadialGradient(center, radius * 1.5) # Adjusted glow radius
        glow_gradient.setColorAt(0, current_color.lighter(150)) # Center of glow
        glow_gradient.setColorAt(1, QColor(0,0,0,0)) # Transparent edge for glow

        painter.setBrush(QBrush(glow_gradient))
        painter.setPen(QPen(Qt.NoPen))
        painter.drawEllipse(center, radius * 1.5, radius * 1.5) # Draw larger glow ellipse

        # Traffic light main circle
        main_radius = min(rect.width(), rect.height()) / 2 - 20

        light_gradient = QRadialGradient(center, main_radius)
        light_gradient.setColorAt(0, current_color)
        light_gradient.setColorAt(0.9, current_color.darker(200)) # Darker edge
        light_gradient.setColorAt(1, current_color.darker(255))
                
        painter.setBrush(QBrush(light_gradient))
        painter.setPen(QPen(Qt.black,0.5))
        painter.drawEllipse(center, main_radius, main_radius)

class SpeedometerWidget(QFrame):
    """
    A custom widget to display a speedometer.

    Draws an analog speedometer with a needle, tick marks, numbers,
    and a central digital speed display. The appearance can adapt
    slightly based on the parent UI's theme mode (dark/light).

    Attributes:
            speed (float): The current speed to display in km/h.
            max_speed (int): The maximum speed value on the speedometer dial (km/h).
    """
    def __init__(self, parent: QMainWindow = None): # More generic type hint
        """
        Initializes the SpeedometerWidget.

        Args:
            parent (QMainWindow, optional): The parent widget. Defaults to None.
                                            Expects parent to have `car.speed_kmh` and `theme_mode`.
        """
        super().__init__(parent)
        self.speed = parent.car.speed_kmh if parent and hasattr(parent, 'car') and hasattr(parent.car, 'speed_kmh') else 0
        self.max_speed = 220

    def set_speed(self,speed: float):
        """
        Sets the speed to be displayed and triggers a repaint.

        Args:
            speed (float): The new speed value.
        """
        self.speed = speed
        self.update() # Schedules a paint event


    def paintEvent(self, event: 'QPaintEvent'):
        """
        Handles the painting of the speedometer widget.

        Draws the speedometer dial, tick marks, numbers, speed arc,
        and needle.

        Args:
            event (QPaintEvent): The paint event.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        rect = self.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) / 2 - 10
        
        # Draw speedometer background
        bg_gradient = QRadialGradient(center, radius)
        # Theme detection (assuming parent has 'theme_mode')
        parent_theme_mode = "light" # Default
        if hasattr(self.parent(), 'theme_mode'):
            parent_theme_mode = self.parent().theme_mode

        if parent_theme_mode == "dark":
            bg_gradient.setColorAt(0, QColor(40, 40, 40))
            bg_gradient.setColorAt(1, QColor(20, 20, 20))
            text_color = QColor(255, 255, 255)
        else: # Light theme
            bg_gradient.setColorAt(0, QColor(240, 240, 240))
            bg_gradient.setColorAt(1, QColor(220, 220, 220))
            text_color = QColor(0, 0, 0)
            
        painter.setBrush(QBrush(bg_gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, radius, radius)
        
        # Draw tick marks and numbers
        painter.setPen(QPen(text_color, 1))
        font_ticks = QFont("Monad", 10) # Renamed for clarity
        painter.setFont(font_ticks)
        
        # Tick drawing loop (corrected range for self.max_speed + 1)
        for i in range(0, self.max_speed + 2, 1): # Iterate up to max_speed for ticks
            if i > self.max_speed: continue # Don't draw beyond max_speed

            angle_deg = 120 + (i / self.max_speed * 300) # Degrees for drawing arc/lines
            rad_angle = math.radians(angle_deg) # Convert to radians for math functions
            
            current_pen_width = 1
            if i % 10 == 0:
                current_pen_width = 2
            painter.setPen(QPen(text_color, current_pen_width))

            # Tick mark lengths
            tick_length = 2
            if i % 10 == 0:
                tick_length = 15
            elif i % 5 == 0:
                tick_length = 10

            outer_x = center.x() + (radius - 10) * math.cos(rad_angle) # Adjusted for padding
            outer_y = center.y() + (radius - 10) * math.sin(rad_angle)
            inner_x = center.x() + (radius - 10 - tick_length) * math.cos(rad_angle)
            inner_y = center.y() + (radius - 10 - tick_length) * math.sin(rad_angle)
            
            painter.drawLine(QPointF(inner_x, inner_y), QPointF(outer_x, outer_y))

            if i % 10 == 0: # Number labels
                font_numbers = QFont("Monad", 10)  # Font for numbers
                painter.setFont(font_numbers) # Set font for drawing text
                text_radius = radius - 35 # Adjusted for better placement
                text_x = center.x() + text_radius * math.cos(rad_angle)
                text_y = center.y() + text_radius * math.sin(rad_angle)
                
                fm = QFontMetrics(font_numbers)
                text_width = fm.horizontalAdvance(str(i))
                # text_height = fm.height() # Not directly needed for centered text here
                
                painter.drawText(
                    int(round(text_x - text_width / 2)),
                    int(round(text_y + fm.ascent() / 2 - fm.descent())), # Better vertical centering
                    str(i)
                )
                painter.setFont(font_ticks) # Reset font for ticks
        
        # Draw speed value in the center
        font_speed_digital = QFont("Monad", 36, QFont.Bold)
        painter.setFont(font_speed_digital)
        speed_text = f"{int(self.speed)}"
        
        fm_speed_digital = QFontMetrics(font_speed_digital)
        text_width_digital = fm_speed_digital.horizontalAdvance(speed_text)
        
        painter.setPen(text_color) # Ensure text color is set for digital speed
        painter.drawText(
            int(round(center.x() - text_width_digital / 2)), # Use center.x()
            int(round(center.y() + fm_speed_digital.ascent() / 2 - fm_speed_digital.descent() + 50)), # Adjusted y
            speed_text
        )
        
        # Draw "km/h" text
        font_unit = QFont("Monad", 12)
        painter.setFont(font_unit)
        unit_text = "km/h"
        
        fm_unit = QFontMetrics(font_unit)
        text_width_unit = fm_unit.horizontalAdvance(unit_text)
        
        painter.drawText(
            int(round(center.x() - text_width_unit / 2)),
            int(round(center.y() + fm_speed_digital.height() / 2 + fm_unit.height() + 40)), # Adjusted y
            unit_text
        )

        # Draw speedometer arc (progress bar style)
        arc_gradient = QRadialGradient(center, radius)
        arc_gradient.setColorAt(0, QColor(254, 147, 4, 255))  # Bright center

        pen_arc = QPen(arc_gradient, 8)
        pen_arc.setCapStyle(Qt.RoundCap)
        painter.setPen(pen_arc)
        
        # Span angle calculation: 0 speed = 0 angle, max_speed = 300 degrees span
        # Start angle for arc is -120 degrees from positive x-axis (pointing left-up)
        # Qt's drawArc angles: 0 is 3 o'clock, positive is counter-clockwise.
        # Speedometer: 0 km/h at 240 deg, 220 km/h at -60 deg (or 300 deg)
        # Start angle for Qt arc: 240 degrees. Span: -300 degrees for full scale.
        start_angle_qt = 240 * 16 # Qt uses 1/16th of a degree
        span_angle_deg = min(self.speed / self.max_speed, 1.0) * 300
        span_angle_qt = int(-span_angle_deg * 16) # Negative for clockwise fill
        
        painter.drawArc(
            int(center.x() - (radius - 5)), # Slightly inset arc
            int(center.y() - (radius - 5)),
            int((radius - 5) * 2),
            int((radius - 5) * 2),
            start_angle_qt,
            span_angle_qt
        )

        # Draw the shining point at the end of the arc
        # Angle calculation for the end of the arc
        end_angle_deg_map = 240 - span_angle_deg # Mapping to geometric angle
        rad_end_angle = math.radians(end_angle_deg_map)

        # Point on the arc radius
        point_radius = radius - 5 # Same radius as arc
        end_x = center.x() + point_radius * math.cos(rad_end_angle)
        end_y = center.y() + point_radius * math.sin(rad_end_angle) # math.sin uses standard angles

        shine_gradient = QRadialGradient(QPointF(end_x, end_y), 10) # Gradient centered on point
        shine_gradient.setColorAt(0, QColor(255, 255, 255, 200))
        shine_gradient.setColorAt(1, QColor(255, 235, 89, 0))
        
        painter.setBrush(QBrush(shine_gradient))
        painter.setPen(Qt.NoPen) # No border for the shine
        painter.drawEllipse(QPointF(end_x, end_y), 7, 7)  # Adjust size as needed
        
        # Draw needle
        painter.save()
        painter.translate(center)
        # Needle rotation: starts at 240 deg for 0 km/h.
        # Rotates clockwise. Max rotation of 300 deg for max_speed.
        needle_angle_deg = 240 + (self.speed / self.max_speed * 300)
        painter.rotate(needle_angle_deg - 90) # Qt rotation, -90 because needle points 'up' initially
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(255, 0, 0, 200))) # Semi-transparent red
        
        # Needle shape (simple rectangle)
        # Adjusted to be thinner and start from center
        needle_rect = QRect(-2, -10, 4, int(radius - 25))  # x, y, width, height
        painter.drawRoundedRect(needle_rect, 2, 2) # Rounded ends
        
        # Draw the needle pivot
        pivot_color = QColor(100,100,100) if parent_theme_mode == "dark" else QColor(50,50,50)
        painter.setBrush(QBrush(pivot_color))
        painter.drawEllipse(QRectF(-10, -10, 20, 20)) # Centered pivot
        
        painter.restore()

class light_operations:
    """
    Handles the logic related to traffic light interactions and braking decisions.

    This class simulates the vehicle's approach to a traffic light,
    determines if braking is necessary based on light color, distance,
    and calculated braking/stopping distances. It interacts with the `Vehicle`
    object to apply brakes if needed and updates the UI instance with status.

    Attributes:
            trafficLight (classes.TrafficLight): An instance of the `TrafficLight` class.
        light_color (str): The current detected color of the traffic light.
            changed_light_color (str): The color the light might change to after a potential change.
            car ('classes.Vehicle'): The vehicle object being controlled.
            ui_inst (AutoBrakeSystemUI): The instance of the UI to update with messages or state changes.
            light_distance (float): Current distance to the traffic light in meters.
            to_stop (bool): Flag indicating if the system has determined the vehicle should prepare to stop.
            to_brake (bool): Flag indicating if autonomous braking should be actively engaged.
            brake_distance (float): Calculated brake distance required for the current conditions.
    """
    def __init__(self, vehicle: 'classes.Vehicle', ui_inst: 'AutoBrakeSystemUI'):
        """
        Initializes the light_operations class.

        Args:
            vehicle ('classes.Vehicle'): The vehicle object.
            ui_inst ('AutoBrakeSystemUI'): The UI instance for updates.
        """
        self.trafficLight = classes.TrafficLight()
        self.light_color = "" # Will be set by self.trafficLight.generation() in light()
        self.changed_light_color="" # Will be set if light changes
        self.car = vehicle
        self.ui_inst = ui_inst
        self.light_distance = self.trafficLight.distance # Initial distance
        self.to_stop = False # Should the car prepare to stop?
        self.to_brake = False # Should autonomous braking be active?
        self.brake_distance = 0 # Calculated brake distance
        
    
    def light_iterator(self,light_color: str) -> str:
        """
        Determines the next color in a typical traffic light sequence.

        Given a current light color, it returns the next color in the
        Green -> Yellow -> Red -> Yellow -> Green ... cycle.

        Args:
            light_color (str): The current color of the traffic light.

        Returns:
            str: The next color in the sequence. Returns current color if not found.
        """
        light_conditions = ["Green","Yellow","Red","Yellow"] # Note: Yellow appears twice
        try:
            current_index = light_conditions.index(light_color)
            # Special handling for the second yellow to loop back to green
            if light_color == "Yellow" and current_index == 3: # Second yellow
                 return "Green" # Assuming Yellow -> Green after Red -> Yellow
            # Need to refine this logic if the sequence is strictly G->Y->R->Y...
            # If current is "Red", next is "Yellow" (index 3 of light_conditions)
            # If current is "Yellow" (index 1, after Green), next is "Red"
            # If current is "Yellow" (index 3, after Red), next is "Green"

            # Simplified logic for now, assuming a simple cycle:
            if light_color == "Green": return "Yellow"
            if light_color == "Yellow": return "Red" # This is ambiguous. Which Yellow?
            if light_color == "Red": return "Yellow" # This yellow should lead to Green

            # More robust:
            # This assumes the sequence is Green -> Yellow (1) -> Red -> Yellow (2) -> Green
            if light_color == "Green":
                return "Yellow" # Yellow (1)
            elif light_color == "Yellow":
                # This requires knowing context (was previous Green or Red?)
                # For simulation, let's assume if current is Yellow, it's on its way to Red.
                # The actual change logic in `light()` needs to be clear about which yellow it is.
                # The `self.trafficLight.color_change()` and `self.light_iterator`
                # interaction implies `light_iterator` is called *after* a change.
                # So if `light_color` was "Green" and it changed, `changed_light_color` becomes "Yellow".
                # If `light_color` was "Red" and it changed, `changed_light_color` becomes "Yellow".
                # This method might be too simplistic for the double-yellow sequence.
                # However, based on its usage in `light()`, it's called with the *original* light_color.
                idx = light_conditions.index(light_color)
                if idx == 0: return "Yellow" # Green -> Yellow
                if idx == 1: return "Red"    # Yellow (after Green) -> Red
                if idx == 2: return "Yellow" # Red -> Yellow
                if idx == 3: return "Green"  # Yellow (after Red) -> Green

        except ValueError:
            return light_color # Should not happen with valid colors
        return light_conditions[(light_conditions.index(light_color) + 1) % len(light_conditions)]


    def light(self):
        """
        Manages the primary logic for approaching and reacting to a traffic light.

        This method simulates:
        1. Detecting the initial light color and distance.
        2. Calculating necessary braking and stopping distances.
        3. Simulating approach: Loop while distance is greater than stopping distance + buffer.
        4. Checking for light color changes during approach.
        5. Making a decision to brake or proceed based on the final light color,
           distance, and vehicle's ability to stop safely.
        6. Updates UI flags (`to_stop`, `to_brake`) and initiates braking on the
           `car` object if necessary.
        """
        
        self.light_color = self.trafficLight.generation() # Get initial light color
        self.ui_inst.traffic_light.set_color(self.light_color) # Update UI
        
        print(f"Light Detected at: {self.trafficLight.distance}m = {self.light_color.upper()}")
        
        # After light detected, get sensor data for calculations
        sensors = classes.Sensors(self.car.speed_kmh)
        sensors_data = sensors.generation()
        self.car.generate(sensors_data) # Vehicle processes sensor data
        self.brake_distance = self.car.collected_data["brake_distance"]
        stopping_distance = self.car.collected_data["stopping_distance"]

        print(f"Calculated Brake Distance: {self.brake_distance} m")
        print(f"Calculated Stopping Distance (includes reaction): {stopping_distance} m")

        # Simulate approaching the light
        # Loop while current distance to light is greater than calculated stopping distance + a safety buffer (e.g., 80m)
        # This loop simulates the car moving closer to the light before a final decision point.
        buffer_distance = 30 # Safety buffer / decision point distance from stopping_distance
        while self.light_distance > stopping_distance + buffer_distance :
            # time.sleep(0.1) # Simulate time passing - BE CAREFUL with sleep in UI-affecting threads
            self.light_distance_cal() # Update distance based on car speed
            if self.light_color == "Red" or (self.light_color == "Yellow" and self.car.speed_kmh > 10): # Consider stopping for yellow if not too close/fast
                self.to_stop = True # Indication to UI to show "Time to brake"
                self.ui_inst.careful_message.setText("Prepare to Stop!")
                self.ui_inst.careful_message.show()
            else:
                self.to_stop = False
                self.ui_inst.careful_message.hide()

            print(f"Approaching light. Distance to Light: {self.light_distance:.2f} m, Speed: {self.car.speed_kmh:.2f} km/h")
            if self.light_distance <= 0: break # Passed the light or at it

        print(f"Reached decision point. Distance: {self.light_distance:.2f}m")
        
        # Check if the light changes as the car is near the decision point
        if self.trafficLight.color_change(): # Simulates a potential color change
            newly_changed_color = self.light_iterator(self.light_color) # Get what it would change to
            print(f"LIGHT HAS CHANGED FROM {self.light_color} TO {newly_changed_color}")
            self.changed_light_color = newly_changed_color # Store this changed color
            self.ui_inst.traffic_light.set_color(self.changed_light_color)
        else: 
            self.changed_light_color = self.light_color # No change, proceed with current color

        final_decision_color = self.changed_light_color # Color to use for final decision

        # Recalculate distances one last time if speed could have changed, though not explicitly modeled here
        self.light_distance_cal()
        print(f"Final check. Distance: {self.light_distance:.2f}m. Light: {final_decision_color}")

        # Decision logic:
        if self.brake_distance < self.light_distance: # Can we physically stop before the light?
            if final_decision_color == "Red":
                print("Decision: RED light. Initiating stop.")
                self.to_stop = True
                self.to_brake = True # Engage auto-brake
                self.car.brake(time.time(), self.light_distance) # Pass current time and distance
            
            elif final_decision_color == "Yellow":
                # Yellow light logic: stop if safe, proceed if too close/fast to stop safely
                # This threshold needs careful tuning. Example: stop if stopping_distance < light_distance + small_buffer
                if stopping_distance < self.light_distance + 10: # Can stop comfortably for yellow
                    print("Decision: YELLOW light. Initiating stop (safe to do so).")
                    self.to_stop = True
                    self.to_brake = True
                    self.car.brake(time.time(),self.light_distance)
                else: # Unsafe to stop for yellow (would brake too hard or stop in intersection)
                    print("Decision: YELLOW light. Proceeding (unsafe to stop).")
                    self.ui_inst.careful_message.setText("Proceed with Caution (Yellow)")
                    self.ui_inst.careful_message.show()
                    self.ui_inst.allowing_message.hide()
                    self.ui_inst.time_to_brake_label.hide()
                    self.ui_inst.time_to_brake_value.hide()
                    self.to_stop = False
                    self.to_brake = False
           
            elif final_decision_color == "Green":
                print("Decision: GREEN light. Proceeding.")
                self.ui_inst.careful_message.hide()
                self.ui_inst.allowing_message.setText("GREEN LIGHT - PROCEED")
                self.ui_inst.allowing_message.show()
                self.ui_inst.time_to_brake_label.hide()
                self.ui_inst.time_to_brake_value.hide()
                self.to_stop = False
                self.to_brake = False
        else: # Cannot stop before the light (brake_distance >= light_distance)
            print(f"Vehicle is unsafe to stop (BrakeDist {self.brake_distance:.2f}m >= LightDist {self.light_distance:.2f}m). Proceeding through {final_decision_color} light.")
            self.ui_inst.careful_message.setText(f"UNABLE TO STOP SAFELY FOR {final_decision_color.upper()} LIGHT")
            self.ui_inst.careful_message.show()
            self.to_stop = False
            self.to_brake = False
            # If it's a red light and we can't stop, this is a failure scenario. Log it.
            if final_decision_color == "Red":
                print("CRITICAL: Ran a red light because unable to stop in time.")
                # Potentially trigger a more severe warning in UI or log.

    def light_distance_cal(self) -> float:
        """
        Calculates and updates the vehicle's current distance to the traffic light.

        This method calls `self.trafficLight.distance_to_light()` which typically
        decrements the distance based on the car's speed and elapsed time.

        Returns:
            float: The updated distance to the light in meters.
        """
        self.light_distance = self.trafficLight.distance_to_light(self.car.speed_ms)
        return self.light_distance
    
    def time_to_intervene_cal(self) -> int:
        """
        Calculates the estimated time left for the driver to intervene (brake)
        before the vehicle reaches a point where autonomous braking might engage
        or before reaching the traffic light if already braking.

        The calculation is `(current_light_distance - required_brake_distance) / current_speed`.

        Returns:
            int: Rounded time in seconds for intervention. Returns 0 if speed is zero
                 or if calculated time is negative.
        """
        try:
            # Time until car reaches the point where it *must* start braking to stop in time.
            time_val = (self.light_distance - self.brake_distance) / self.car.speed_ms
            if time_val < 0: return 0 # Already past the ideal braking point or very close
        except ZeroDivisionError: # Speed is zero
            time_val = 0 # Or a large number if distance > brake_distance, but 0 is safer if stopped.
        return round(time_val)
              


        
