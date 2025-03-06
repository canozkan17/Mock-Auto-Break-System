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

    def __init__(self,vehicle:object,database:object): 

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
        self.current_speed = 0
        self.brake_countdown = 0
        self.light_color = ""
        self.is_blurred = False
        self.key = ""

        self.start = time.time()
        self.end = 0


        # Initialize data display labels
        self.init_ui()


        # Initialize master key for encryption and decryption of data
        connection = sqlite3.connect("Loggs.db")
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT * FROM user_master_key")
            self.key = cursor.fetchone()[0]

        except sqlite3.OperationalError:
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
        self.braking_sound.setLoopCount(QSoundEffect.Infinite)
        self.braking_sound.setVolume(0.5)
        
        # Start data update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1)  # Update every 1ms
        
        # Start the main processing in a separate thread
        self.processing_thread = threading.Thread(target=self.run_main_process)
        #self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def master_key(self):

        #self.timer.stop()
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
        else:
            sys.exit()

        #self.timer.start(1)
        
    def run_main_process(self):
        self.engine_sound.play()
        self.light_operations_inst.light()
        

    def update_display (self):
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
        self.light_operations_inst.light_distance_cal()

        time_to_intervene = self.light_operations_inst.time_to_intervene_cal()

        if self.light_operations_inst.changed_light_color != "":
            self.light_color = self.light_operations_inst.changed_light_color   

        else:
            self.light_color = self.light_operations_inst.light_color 
        

        if self.light_operations_inst.to_stop == True:
            self.time_to_brake_label.show()
            if time_to_intervene <= 0:
                self.time_to_brake_value.setText("0")  
            else:
                self.time_to_brake_value.setText(str(time_to_intervene))  
        
        
        if self.light_operations_inst.to_brake == True:
            self.time_to_brake_label.setText("Auto Brake in")
            self.time_to_brake_value.setFont(QFont("Monad", 15))

        if self.car.user_brake_applied == True:
            self.braking_message.setText("BRAKES APPLIED BY DRIVER")
            self.careful_message.hide()
            self.braking_message.show()
            self.engine_sound.stop()
            if self.braking_sound.isPlaying() == False:
                self.braking_sound.play()

        if self.car.auto_brake_applied == True:
                self.careful_message.hide()
                self.braking_message.show()
                self.engine_sound.stop()
                if self.braking_sound.isPlaying() == False:
                    self.braking_sound.play()

            
            
        

        
                                

        self.traffic_light.set_color(self.light_color) 


        if self.light_operations_inst.light_distance < 0:
            self.braking_sound.stop()
            self.end = time.time()
            print(self.end - self.start)
            print(f"self.light_color {self.light_color}")
            print(f"self.light_operations_inst.light_color {self.light_operations_inst.light_color}")
            print(f"self.light_operations_inst.changed_light_color {self.light_operations_inst.changed_light_color}")
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle('Continue ?')
            msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg_box.setDefaultButton(QMessageBox.Ok)
            msg_box.setMinimumSize(400, 200)
            if msg_box.exec_() == QMessageBox.Ok:
                self.toggle_run_again()
            else:
                # Encrypting the run before exiting
                DES_Encryption_Decryption().Encrypt_to_db(self.car, self.key)
                self.db.insert_db(self.car.collected_data)
                sys.exit()

    def toggle_run_again(self):
        # Encrypting the previous run before proceeding to the next. 
        DES_Encryption_Decryption().Encrypt_to_db(self.car, self.key)
        self.db.insert_db(self.car.collected_data)
        
        QApplication.quit()
        # Restart the program
        QProcess.startDetached(sys.executable, sys.argv)        

    def toggle_admin_mode(self):
        
        self.timer.stop()
        
        dialog = QInputDialog(self)
        dialog.setWindowTitle('Enter your Master Key Below:')
        dialog.setLabelText('Enter your text:')
        dialog.resize(400, 200)      

        ok = dialog.exec_()
        if ok:
            self.key = dialog.textValue()
            try:
                connection = sqlite3.connect("Loggs.db")
                cursor = connection.cursor()
                
                cursor.execute("SELECT * FROM user_master_key")
                result = cursor.fetchone()[0]
                
                if result == self.key:

                    DES_Encryption_Decryption().Decrypt_from_db(self.db,self.key)
                    command = 'start cmd /k "python -c ^"from DB_class import DataBase; DataBase().read_from_db()^" "'
                    subprocess.Popen(command, shell=True)

                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("Want to Reset Decryptions ? ")
                    msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                    msg_box.setDefaultButton(QMessageBox.Ok)
                    msg_box.setMinimumSize(400, 200)
                    if msg_box.exec_() == QMessageBox.Ok:
                        cursor.execute("DROP TABLE IF EXISTS user_master_key")
                        cursor.execute("DROP TABLE IF EXISTS decrypted_data")
                    
            except:
                print("Cannot Access DATABASE")
                sys.exit()
                
        self.timer.start(1)

    def update_theme(self):
        # Detect system theme using QPalette
        app = QApplication.instance()
        palette = app.palette()

        # Check if background color is dark or light

        self.setStyleSheet("""
            QMainWindow { background-color: #121212; color: white; }
            QLabel { color: white; }
            QPushButton { background-color: #3D4956; color: white; border-radius: 5px; padding: 10px; }
            QPushButton:hover { background-color: #4D5966; }
        """)
        self.theme_mode = "dark"
        
    def init_ui(self):
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

        self.light_distance_value = QLabel("200 m", self)
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
        self.time_to_brake_label.hide()

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
        self.run_button = QPushButton("Run Again MODE", self)
        self.run_button.setGeometry(940, 630, 220, 50)
        self.run_button.setFont(QFont("Monad", 12, QFont.Bold))
        self.run_button.clicked.connect(self.toggle_run_again)

        # Weather Info Frame
        self.weather_frame = QFrame(self)
        self.weather_frame.setGeometry(30, 250, 400, 500)
        
        # Humidity
        self.humidity_title = QLabel("Humidity", self.weather_frame)
        self.humidity_title.setGeometry(0, 0, 150, 30)
        self.humidity_title.setFont(QFont("Monad", 14))
        
        self.humidity_value = QLabel("", self.weather_frame)
        self.humidity_value.setGeometry(0, 40, 150, 60)
        self.humidity_value.setFont(QFont("Monad", 12))
        
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
        self.braking_message.setGeometry(450, 250, 450, 30)
        self.braking_message.setFont(QFont("Monad", 14, QFont.Bold))
        self.braking_message.hide()
        
        # Allowing Message
        self.allowing_message = QLabel("LIGHT ALLOWS PASSAGE",self)
        self.allowing_message.setGeometry(450, 250, 450, 30)
        self.allowing_message.setFont(QFont("Monad", 14, QFont.Bold))
        self.allowing_message.hide()
        
        # Carefull Message
        self.careful_message = QLabel("Be Ready to Break",self)
        self.careful_message.setGeometry(475, 250, 450, 30)
        self.careful_message.setFont(QFont("Monad", 14, QFont.Bold))

        
        # Speedometer
        self.speedometer = SpeedometerWidget(self)
        self.speedometer.setGeometry(350, 300, 500, 500)

    def sound_effect(self):
        self.engine_sound.play()
        

class TrafficLightWidget(QFrame):
    def __init__(self, parent=AutoBrakeSystemUI):
        super().__init__(parent)
        self.color = parent.light_color
        
    def set_color(self,color):
        self.color = color
        self.update()
        
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw traffic light circle
        rect = self.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) / 2 - 5
        
        # Set color based on traffic light state
        if self.color == "Red":
            color = QColor(255, 0, 0)
        elif self.color == "Yellow":
            color = QColor(255, 255, 0)
        else:  # Green
            color = QColor(0, 255, 0)
            
        # Create glow effect
        glow = QRadialGradient(center, radius * 2.5)
        glow.setColorAt(1, color.lighter(50))

        painter.setBrush(QBrush(glow))
        painter.setPen(QPen(Qt.NoPen))
        painter.drawEllipse(center, radius,radius)

        # Traffic light
        radius = min(rect.width(), rect.height()) / 2 - 20

        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0, color)
        gradient.setColorAt(0.9, color.darker(255))
                
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(Qt.black,0.5))
        painter.drawEllipse(center, radius, radius)

class SpeedometerWidget(QFrame):
    def __init__(self, parent=AutoBrakeSystemUI):
        super().__init__(parent)
        self.speed = parent.car.speed_kmh
        self.max_speed = 220

    def set_speed(self,speed):
        self.speed = speed
        self.update()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        rect = self.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) / 2 - 10
        
        # Draw speedometer background
        gradient = QRadialGradient(center, radius)
        if hasattr(self.parent(), 'theme_mode') and self.parent().theme_mode == "dark":
            gradient.setColorAt(0, QColor(40, 40, 40))
            gradient.setColorAt(1, QColor(20, 20, 20))
            text_color = QColor(255, 255, 255)
        else:
            gradient.setColorAt(0, QColor(240, 240, 240))
            gradient.setColorAt(1, QColor(220, 220, 220))
            text_color = QColor(0, 0, 0)
            
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, radius, radius)
        
        # Draw tick marks and numbers
        painter.setPen(QPen(text_color, 1))
        font = QFont("Monad", 10)
        painter.setFont(font)
        
        for i in range(0, self.max_speed + 1):
            angle = 120 + (i / self.max_speed * 300)
            rad_angle = angle * 3.14159 / 180
            
            if i % 10 == 0:
                painter.setPen(QPen(text_color, 2))
            else:
                painter.setPen(QPen(text_color, 1))

            # Major tick marks
            outer_x = center.x() + radius * math.cos(rad_angle)
            outer_y = center.y() + radius * math.sin(rad_angle)
            
            # Determining the tick mark lenght
            if i % 10 == 0:
                tick_length = 15
            elif i % 5 == 0:
                tick_length = 10
            else:
                tick_length = 2 

            # Adjust inner coordinates based on tick mark length
            inner_x = center.x() + (radius - tick_length - 10) * math.cos(rad_angle)
            inner_y = center.y() + (radius - tick_length - 10) * math.sin(rad_angle)
            
            painter.drawLine(int(inner_x), int(inner_y), int(outer_x), int(outer_y))

            if i % 10 == 0:
                font = QFont("Monad", 10)  # Larger font for multiples of 20
                # Draw numbers
                text_radius = radius - 40
                text_x = center.x() + text_radius * math.cos(rad_angle)
                text_y = center.y() + text_radius * math.sin(rad_angle)
                
                fm = QFontMetrics(font)
                text_width = fm.horizontalAdvance(str(i))
                text_height = fm.height()
                
                painter.drawText(
                int(round(text_x - text_width / 2)),  # Ensuring an integer value
                int(round(text_y + text_height / 2)),  # Ensuring an integer value
                str(i)
                )
        
        # Draw speed value in the center
        font = QFont("Monad", 36, QFont.Bold)
        painter.setFont(font)
        speed_text = f"{int(self.speed)}"
        
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(speed_text)
        text_height = fm.height()
        
        painter.drawText(
            round(250 - text_width / 2),
            round(350 + text_height / 4),
            speed_text
        )
        
        # Draw "km/h" text
        font = QFont("Monad", 12)
        painter.setFont(font)
        unit_text = "km/h"
        
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(unit_text)
        
        painter.drawText(
            round(center.x() - text_width / 2),
            400,
            unit_text
        )

        # Draw speedometer arc
        # Create a radial gradient
        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0, QColor(254, 147, 4, 255))  # Bright center

        pen = QPen(gradient, 8)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        span_angle = min(self.speed / self.max_speed * 300, 300)
        
        # Draw the main arc
        painter.drawArc(
            int(center.x() - radius),
            int(center.y() - radius),
            int(radius * 2),
            int(radius * 2),
            240 * 16,
            int(-span_angle * 16)
        )

        # Draw the shining point at the end of the arc
        end_angle = 240 - span_angle
        rad_end_angle = end_angle * math.pi / 180
        end_x = center.x() + radius * math.cos(rad_end_angle)
        end_y = center.y() - radius * math.sin(rad_end_angle)

        gradient = QRadialGradient(center, radius - 10 )
        gradient.setColorAt(0.01, QColor(255, 255, 255, 150))  # Bright center
        pen = QPen(gradient, 3)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        # Create the bright point at the end
        painter.setBrush(QColor(255, 235, 89, 100))  # Bright color
        painter.drawEllipse(QPointF(end_x, end_y), 5, 5)  # Adjust size as needed
        
        # Draw needle
        painter.save()
        painter.translate(center)
        painter.rotate(210 + (self.speed * 1.376))
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(255, 0, 0)))
        
        needle = QRect(-5, int(-radius + 20), 2, int(radius - 40))  
        painter.drawRect(needle)
        
        # Draw the needle pivot
        painter.setBrush(QBrush(QColor(100, 100, 100)))
        painter.drawEllipse(-10, -10, 20, 20)
        
        painter.restore()

class light_operations:   
    def __init__(self, vehicle: object, ui_inst: AutoBrakeSystemUI):
        self.trafficLight = classes.TrafficLight()
        self.light_color = ""
        self.changed_light_color=""
        self.car = vehicle
        self.ui_inst = ui_inst
        self.light_distance = self.trafficLight.distance
        self.to_stop = False
        self.to_brake = False
        self.brake_distance = 0
        
    
    def light_iterator(self,light_color):
        light_conditions = ["Green","Yellow","Red","Yellow"]
        i = light_conditions.index(light_color)
        enumared_light = list(enumerate(light_conditions))
        return enumared_light[i+1][1]

    def light(self):
        # the light has been detected,
        # color identified, 
        # time taken when the trafficlight object created.  
        
        self.light_color = self.trafficLight.generation()
        
        print(f"Light Detected in: {self.trafficLight.distance} = {self.light_color.upper()}")


        
        # after light detected the sensors are called for brake distance & stopping distance (driver interference added) calculation
        sensors = classes.Sensors(self.car.speed_kmh)
        sensors_data = sensors.generation()
        self.car.generate(sensors_data)
        self.brake_distance = self.car.collected_data["brake_distance"]
        stopping_distance = self.car.collected_data["stopping_distance"]

        print(f"Brake Distance: {self.brake_distance} m")
        print(f"Stopping Distance: {stopping_distance} m")

        # waiting to approach to the light   
        while self.light_distance > stopping_distance + 80:
            #time.sleep(1)
            self.light_distance_cal()
            if self.light_color == "Red" or self.light_color == "Yellow":
                self.to_stop = True
            print(f"Distance to Light: {self.light_distance} m")
        
        
        
        #checking if the light will change
        if self.trafficLight.color_change() == True:
            self.changed_light_color = self.light_iterator(self.light_color)
            print(f"LIGHT HAS CHANGED TO {self.changed_light_color}")
        else: 
            self.changed_light_color = self.light_color

        # getting the light distance for light color decision making
        self.light_distance_cal()
        print(f"Distance to Light: {self.light_distance} m")

        if self.brake_distance < self.light_distance:
            if self.changed_light_color == "Red":
                start_time = int(time.time())
                time_to_intervene = self.time_to_intervene_cal()

                print(f"Time left for braking: {time_to_intervene}")

                self.to_stop = True
                self.to_brake= True
                self.car.brake(start_time,self.light_distance)
            
            elif self.changed_light_color == "Yellow":
                
                if self.light_color == "Red" or self.light_color == "Yellow":
                    print("Yellow Light Allows Passage")
                    self.ui_inst.careful_message.hide()
                    self.ui_inst.allowing_message.show()
                    self.ui_inst.time_to_brake_label.hide()
                    self.ui_inst.time_to_brake_value.hide()
                    self.to_stop = False
                    self.to_brake = False
               
                elif self.light_color == "Green":
                    start_time = int(time.time())
                    time_to_intervene = self.time_to_intervene_cal()

                    print(f"Time left for braking: {time_to_intervene}")

                    self.to_stop = True
                    self.to_brake= True
                    self.car.brake(start_time,self.light_distance)
           
            elif self.changed_light_color == "Green":
                print("Light Allows Passage")
                self.ui_inst.careful_message.hide()
                self.ui_inst.allowing_message.show()
                self.ui_inst.time_to_brake_label.hide()
                self.ui_inst.time_to_brake_value.hide()
                self.to_stop = False
                self.to_brake = False

        elif self.brake_distance >= self.light_distance:
            print("Vehicle is unsafe to stop, passing")
            self.to_stop = False
            self.to_brake = False

    def light_distance_cal(self):
        self.light_distance = self.trafficLight.distance_to_light(self.car.speed_ms)
        return self.light_distance
    
    def time_to_intervene_cal(self):
        try:
            time_to_intervene = (self.trafficLight.distance - self.brake_distance) / self.car.speed_ms
        except ZeroDivisionError:
            time_to_intervene = 0
        return round(time_to_intervene)
              


        
