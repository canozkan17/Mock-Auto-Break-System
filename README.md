# MOCK Automatic Braking System Simulation

## Description
This project is a Python-based simulation of a vehicle's automatic braking system. It features a graphical user interface (GUI) built with PyQt5 to visualize the simulation in real-time. The simulation includes various environmental factors, detailed vehicle dynamics, and a traffic light system. All critical simulation parameters are logged into an SQLite database (`Loggs.db`). To ensure data security, the logged data and the keys used for encryption are protected using the Data Encryption Standard (DES) algorithm, requiring a master key for access and decryption.

## Features
*   **Interactive GUI:** Displays real-time vehicle speed, traffic light status, sensor readings, and environmental conditions.
*   **Environmental Simulation:** Models factors like humidity, rainfall, road wetness, and road/tire temperatures.
*   **Vehicle Dynamics:** Calculates reaction, braking, and stopping distances based on current conditions.
*   **Coefficient of Friction:** Dynamically calculates the coefficient of friction using multiple environmental and vehicle parameters.
*   **Traffic Light Simulation:** Simulates traffic lights with changing colors, influencing braking decisions.
*   **Braking Scenarios:** Supports both automatic braking initiated by the system and manual braking by the user (simulated via keyboard input).
*   **Data Logging:** Records detailed simulation parameters for each run into an SQLite database.
*   **DES Encryption:**
    *   Encrypts all logged data before storing it in the database.
    *   Encrypts the DES keys (generated per simulation run) using a user-defined master key. These encrypted DES keys are stored in `keys.txt`.
*   **Admin Mode:** Allows users with the master key to decrypt and view the logged data from the database.

## File Structure
*   `main.py`: Main entry point to launch the application. Initializes the simulation objects (Vehicle, Database) and the UI.
*   `UI.py`: Implements the PyQt5 based graphical user interface. It includes custom widgets for the speedometer and traffic light, manages UI updates, user interactions (like Admin Mode access), and houses the `light_operations` class for traffic light interaction logic within the UI context.
*   `classes.py`: Contains the core simulation classes:
    *   `Vehicle`: Manages vehicle state, dynamics (speed, braking calculations), and interaction with sensor data.
    *   `TrafficLight`: Simulates traffic light behavior (color changes, distance calculation).
    *   `Sensors`: Aggregates data from various environmental sensor classes.
    *   Environmental classes: `Humidity`, `Rainfall`, `Road_Wetness`, `R_Temp` (Road Temperature).
    *   Tire-related classes: `T_Temp` (Tire Temperature), `T_Pressure` (Tire Pressure).
*   `DB_class.py`: Manages all SQLite database operations. This includes creating tables (`logged_data`, `decrypted_data`, `user_master_key`), inserting encrypted simulation data, and handling data retrieval and display for the Admin mode.
*   `DES_class.py`: Implements the Data Encryption Standard (DES) algorithm. It's used for encrypting the collected simulation data before logging and for encrypting/decrypting the individual run keys stored in `keys.txt`.
*   `DES_constants.py`: Stores constant tables (S-boxes, permutation tables like PC-1, PC-2, IP, FP, E, P) required for the DES algorithm.
*   `light_detection.py`: Contains a `Light_Detection` class. This class also simulates traffic light detection and vehicle response, emitting PyQt signals. Its role might overlap with `UI.py`'s `light_operations` class and seems intended for a potentially different or decoupled simulation pathway.
*   `constants_calculation_ai.py`: A utility script for data analysis. It generates sample data, calculates friction coefficients, and uses `statsmodels` to perform linear regression. This is used for research or model calibration related to friction coefficient and is not part of the main simulation runtime.
    *   `Loggs.db`: The SQLite database file. Encrypted simulation data is stored in the `logged_data` table. Decrypted data is temporarily stored in `decrypted_data` when accessed via Admin Mode. The user-provided master key is stored in plain text in the `user_master_key` table (see Security note).
*   `keys.txt`: A text file storing DES keys. Each key is generated per simulation run for encrypting that run's data, and these keys themselves are encrypted using the master key before being stored in this file.
*   `car_running.wav`, `car_stopping.wav`: Audio files for engine and braking sound effects in the UI.
*   `brake_icon.png`: Image file used as the application icon.

## How to Run

### Prerequisites
*   Python 3.x
*   Install required Python libraries:
    ```bash
    pip install PyQt5 pandas statsmodels keyboard
    ```
    *(Note: `keyboard` is used for manual brake input in the simulation; ensure it works on your OS or adapt as needed.)*

### Running the Simulation
1.  Navigate to the project directory in your terminal.
2.  Run the command:
    ```bash
    python main.py
    ```

### Master Key
*   **First Run:** On the very first run of the application (or if `Loggs.db` or the `user_master_key` table is missing), you will be prompted to enter a Master Key.
*   **Purpose:** This master key is crucial. It's used to:
    1.  Encrypt the unique DES keys that are generated for each simulation run (these DES keys are stored in `keys.txt`).
    2.  Decrypt these DES keys when accessing Admin Mode, which then allows the decryption of the actual simulation data stored in `Loggs.db`.
*   **Security:** **You must remember this master key.** If lost, you will not be able to decrypt and view the logged data. The application will store a representation of this key in the `Loggs.db` for subsequent verification.

## Dependencies
*   **PyQt5:** For the graphical user interface.
*   **pandas:** Used in `DB_class.py` for displaying database contents (though the current `read_from_db` prints to console, pandas is available) and extensively in `constants_calculation_ai.py` for data manipulation.
*   **statsmodels:** Used in `constants_calculation_ai.py` for performing Ordinary Least Squares (OLS) regression analysis.
*   **keyboard:** Used in `classes.py` (Vehicle class) to detect manual brake input.
*   **sqlite3:** (Python standard library) Used for all database operations.

## Configuration
*   **Master Key:** User-defined upon first use. It is stored in plain text in the `user_master_key` table within `Loggs.db`.
*   **`keys.txt`:** Stores DES keys generated for each simulation session. Each key in this file is encrypted with the master key. This file is created if it doesn't exist.
*   **`Loggs.db`:** The SQLite database.
    *   `logged_data`: Table storing the actual simulation parameters, with data fields encrypted using a DES key from `keys.txt`.
    *   `decrypted_data`: Table temporarily populated with decrypted data when an admin accesses the logs. Can be cleared by the admin.
    *   `user_master_key`: Table storing the user's chosen master key in plain text.

## Notes
*   **Overlapping Functionality (`light_detection.py` vs. `UI.py`):** The `light_detection.py` file contains a `Light_Detection` class whose responsibilities (simulating traffic light detection and car response) appear to overlap with the `light_operations` class found within `UI.py`. This might be an area for future review to clarify distinct roles or refactor for better separation of concerns.
*   **Analysis Script (`constants_calculation_ai.py`):** The `constants_calculation_ai.py` script is a standalone utility for data analysis and model fitting (specifically, linear regression to understand friction coefficient). It is not executed as part of the main simulation runtime but serves as a tool for research, calibration, or deriving model parameters that might be used by an AI component (if one were to be integrated).
*   **Error Handling & Robustness:** The simulation includes basic error handling, but further improvements could be made for robustness, especially around file I/O and user inputs.
    *   **Security of Master Key Storage:** The master key is currently stored in plain text in the `Loggs.db` database. For a real-world application, this key should be securely hashed (e.g., using a strong, salted hashing algorithm like Argon2 or scrypt) before storage to protect it from unauthorized access. The current plain text storage is a significant security vulnerability.
