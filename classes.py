import random
import time
import keyboard
import datetime

generated_data = {}

class Humidity:

    def __init__(self):
        self.humidity = random.randint(0,100)
        self.sit = None
    
    def situation(self):
        generated_data.update({"humidity": self.humidity})
        humidity = self.humidity
        sit = self.sit
        if humidity <= 25:
            sit =  "Very Dry"
        elif humidity > 25 and humidity <=55:
            sit =  "Medium"
        elif humidity > 55 and humidity <=75:
            sit =  "Humid"   
        elif humidity > 75:
            sit =  "Very Humid"
        
        generated_data.update({"humidity situation": sit})
        return sit
        
class Rainfall:
    def __init__(self, humidity):
        self.humidity = humidity
        self.fall = False
      
    def weather_fall(self):
        conditions = [True, False]
        fall = random.choices(conditions, weights=[0.41,0.59],k=1)
        generated_data.update({"rainfall": fall[0]})
        return fall[0]

    def generation(self):
        
        humidity = self.humidity
        fall = self.fall
        
        if humidity == "Very Dry" or fall == False:
            voltage = 0
        elif humidity == "Medium" and fall == True:
            voltage = round(random.uniform(0.1,0.5),2)
        elif humidity == "Humid" and fall == True:
            voltage = round(random.uniform(0.5,1.0),2)
        elif humidity == "Very Humid" and fall == True:
            voltage = round(random.uniform(1.0,2.0),2)

        generated_data.update({"voltage": voltage})

        return voltage

class Road_Wetness:

    def __init__(self, humidity, voltage):
        self.voltage = voltage
        self.humidity = humidity

    def generation(self):

        voltage = self.voltage
        humidity = self.humidity
        if voltage == 0 and humidity == "Very Dry":
            w_film_heigh_mm = 0
        elif voltage > 0:
            if voltage < 0.5:
                w_film_heigh_mm = round(random.uniform(1.0,4.0))
            elif voltage >= 0.5 and voltage < 1:
                w_film_heigh_mm = round(random.uniform(4.1,10.0))
            elif voltage >= 1:
                w_film_heigh_mm = round(random.uniform(10.0,50.0))
        elif voltage == 0:
            if humidity == "Medium":
                w_film_heigh_mm = round(random.uniform(0.0,0.25),2)
            elif humidity == "Humid":
                w_film_heigh_mm = round(random.uniform(0.25,0.5),2)
            elif humidity == "Very Humid":
                w_film_heigh_mm = round(random.uniform(0.5,2.0),2)

        generated_data.update({"road_wetness": w_film_heigh_mm})
        return w_film_heigh_mm

class R_Temp:
    def __init__(self,w_film):
        self.w_film = w_film
            
    def generation(self):
        if self.w_film > 4:
            r_temp = random.randint(0,20)
        else:
            r_temp = random.randint(-5,15)

        generated_data.update({"road_temperature": r_temp})
        return r_temp


class Vehicle:
    gravity = 9.81  
    
    def __init__(self):
        self.speed_kmh = random.randint(50,100)
        self.speed_ms = round(self.speed_kmh // 3.6)
        self.weight_kg = 1500
        self.date_time = datetime.datetime.now()
        self.user_brake_applied = False
        self.auto_brake_applied = False

    def generate(self,collected_data:dict):
        self.collected_data = collected_data
        self.collected_data.update({"speed": self.speed_kmh})
        self.collected_data.update({"Date_Time_Start": self.date_time.strftime("%d/%b/%y %X")})
        self.collected_data.update({"Lag" : 0})
        self.collected_data.update({"Driver_Reaction_Time" : 0.0})
        self.reaction_distance()
        self.co_of_friction()
        self.brake_distance()
        self.stopping_distance()
        self.brake_force()
        

    def reaction_distance(self):
        reaction_time = int(1)
        reaction_distance = round(self.speed_ms * reaction_time,2)
        self.collected_data.update({"reaction_distance": reaction_distance})
        return reaction_distance
        
    def brake_distance(self):
        reaction_distance = self.collected_data["reaction_distance"]
        co_of_friction = self.collected_data["co_of_friction"]
        brake_distance = round((reaction_distance ** 2) / (2 * co_of_friction * Vehicle.gravity),2)
        self.collected_data.update({"brake_distance": brake_distance})
        return brake_distance

    def stopping_distance(self):
        reaction_distance = self.collected_data["reaction_distance"]
        brake_distance = self.collected_data["brake_distance"]
        stopping_distance = round(reaction_distance + brake_distance, 3)
        self.collected_data.update({"stopping_distance": stopping_distance})
        return stopping_distance
    
    def co_of_friction(self):
        const, k_1, k_2, k_3, k_4, k_5, k_6 = 0.3033,0.1989,0.1011,0.2700,0.0015,-0.1018,0.0104
        collected_data = self.collected_data
        humidity = collected_data["humidity"]
        road_temperature = collected_data["road_temperature"]
        tire_temperature = collected_data["tire_temperature"]
        tire_pressure = collected_data["tire_pressure"]
        road_wetness = collected_data["road_wetness"]
        voltage = collected_data["voltage"]
        mu = const + k_1 * (1 - humidity/100) + k_2 * (road_temperature/20) + k_3 * (tire_temperature/90) + k_4 * (tire_pressure/500) - k_5 * (road_wetness/50) + k_6 * voltage
        self.collected_data.update({"co_of_friction" : round(mu,2)})
        return mu
    
    def brake(self,start_time,traffic_light_distance):
        light_distance = traffic_light_distance

        stopping_distance = self.collected_data["stopping_distance"]
        time_to_intervene = (light_distance - stopping_distance) / self.speed_ms

        try:
            while True:
                wait_time = time.time() - start_time
                            
                if wait_time >= time_to_intervene:
                    print("BRAKES APPLIED AUTOMATICALLY")
                    self.collected_data.update({"Lag" : round(wait_time - time_to_intervene,4)})
                    self.auto_brake_applied = True
                    self.speed()
                    break
                if keyboard.is_pressed('b'):
                    print("Brakes applied by driver safely")
                    self.user_brake_applied = True
                    brake_applied_time = round(time.time() - start_time,4)
                    self.collected_data.update({"Driver_Reaction_Time" : brake_applied_time})
                    self.speed()
                    break
        except KeyboardInterrupt:
            pass        
        pass

    def brake_force(self):
        mu = self.collected_data["co_of_friction"]
        deceleration = mu * self.gravity
        brake_force = deceleration * self.weight_kg
        self.collected_data.update({"brake_force" : round(brake_force,3)})
        return brake_force
    
    def speed(self):       
        mu = self.collected_data["co_of_friction"]
        speed_over_time = self.speed_ms
        decelaration = mu * self.gravity
        t_start = time.time()
        while speed_over_time > 0:    
            t_passed = time.time() - t_start
       
            speed_over_time = self.speed_ms - decelaration * t_passed
    
            if round(speed_over_time) < 0.1:
                speed_over_time = 0

            self.speed_kmh = round(speed_over_time * 3.6)
        pass        
        

class T_Temp:
    def __init__(self,speed_kmh):
        self.speed = speed_kmh
        
    def generation(self):
        if self.speed > 75 :
            t_temp = random.randint(0,90)
        elif self.speed >= 50:
            t_temp = random.randint(0,80)

        generated_data.update({"tire_temperature": t_temp})
        return t_temp 
    
class T_Pressure:
    def __init__(self,t_temp):
        self.t_temp = t_temp
                
    def generation(self):
        t_temp = self.t_temp
        if t_temp > 30 and t_temp < 80:
            t_pressure = random.randint(200,300)
        elif t_temp <= 30:
            t_pressure = random.randint(190,200)
        elif t_temp >= 80:
            t_pressure = random.randint(300,500)

        generated_data.update({"tire_pressure": t_pressure})
        return t_pressure

class TrafficLight:
    def __init__(self):
        self.distance = 220 
        self.color = None
        self.change = None
        self.last_update = time.time()

    def generation(self):
        conditions = ["Red","Yellow","Green"]
        status = random.choices(conditions, k=1)
        self.color = status[0]
        return self.color
    
    def color_change(self):
        conditions = [True,False]
        change = random.choice(conditions)
        self.change = change
        return change
    
    def distance_to_light(self,speed_ms):
        current_time = time.time()
        passed_time = current_time - self.last_update
        self.last_update = current_time
        self.distance = self.distance - (speed_ms * passed_time) 
        return int(self.distance)
    
    def time_to_light(self,speed_ms,stopping_distance):
        stopping_time = int(stopping_distance / speed_ms)
        return stopping_time


class Sensors:
    def __init__(self,speed_kmh):
        self.speed = speed_kmh

    def generation(self):
        humidity = Humidity()
        humidity_situation = humidity.situation()

        rainfall = Rainfall(humidity_situation)
        rainfall_fall = rainfall.weather_fall()
        rainfall_voltage = rainfall.generation()

        road_wetness = Road_Wetness(humidity_situation,rainfall_voltage)
        road_wetness_mm = road_wetness.generation()

        road_temperature = R_Temp(road_wetness_mm)
        road_temperature_degree = road_temperature.generation()

        tire_temperature = T_Temp(self.speed)
        t_temp = tire_temperature.generation()
        tire_pressure = T_Pressure(t_temp)
        t_press = tire_pressure.generation()

        return generated_data




