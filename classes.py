"""
This module defines the core classes used for the MOCK Automatic Braking System simulation.

These classes model various aspects of the simulation environment and vehicle dynamics:
- Environmental conditions: `Humidity`, `Rainfall`, `Road_Wetness`, `R_Temp` (Road Temperature).
- Vehicle properties and behavior: `Vehicle`.
- Tire characteristics: `T_Temp` (Tire Temperature), `T_Pressure` (Tire Pressure).
- Traffic infrastructure: `TrafficLight`.
- Sensor aggregation: `Sensors`.

The `generated_data` global dictionary is used by some of these classes to store
and pass around simulated sensor readings and environmental data. This is a somewhat
unconventional way to handle data flow and might be refactored in a larger system
for better encapsulation (e.g., by having `Sensors` return a structured object or dict).
The `keyboard` module is used by the `Vehicle` class for simulating manual brake input.
"""
import random
import time
import keyboard
import datetime

# Global dictionary to store generated data points from various sensor/environment classes.
# This is populated by individual classes and then typically returned by the `Sensors` class.
generated_data = {}

class Humidity:
    """
    Simulates environmental humidity and determines its qualitative state.

    Attributes:
        humidity (int): A randomly generated humidity percentage (0-100).
        sit (str | None): A string describing the humidity situation (e.g., "Very Dry", "Humid").
                          Initialized to None, set by `situation()`.
    """

    def __init__(self):
        """Initializes Humidity with a random humidity value."""
        self.humidity = random.randint(0,100)
        self.sit = None # Qualitative situation string
    
    def situation(self) -> str:
        """
        Determines and returns the qualitative humidity situation based on the humidity value.

        Updates `generated_data` with the raw humidity and situation string.

        Returns:
            str: A string describing the humidity situation (e.g., "Very Dry", "Humid").
        """
        generated_data.update({"humidity": self.humidity})
        # humidity = self.humidity # Local variable not strictly necessary here
        # sit = self.sit # Local variable not strictly necessary here

        if self.humidity <= 25:
            self.sit =  "Very Dry"
        elif self.humidity > 25 and self.humidity <=55: # Python allows chained comparisons: 25 < self.humidity <= 55
            self.sit =  "Medium"
        elif self.humidity > 55 and self.humidity <=75: # 55 < self.humidity <= 75
            self.sit =  "Humid"
        elif self.humidity > 75:
            self.sit =  "Very Humid"
        
        generated_data.update({"humidity situation": self.sit})
        return self.sit
        
class Rainfall:
    """
    Simulates rainfall presence and intensity (as a voltage) based on humidity.

    Attributes:
        humidity (str): The qualitative humidity situation (e.g., "Very Dry").
        fall (bool): Whether rainfall is occurring. Determined by `weather_fall()`.
    """
    def __init__(self, humidity: str):
        """
        Initializes Rainfall based on the current humidity situation.

        Args:
            humidity (str): The qualitative humidity situation string.
        """
        self.humidity = humidity
        self.fall = False # Initial state, updated by weather_fall()
      
    def weather_fall(self) -> bool:
        """
        Randomly determines if rainfall is occurring.

        The chance of rain is weighted (41% chance of True).
        Updates `generated_data` with the rainfall status.

        Returns:
            bool: True if rain is falling, False otherwise.
        """
        conditions = [True, False]
        # random.choices returns a list, so access the first element.
        self.fall = random.choices(conditions, weights=[0.41,0.59],k=1)[0]
        generated_data.update({"rainfall": self.fall})
        return self.fall

    def generation(self) -> float:
        """
        Generates a voltage value representing rainfall intensity.

        The voltage depends on the humidity situation and whether rain is falling.
        Updates `generated_data` with the generated voltage.

        Returns:
            float: A voltage value (typically 0 to 2.0).
        """
        
        # humidity = self.humidity # Local variable not needed
        # fall = self.fall # Local variable not needed
        voltage = 0.0 # Default to 0
        
        if self.humidity == "Very Dry" or not self.fall: # Corrected: use self.fall
            voltage = 0.0
        elif self.humidity == "Medium" and self.fall:
            voltage = round(random.uniform(0.1,0.5),2)
        elif self.humidity == "Humid" and self.fall:
            voltage = round(random.uniform(0.5,1.0),2)
        elif self.humidity == "Very Humid" and self.fall:
            voltage = round(random.uniform(1.0,2.0),2)

        generated_data.update({"voltage": voltage})
        return voltage

class Road_Wetness:
    """
    Simulates road wetness (water film height) based on humidity and rainfall voltage.

    Attributes:
        voltage (float): The voltage representing rainfall intensity.
        humidity (str): The qualitative humidity situation.
    """

    def __init__(self, humidity: str, voltage: float):
        """
        Initializes Road_Wetness.

        Args:
            humidity (str): The qualitative humidity situation string.
            voltage (float): The voltage from the rainfall sensor.
        """
        self.voltage = voltage
        self.humidity = humidity

    def generation(self) -> float:
        """
        Generates the water film height on the road in millimeters.

        The film height depends on the rainfall voltage and humidity.
        Updates `generated_data` with the calculated road wetness.

        Returns:
            float: The height of the water film in mm.
        """
        w_film_heigh_mm = 0.0 # Default value
        # voltage = self.voltage # Local variable not needed
        # humidity = self.humidity # Local variable not needed

        if self.voltage == 0 and self.humidity == "Very Dry":
            w_film_heigh_mm = 0.0
        elif self.voltage > 0: # If there's rainfall voltage, it dictates wetness primarily
            if self.voltage < 0.5:
                w_film_heigh_mm = round(random.uniform(1.0,4.0)) # Assuming integer mm for larger amounts
            elif self.voltage >= 0.5 and self.voltage < 1:
                w_film_heigh_mm = round(random.uniform(4.1,10.0))
            elif self.voltage >= 1:
                w_film_heigh_mm = round(random.uniform(10.0,50.0))
        elif self.voltage == 0: # No rainfall voltage, but humidity can cause some wetness
            if self.humidity == "Medium":
                w_film_heigh_mm = round(random.uniform(0.0,0.25),2)
            elif self.humidity == "Humid":
                w_film_heigh_mm = round(random.uniform(0.25,0.5),2)
            elif self.humidity == "Very Humid":
                w_film_heigh_mm = round(random.uniform(0.5,2.0),2)

        generated_data.update({"road_wetness": w_film_heigh_mm})
        return w_film_heigh_mm

class R_Temp: # Road Temperature
    """
    Simulates road surface temperature based on water film height.

    Attributes:
        w_film (float): The height of the water film on the road in mm.
    """
    def __init__(self,w_film: float):
        """
        Initializes Road Temperature simulation.

        Args:
            w_film (float): Water film height in mm.
        """
        self.w_film = w_film
            
    def generation(self) -> int:
        """
        Generates a road temperature value in Celsius.

        Temperature is influenced by the presence of significant water film.
        Updates `generated_data` with the road temperature.

        Returns:
            int: The road temperature in degrees Celsius.
        """
        if self.w_film > 4: # Significant water film might keep temp lower or stable
            r_temp = random.randint(0,20)
        else: # Less water, wider range including potential freezing
            r_temp = random.randint(-5,15)

        generated_data.update({"road_temperature": r_temp})
        return r_temp


class Vehicle:
    """
    Represents the simulated vehicle and its physical properties and actions.

    Handles calculations for speed, distances (reaction, braking, stopping),
    coefficient of friction, and simulates braking maneuvers.

    Attributes:
        gravity (float): Standard gravity in m/s^2. Class attribute.
        speed_kmh (int): Current speed of the vehicle in km/h.
        speed_ms (float): Current speed of the vehicle in m/s.
        weight_kg (int): Weight of the vehicle in kilograms.
        date_time (datetime.datetime): Timestamp of vehicle object creation or last update.
        user_brake_applied (bool): Flag indicating if user/driver has applied brakes.
        auto_brake_applied (bool): Flag indicating if autonomous braking is active.
        collected_data (dict): A dictionary storing various sensor readings and
                               calculated values related to the vehicle's state and
                               its environment.
    """
    gravity = 9.81  # m/s^2
    
    def __init__(self):
        """Initializes the Vehicle with random speed and default properties."""
        self.speed_kmh = random.randint(50,100)
        self.speed_ms = round(self.speed_kmh / 3.6, 2) # Corrected conversion and rounding
        self.weight_kg = 1500
        self.date_time = datetime.datetime.now()
        self.user_brake_applied = False
        self.auto_brake_applied = False
        self.collected_data = {} # Initialize to ensure it exists

    def generate(self,collected_data:dict):
        """
        Populates the vehicle's `collected_data` with initial and calculated values.

        This method should be called after sensor data has been collected externally
        and passed in. It then calculates derived metrics like various distances
        and forces.

        Args:
            collected_data (dict): A dictionary containing externally sourced sensor data
                                   (e.g., from the `Sensors` class).
        """
        self.collected_data = collected_data
        self.collected_data.update({"speed": self.speed_kmh})
        self.collected_data.update({"Date_Time_Start": self.date_time.strftime("%d/%b/%y %X")})
        self.collected_data.update({"Lag" : 0.0}) # Lag time for auto brake system
        self.collected_data.update({"Driver_Reaction_Time" : 0.0})
        
        # These calculations depend on data being present in self.collected_data
        # Ensure the order of calls is correct or data dependencies are handled.
        self.reaction_distance() # Depends on speed_ms
        self.co_of_friction()    # Depends on environmental factors from collected_data
        self.brake_distance()    # Depends on reaction_distance and co_of_friction
        self.stopping_distance() # Depends on reaction_distance and brake_distance
        self.brake_force()       # Depends on co_of_friction and weight


    def reaction_distance(self) -> float:
        """
        Calculates the distance traveled during driver's reaction time.

        Assumes a fixed reaction time of 1 second.
        Updates `self.collected_data` with the calculated reaction distance.

        Returns:
            float: The reaction distance in meters.
        """
        reaction_time_sec = 1.0 # Standard driver reaction time
        reaction_dist = round(self.speed_ms * reaction_time_sec, 2)
        self.collected_data.update({"reaction_distance": reaction_dist})
        return reaction_dist
        
    def brake_distance(self) -> float:
        """
        Calculates the theoretical braking distance once brakes are applied.

        Formula: `v^2 / (2 * mu * g)`, where v is initial speed (m/s),
        mu is coefficient of friction, g is gravity.
        Note: The current formula uses `reaction_distance` as `v`, which is incorrect.
        It should use `self.speed_ms`.
        Updates `self.collected_data` with the calculated brake distance.

        Returns:
            float: The braking distance in meters.
        """
        # reaction_distance = self.collected_data["reaction_distance"] # Incorrect use
        co_of_friction = self.collected_data.get("co_of_friction", 0.7) # Use .get for safety
        # Corrected formula: uses current speed in m/s
        brake_dist = round((self.speed_ms ** 2) / (2 * co_of_friction * Vehicle.gravity),2) \
            if co_of_friction > 0 else float('inf') # Handle mu=0 case
        self.collected_data.update({"brake_distance": brake_dist})
        return brake_dist

    def stopping_distance(self) -> float:
        """
        Calculates the total stopping distance (reaction distance + braking distance).

        Updates `self.collected_data` with the calculated stopping distance.

        Returns:
            float: The total stopping distance in meters.
        """
        reaction_dist = self.collected_data.get("reaction_distance", 0.0)
        brake_dist = self.collected_data.get("brake_distance", 0.0)
        stopping_dist = round(reaction_dist + brake_dist, 3)
        self.collected_data.update({"stopping_distance": stopping_dist})
        return stopping_dist
    
    def co_of_friction(self) -> float:
        """
        Calculates the coefficient of friction (mu) based on various environmental
        and vehicle parameters using an empirical formula.

        Parameters are fetched from `self.collected_data`.
        Updates `self.collected_data` with the calculated coefficient of friction.

        Returns:
            float: The calculated coefficient of friction (mu).
        """
        # Empirical constants for friction calculation
        const, k_1, k_2, k_3, k_4, k_5, k_6 = 0.3033,0.1989,0.1011,0.2700,0.0015,-0.1018,0.0104

        # Get data safely using .get() with defaults if keys might be missing
        humidity = self.collected_data.get("humidity", 50) # Default to 50%
        road_temperature = self.collected_data.get("road_temperature", 10) # Default to 10 C
        tire_temperature = self.collected_data.get("tire_temperature", 30) # Default to 30 C
        tire_pressure = self.collected_data.get("tire_pressure", 250) # Default to 250 kPa
        road_wetness = self.collected_data.get("road_wetness", 0) # Default to 0 mm
        voltage = self.collected_data.get("voltage", 0) # Default to 0 (rainfall sensor voltage)

        # Calculate mu using the empirical formula
        mu = const + \
             k_1 * (1 - humidity/100.0) + \
             k_2 * (road_temperature/20.0) + \
             k_3 * (tire_temperature/90.0) + \
             k_4 * (tire_pressure/500.0) - \
             k_5 * (road_wetness/50.0) + \
             k_6 * voltage

        mu = max(0.01, min(mu, 1.0)) # Clamp mu to a realistic range (e.g., 0.01 to 1.0)
        self.collected_data.update({"co_of_friction" : round(mu,2)})
        return mu
    
    def brake(self,start_time: float, traffic_light_distance: float):
        """
        Simulates the braking process, either by driver intervention or automatically.

        Monitors keyboard input for 'b' (driver brake). If driver doesn't brake
        within the calculated `time_to_intervene`, automatic braking is applied.
        Updates `collected_data` with lag time or driver reaction time.
        Calls `self.speed()` to simulate deceleration.

        Args:
            start_time (float): The timestamp when the braking scenario started.
            traffic_light_distance (float): Distance to the traffic light when scenario started.
        """
        # light_distance = traffic_light_distance # Renaming for clarity, not strictly needed

        stopping_dist = self.collected_data.get("stopping_distance", self.speed_ms * 2) # Default if not found

        # Time available before the car *must* start decelerating at the rate defined by stopping_distance
        # to stop *at* the light_distance.
        time_to_intervene = (traffic_light_distance - stopping_dist) / self.speed_ms if self.speed_ms > 0 else 0
        time_to_intervene = max(0, time_to_intervene) # Cannot be negative

        print(f"Brake scenario started. Time to intervene: {time_to_intervene:.2f}s. StopDist: {stopping_dist}m. LightDist: {traffic_light_distance}m")

        try:
            while True:
                elapsed_time = time.time() - start_time # Use elapsed_time for clarity
                            
                if elapsed_time >= time_to_intervene and not self.user_brake_applied:
                    print("AUTO BRAKES: Time to intervene elapsed. BRAKES APPLIED AUTOMATICALLY.")
                    self.collected_data.update({"Lag" : round(elapsed_time - time_to_intervene,4)})
                    self.auto_brake_applied = True
                    self.speed() # Simulate deceleration
                    break

                # Check for driver intervention (pressing 'b')
                # Note: keyboard.is_pressed can be CPU intensive and platform-dependent.
                # For a PyQt app, it's better to handle key presses via Qt event system.
                if keyboard.is_pressed('b'):
                    if not self.auto_brake_applied: # Driver reacted before auto-brake
                        print("DRIVER BRAKES: Brakes applied by driver.")
                        self.user_brake_applied = True
                        driver_reaction_time = round(elapsed_time,4)
                        self.collected_data.update({"Driver_Reaction_Time" : driver_reaction_time})
                        self.speed() # Simulate deceleration
                        break
                    else: # Auto-brake already engaged, driver pressing 'b' is redundant here
                        pass

                if self.speed_kmh == 0: # If car already stopped
                    break

                time.sleep(0.01) # Small sleep to prevent busy-waiting if using keyboard library

        except KeyboardInterrupt:
            print("Braking simulation interrupted by user (Ctrl+C).")
        # No specific 'pass' needed here unless it's a placeholder for future code.

    def brake_force(self) -> float:
        """
        Calculates the braking force.

        Formula: `Force = mu * g * mass`.
        Updates `self.collected_data` with the calculated brake force.

        Returns:
            float: The braking force in Newtons.
        """
        mu = self.collected_data.get("co_of_friction", 0.7)
        deceleration = mu * self.gravity
        calculated_brake_force = deceleration * self.weight_kg
        self.collected_data.update({"brake_force" : round(calculated_brake_force,3)})
        return calculated_brake_force
    
    def speed(self):
        """
        Simulates the vehicle's deceleration to a stop once brakes are applied.

        Updates `self.speed_kmh` and `self.speed_ms` over time until speed is zero.
        This method uses a loop that simulates time steps; in a real-time simulation,
        this would be integrated with a main simulation loop and delta time.
        """
        mu = self.collected_data.get("co_of_friction", 0.7)
        initial_speed_ms = self.speed_ms # Speed when braking starts
        deceleration = mu * self.gravity # m/s^2, assumed constant

        if deceleration <= 0: # Cannot decelerate if mu or gravity is zero/negative
            print("Warning: Cannot decelerate, mu or gravity is zero/negative.")
            return

        time_to_stop = initial_speed_ms / deceleration # Theoretical time to stop

        t_start_deceleration = time.time()
        elapsed_braking_time = 0

        print(f"Deceleration started. Initial speed: {initial_speed_ms:.2f} m/s. Deceleration: {deceleration:.2f} m/s^2. Est. time to stop: {time_to_stop:.2f}s")

        while self.speed_ms > 0:
            elapsed_braking_time = time.time() - t_start_deceleration

            # Speed = Initial Speed - (deceleration * time_elapsed_during_braking)
            current_speed_ms = initial_speed_ms - (deceleration * elapsed_braking_time)

            if current_speed_ms < 0.01: # Threshold to consider as stopped
                current_speed_ms = 0

            self.speed_ms = round(current_speed_ms, 2)
            self.speed_kmh = round(self.speed_ms * 3.6)

            # In a real simulation, this loop would yield to the main event loop
            # or be driven by it with fixed time steps.
            # For this blocking version, a small sleep can make it observable if printing speed.
            # print(f"Braking: Speed {self.speed_kmh} km/h, Time elapsed {elapsed_braking_time:.2f}s")
            if self.speed_ms == 0:
                break
            time.sleep(0.02) # Simulate discrete time steps for speed reduction

        print(f"Vehicle stopped. Actual braking time: {elapsed_braking_time:.2f}s")
        # No specific 'pass' needed here.
        

class T_Temp: # Tire Temperature
    """
    Simulates tire temperature based on vehicle speed.

    Attributes:
        speed (int): The vehicle's speed in km/h.
    """
    def __init__(self,speed_kmh: int):
        """
        Initializes Tire Temperature simulation.

        Args:
            speed_kmh (int): Current speed of the vehicle in km/h.
        """
        self.speed = speed_kmh
        
    def generation(self) -> int:
        """
        Generates a tire temperature value in Celsius.

        Temperature is higher for higher speeds.
        Updates `generated_data` with the tire temperature.

        Returns:
            int: The tire temperature in degrees Celsius.
        """
        t_temp = 0 # Default
        if self.speed > 75 :
            t_temp = random.randint(60,90) # Higher speed, higher temp range
        elif self.speed >= 50:
            t_temp = random.randint(40,79) # Medium speed, medium temp range
        else: # Lower speed
            t_temp = random.randint(20,39)


        generated_data.update({"tire_temperature": t_temp})
        return t_temp 
    
class T_Pressure: # Tire Pressure
    """
    Simulates tire pressure based on tire temperature.

    Attributes:
        t_temp (int): The tire temperature in Celsius.
    """
    def __init__(self,t_temp: int):
        """
        Initializes Tire Pressure simulation.

        Args:
            t_temp (int): Current tire temperature in Celsius.
        """
        self.t_temp = t_temp
                
    def generation(self) -> int:
        """
        Generates a tire pressure value in kPa.

        Pressure is influenced by temperature (higher temp, potentially higher pressure).
        Updates `generated_data` with the tire pressure.

        Returns:
            int: The tire pressure in kPa.
        """
        # t_temp = self.t_temp # Local variable not needed
        t_pressure = 0 # Default
        if self.t_temp > 30 and self.t_temp < 80: # Normal operating temp
            t_pressure = random.randint(200,300)
        elif self.t_temp <= 30: # Colder tire
            t_pressure = random.randint(190,220) # Slightly lower pressure
        elif self.t_temp >= 80: # Hotter tire
            t_pressure = random.randint(280,500) # Potentially higher pressure

        generated_data.update({"tire_pressure": t_pressure})
        return t_pressure

class TrafficLight:
    """
    Simulates a traffic light's state and behavior.

    Attributes:
        distance (float): Initial distance to the traffic light in meters.
        color (str | None): Current color of the traffic light ("Red", "Yellow", "Green").
        change (bool | None): Flag indicating if the light's color might change.
        last_update (float): Timestamp of the last time distance was updated.
    """
    def __init__(self):
        """Initializes the TrafficLight with a default distance and state."""
        self.distance = 220.0 # Initial distance to the light in meters
        self.color = None
        self.change = None # Not directly used for color state, but for simulating change event
        self.last_update = time.time() # For calculating distance traveled

    def generation(self) -> str:
        """
        Randomly generates and sets the initial color of the traffic light.

        Returns:
            str: The generated color ("Red", "Yellow", or "Green").
        """
        conditions = ["Red","Yellow","Green"]
        self.color = random.choice(conditions) # Corrected from random.choices k=1
        return self.color
    
    def color_change(self) -> bool:
        """
        Randomly determines if the traffic light should change its color.

        This simulates the dynamic nature of a traffic light.
        Sets `self.change` attribute.

        Returns:
            bool: True if the light is simulated to change, False otherwise.
        """
        conditions = [True,False]
        self.change = random.choice(conditions) # 50/50 chance of change
        return self.change
    
    def distance_to_light(self,speed_ms: float) -> int:
        """
        Calculates the new distance to the light based on vehicle speed and elapsed time.

        Updates `self.distance` and `self.last_update`.

        Args:
            speed_ms (float): Current speed of the vehicle in m/s.

        Returns:
            int: The updated distance to the light in meters, rounded to an integer.
        """
        current_time = time.time()
        passed_time = current_time - self.last_update
        self.last_update = current_time

        distance_covered = speed_ms * passed_time
        self.distance -= distance_covered
        self.distance = max(0, self.distance) # Distance cannot be negative
        return int(self.distance)
    
    def time_to_light(self,speed_ms: float, current_distance: float) -> int: # Renamed arg
        """
        Calculates the estimated time to reach the traffic light at the current speed.

        Args:
            speed_ms (float): Current speed of the vehicle in m/s.
            current_distance (float): Current distance to the traffic light in meters.

        Returns:
            int: Estimated time to reach the light in seconds. Returns a large number
                 if speed is zero to represent infinite time.
        """
        if speed_ms <= 0:
            return float('inf') # Or a very large number, effectively infinite time

        time_to_reach = current_distance / speed_ms
        return int(time_to_reach)


class Sensors:
    """
    Aggregates data from various simulated environmental and vehicle sensors.

    This class initializes instances of other sensor-like classes (Humidity,
    Rainfall, etc.) and calls their generation methods to populate the
    global `generated_data` dictionary.

    Attributes:
        speed (int): The vehicle's speed in km/h, used to initialize some sensors.
    """
    def __init__(self,speed_kmh: int):
        """
        Initializes the Sensors aggregator.

        Args:
            speed_kmh (int): Current speed of the vehicle in km/h.
        """
        self.speed = speed_kmh

    def generation(self) -> dict:
        """
        Generates and collects data from all simulated sensors.

        Instantiates sensor classes, calls their data generation methods,
        which in turn update the global `generated_data` dictionary.

        Returns:
            dict: The `generated_data` dictionary populated with the latest
                  sensor readings and environmental data.
        """
        # Initialize and generate data from each sensor type
        humidity_sensor = Humidity()
        humidity_situation_str = humidity_sensor.situation()

        rainfall_sensor = Rainfall(humidity_situation_str)
        is_raining = rainfall_sensor.weather_fall() # Determine if it's raining
        # rainfall_sensor.fall is now set, use it for voltage generation
        rainfall_voltage_val = rainfall_sensor.generation()

        road_wetness_sensor = Road_Wetness(humidity_situation_str, rainfall_voltage_val)
        road_wetness_mm_val = road_wetness_sensor.generation()

        road_temp_sensor = R_Temp(road_wetness_mm_val)
        road_temp_degree_val = road_temp_sensor.generation()

        tire_temp_sensor = T_Temp(self.speed)
        tire_temp_val = tire_temp_sensor.generation()

        tire_pressure_sensor = T_Pressure(tire_temp_val)
        tire_pressure_val = tire_pressure_sensor.generation() # Corrected to call method

        # The global generated_data dictionary is populated by the .generation()
        # and .situation() methods of the above classes.
        return generated_data




