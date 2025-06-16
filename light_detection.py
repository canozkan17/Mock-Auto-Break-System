"""
This module simulates the detection of traffic lights and the subsequent
decision-making process for a vehicle.

It defines the `Light_Detection` class which encapsulates the logic for:
- Simulating a traffic light's state (color, distance).
- Calculating braking and stopping distances based on vehicle speed.
- Simulating the vehicle's approach to the light.
- Determining if the light color changes during approach.
- Making a decision to brake or proceed based on the light's final state
  and the vehicle's ability to stop safely.
- Emitting signals (e.g., `light_distance_signal`) that can be used by
  other parts of an application (potentially a UI) to react to these events.

Note: The `keyboard` import is present but not used in the provided code.
The functionality of this module appears similar in some aspects to the
`light_operations` class within `UI.py`, but is structured as a standalone
QObject, suggesting it could be used independently or integrated differently.
"""
import classes
import time
import keyboard # This import is not used in the current code.
from PyQt5.QtCore import pyqtSignal,QObject


class Light_Detection(QObject):
    """
    Simulates traffic light detection and vehicle response logic.

    This class models the process of a vehicle approaching a traffic light.
    It determines the light's color, calculates necessary stopping distances,
    simulates the approach, checks for light changes, and then decides
    whether the vehicle should brake or proceed. It uses PyQt signals to
    communicate events like changes in distance to the light.

    Signals:
        light_distance_signal (pyqtSignal(int)): Emitted to signal the current
                                                 distance to the traffic light.
    Attributes:
        light_color (str): The currently detected color of the traffic light.
        changed_light_color (str): The color the light may change to upon closer
                                   approach or after a time interval.
    """
    light_distance_signal = pyqtSignal(int)

    def __init__(self):
        """
        Initializes the Light_Detection object.
        Sets up initial empty values for `light_color` and `changed_light_color`.
        """
        super().__init__()

        self.light_color = ""
        self.changed_light_color = ""

    def light_iterator(self,light_color: str) -> str:
        """
        Determines the next color in a predefined traffic light sequence.

        The sequence is Green -> Yellow -> Red -> Yellow -> Green.

        Args:
            light_color (str): The current color of the traffic light.
                               Expected values: "Green", "Yellow", "Red".

        Returns:
            str: The next color in the traffic light sequence. If the input
                 color is not recognized, it might raise an error or return
                 an unexpected value due to `list.index()`.
        """
        light_conditions = ["Green","Yellow","Red","Yellow"] # Order matters for cycling
        # This implementation of cycling through colors can be problematic if
        # "Yellow" is ambiguous (is it after Green or after Red?).
        # A state machine or more context might be needed for perfect accuracy.
        try:
            current_index = light_conditions.index(light_color)
            # This logic might not correctly cycle G->Y1->R->Y2->G
            # For example, if light_color is "Yellow", index is 1. Next is "Red".
            # If light_color is "Red", index is 2. Next is "Yellow".
            # This doesn't distinguish the two "Yellow" states in a G-Y-R-Y cycle.
            # However, if trafficLight.color_change() implies a full cycle step,
            # then this might be fetching the color *after* the change.
            # Example: If was Green, changes, new is Yellow. iterator("Green") -> "Yellow".
            # If was Red, changes, new is Yellow. iterator("Red") -> "Yellow".
            # This seems to be the intended use.
            i = current_index
            # The original code had:
            # i = light_conditions.index(light_color)
            # enumared_light = list(enumerate(light_conditions))
            # return enumared_light[i+1][1] # This would go out of bounds for last "Yellow"

            # Corrected cycling:
            if i == 0: # Green
                return "Yellow"
            elif i == 1: # First Yellow (after Green)
                return "Red"
            elif i == 2: # Red
                return "Yellow" # Second Yellow (after Red)
            elif i == 3: # Second Yellow
                return "Green"
            else: # Should not happen
                return light_conditions[0]
        except ValueError:
            # Handle cases where light_color is not in light_conditions
            print(f"Warning: Unknown light color '{light_color}' in light_iterator.")
            return "Green" # Default or error color


    def light(self,car: classes.Vehicle):
        """
        Simulates the process of detecting a traffic light and reacting to it.

        This comprehensive method performs several steps:
        1. Initializes a `TrafficLight` object to get its current state (color, distance).
        2. Emits the initial distance via `light_distance_signal`.
        3. Initializes `Sensors` based on current car speed and gets sensor data.
        4. Updates the `car` object with this sensor data (which calculates brake/stopping distances).
        5. Simulates the car approaching the light:
           - In a loop, updates the distance to the light.
           - If the light is Red or Yellow, calculates estimated stopping time and emits distance.
           - The loop continues until the car is within a certain range of the
             calculated stopping distance (plus a buffer of 50m).
        6. Checks if the traffic light's color changes as the car gets closer.
        7. Makes a final decision based on the (potentially changed) light color:
           - If Red or Yellow (from Green): Calculates time to intervene and instructs the car to brake.
           - If Green or Yellow (from Red/Yellow, implying passage is now allowed): Prints "Light Allows Passage".
           - If braking is required but the calculated brake distance is greater than
             the current distance to the light, it prints that the vehicle is unsafe to stop.

        Args:
            car (classes.Vehicle): The vehicle object that is approaching the light.
                                   This object will have its `brake()` method called
                                   if necessary and its attributes (speed, sensor data) used.
        """

        # Initialize traffic light and get its initial state
        trafficLight = classes.TrafficLight()
        self.light_color = trafficLight.generation() # Sets initial color
        light_detection_time = int(time.time()) # Records time of detection
        
        print(f"Light Detected at: {trafficLight.distance}m = {self.light_color.upper()}")
        self.light_distance_signal.emit(trafficLight.distance) # Emit initial distance

        # Get sensor data and calculate braking/stopping distances
        sensors = classes.Sensors(car.speed_kmh)
        sensors_data = sensors.generation()
        car.generate(sensors_data) # Car processes sensor data to update its state
        brake_distance = car.collected_data["brake_distance"]
        stopping_distance = car.collected_data["stopping_distance"]

        print(f"Calculated Brake Distance: {brake_distance} m")
        print(f"Calculated Stopping Distance (includes reaction): {stopping_distance} m")
        
        current_light_distance = trafficLight.distance_to_light(car.speed_ms, light_detection_time)
        # print(f"Initial calculated distance to Light: {current_light_distance} m")

        # Simulate approaching the light
        # Loop continues as long as the car is further than its stopping distance + 50m buffer
        # This simulates the car moving closer before a critical decision point.
        approach_buffer = 50 # meters
        while current_light_distance > stopping_distance + approach_buffer:
            light_detection_time = int(time.time()) # Update time for distance calculation
            # time.sleep(0.1) # Simulate passage of time - using actual time diff is better
            current_light_distance = trafficLight.distance_to_light(car.speed_ms, light_detection_time)
            self.light_distance_signal.emit(int(current_light_distance)) # Emit current distance

            if self.light_color == "Red" or self.light_color == "Yellow":
                # Optional: calculate time to light if needed for UI, not directly used in logic below
                # stopping_time = trafficLight.time_to_light(car.speed_ms, current_light_distance)
                # print(f"Approaching {self.light_color} light. Distance: {current_light_distance:.2f}m. Time to light: {stopping_time:.2f}s")
                pass # Handled by general print below
            #else:
            print(f"Approaching light. Distance: {current_light_distance:.2f} m")
            if current_light_distance <= 0: break # Safety break if passed light
        
        print(f"Reached decision zone. Distance: {current_light_distance:.2f}m.")
        
        # Check if the light changes color at the decision point
        if trafficLight.color_change(): # Simulates a random chance of color change
            self.changed_light_color = self.light_iterator(self.light_color)
            print(f"LIGHT HAS CHANGED FROM {self.light_color} TO {self.changed_light_color}")
        else: 
            self.changed_light_color = self.light_color # No change

        final_decision_color = self.changed_light_color

        # Update distance one last time before final decision
        light_detection_time = int(time.time())
        current_light_distance = trafficLight.distance_to_light(car.speed_ms, light_detection_time)
        self.light_distance_signal.emit(int(current_light_distance))
        print(f"Final decision distance: {current_light_distance:.2f}m to {final_decision_color} light.")

        # Decision logic based on final light color and ability to stop
        if brake_distance < current_light_distance: # Vehicle can stop in time
            if final_decision_color == "Red":
                start_time_brake = int(time.time()) # Renamed to avoid conflict
                # Time to intervene is effectively the time the car has before it *must* brake.
                # If already deciding to brake, this is more of a "time until stop" if braking starts now.
                time_to_intervene = (current_light_distance - brake_distance) / car.speed_ms if car.speed_ms > 0 else float('inf')
                print(f"RED light. Braking initiated. Estimated time to intervene/stop if braking starts now: {time_to_intervene:.2f}s")
                car.brake(start_time_brake, current_light_distance)

            elif final_decision_color == "Yellow":
                # Decision for yellow: if current light was green, now yellow means prepare to stop.
                # If current light was red/yellow, now yellow might mean it's about to turn green (proceed with caution or stop based on rules)
                if self.light_color == "Green": # Transitioned Green -> Yellow
                    start_time_brake_yellow = int(time.time())
                    time_to_intervene_yellow = (current_light_distance - brake_distance) / car.speed_ms if car.speed_ms > 0 else float('inf')
                    print(f"YELLOW light (from Green). Braking. Estimated time to intervene/stop: {time_to_intervene_yellow:.2f}s")
                    car.brake(start_time_brake_yellow, current_light_distance)
                else: # Was Red or Yellow, now Yellow again (e.g., end of Red cycle) - typically means proceed or light is stuck.
                      # For this simulation, assume it means "about to turn green" or "safe to proceed if already stopping for red".
                    print("YELLOW light (not from Green). Assuming passage is allowed or will be soon. Proceeding with caution.")

            elif final_decision_color == "Green":
                print("GREEN light. Passage allowed.")

        elif brake_distance >= current_light_distance: # Vehicle cannot stop in time
            print(f"Vehicle UNSAFE to stop (BrakeDist {brake_distance:.2f}m >= LightDist {current_light_distance:.2f}m). Proceeding through {final_decision_color} light.")
            if final_decision_color == "Red":
                print("CRITICAL: Running RED light as vehicle cannot stop in time.")


