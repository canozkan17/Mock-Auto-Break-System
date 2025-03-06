import classes
import time
import keyboard
from PyQt5.QtCore import pyqtSignal,QObject


class Light_Detection(QObject):
    light_distance_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.light_color = ""
        self.changed_light_color = ""

    def light_iterator(self,light_color):
        light_conditions = ["Green","Yellow","Red","Yellow"]
        i = light_conditions.index(light_color)
        enumared_light = list(enumerate(light_conditions))
        return enumared_light[i+1][1]

    def light(self,car):

        # the light has been detected,
        # color identified, 
        # time taken. 
        trafficLight = classes.TrafficLight()
        self.light_color = trafficLight.generation()
        light_detection_time = int(time.time())
        print(f"Light Detected in: {trafficLight.distance} = {self.light_color.upper()}")
        self.light_distance_signal.emit(trafficLight.distance)
        

        # after light detected the sensors are called for brake distance & stopping distance (driver interference added) calculation
        sensors = classes.Sensors(car.speed_kmh)
        sensors_data = sensors.generation()
        car.generate(sensors_data)
        brake_distance = car.collected_data["brake_distance"]
        stopping_distance = car.collected_data["stopping_distance"]

        print(f"Brake Distance: {brake_distance} m")
        print(f"Stopping Distance: {stopping_distance} m")

        
        light_distance = trafficLight.distance_to_light(car.speed_ms, light_detection_time)
        #print(f"Distance to Light: {light_distance} m")


        # waiting to approach to the light   
        while light_distance > stopping_distance + 50:
            light_detection_time = int(time.time())
            #time.sleep(1)
            light_distance = trafficLight.distance_to_light(car.speed_ms, light_detection_time)
            if self.light_color == "Red" or self.light_color == "Yellow":
                stopping_time = trafficLight.time_to_light(car.speed_ms,light_distance)
                self.light_distance_signal.emit(trafficLight.distance)
                #print(f"Distance to Light: {light_distance} m, Time to Break: {stopping_time}")

            else:
                print(f"Distance to Light: {light_distance} m")
                self.light_distance_signal.emit(trafficLight.distance)
        
        
        #checking if the light will change
        if trafficLight.color_change() == True:
            self.changed_light_color = self.light_iterator(self.light_color)
            print(f"LIGHT HAS CHANGED TO {self.changed_light_color}")
        else: 
            self.changed_light_color = self.light_color

        # getting the light distance for light color decision making
        light_detection_time = int(time.time())
        light_distance = trafficLight.distance_to_light(car.speed_ms, light_detection_time)

        if brake_distance < light_distance:

            if self.changed_light_color == "Red":
                start_time = int(time.time())
                time_to_intervene = (trafficLight.distance - brake_distance) / car.speed_ms
                print(f"Time left for braking: {round(time_to_intervene)}")

                light_distance = trafficLight.distance_to_light(car.speed_ms, light_detection_time)
                print(f"Distance to Light: {light_distance} m")
                self.light_distance_signal.emit(trafficLight.distance)

                car.brake(start_time,light_distance)
            elif self.changed_light_color == "Yellow":
                if self.light_color == "Red" or self.light_color == "Yellow":
                    print("Yellow Light Allows Passage")
                elif self.light_color == "Green":
                    start_time = int(time.time())
                    time_to_intervene = (trafficLight.distance - brake_distance) / car.speed_ms
                    print(f"Time left for braking: {round(time_to_intervene)}")

                    light_distance = trafficLight.distance_to_light(car.speed_ms, light_detection_time)
                    print(f"Distance to Light: {light_distance} m")
                    self.light_distance_signal.emit(trafficLight.distance)

                    car.brake(start_time,light_distance)
            elif self.changed_light_color == "Green":
                print("Light Allows Passage")

        elif brake_distance >= light_distance:
            print("Vehicle is unsafe to stop, passing")


