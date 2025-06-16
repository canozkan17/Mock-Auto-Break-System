"""
This script performs data generation, preprocessing, and statistical modeling
to analyze the factors influencing vehicle friction coefficient.

The script includes the following main steps:
1.  **Sample Data Generation**: Creates lists of sample data for various
    environmental and vehicle parameters such as humidity, road temperature,
    tire temperature, tire pressure, road wetness, and rainfall voltage.
    These lists represent hypothetical sensor readings or simulation inputs.

2.  **Friction Coefficient Calculation**: Generates a 'friction_coefficient' list
    based on an empirical formula that takes the generated parameters as inputs.
    This formula models how different factors might combine to affect friction.

3.  **Data Structuring**: Combines all generated lists into a pandas DataFrame
    for easier manipulation and analysis.

4.  **Data Normalization**: Normalizes some of the parameters (humidity,
    temperatures, pressure, wetness) to a common scale or representation,
    which can be beneficial for statistical modeling.

5.  **Regression Analysis**:
    -   Defines independent variables (X) from the normalized data and the
        rainfall voltage.
    -   Defines the dependent variable (y) as the calculated 'friction_coefficient'.
    -   Adds a constant term to the independent variables for the intercept
        in the linear regression model.
    -   Performs an Ordinary Least Squares (OLS) multiple linear regression using
        the `statsmodels` library to model the relationship between the
        independent variables and the friction coefficient.

6.  **Results Output**: Prints the summary of the regression model, which
    includes coefficients, standard errors, t-statistics, p-values, R-squared,
    and other statistical measures. This summary helps in understanding the
    significance and impact of each factor on the friction coefficient.

This script is primarily intended for data analysis, model exploration, or for
deriving/validating coefficients for a friction model, possibly for an AI
component within a larger simulation system. It does not define constants or
classes for direct import into the main simulation loop in the same way other
modules like `DES_constants.py` or `classes.py` might.
"""
import random
import pandas as pd
import statsmodels.api as sm

# --- Sample Data Generation ---
# These lists represent sample data points for various conditions.
# In a real scenario, this data might come from sensors or more complex simulations.
# All lists are ensured to have consistent lengths for DataFrame creation.
humidity= [8, 5, 97, 54, 90, 30, 8, 30, 88, 84, 26, 91, 29, 78, 76, 73, 77, 2, 44, 15, 35, 87, 9, 60, 44, 38, 10, 10, 73, 85, 49, 25, 53, 60, 45, 89, 36, 23, 72, 25, 33, 49, 16, 37, 22, 51, 41, 1, 78, 66, 83, 52, 3, 76, 1, 69, 34, 64, 6, 31, 34, 90, 34, 12, 85, 59, 13, 34, 41, 66, 47, 83, 1, 25, 20, 33, 43, 57, 74, 52, 3, 77, 32, 45, 76, 37, 4, 31, 30, 1, 40, 70, 29, 39, 53, 81, 10, 78, 48, 92, 44, 77, 55, 28, 98, 57, 48, 88, 2, 3, 14, 13, 14, 84, 44, 75, 4, 62, 97, 42, 32, 2, 32, 26, 96, 85, 71, 52, 79, 96, 53, 55, 5, 96, 69, 64, 54, 13, 39, 26, 21, 83, 99, 53, 16, 65, 38, 16, 56, 83]
road_temp= [11, -3, 11, -3, 2, 5, 8, 10, 12, 7, 1, -2, 3, 15, 15, 6, 9, -4, -2, 15, -5, 5, -1, 10, -2, 5, 15, 3, 6, 12, 14, 2, 1, 5, 13, 14, 5, 10, 6, -1, 6, 15, 11, 4, 3, 4, -2, 0, 6, -4, 14, 2, 2, 7, 9, -2, 13, 1, 2, -2, -2, -3, 3, 1, 10, 6, 12, 6, -3, 11, 10, 14, -5, 4, -5, -2, 10, 14, 11, 5, -2, -2, 0, 7, 19, 6, 12, 8, -2, 14, 3, 13, -4, 11, 11, 3, 3, 12, 15, 8, 3, 10, 11, -3, 15, 3, 11, 2, 0, 5, -3, -4, 15, 8, 5, 10, -4, 7, 9, -5, 8, 5, 6, -2, 2, 4, 11, 12, 7, 12, -3, 1, 2, 7, 4, 7, -5, -1, 7, 9, 13, 15, 0, 15, 3, 16, -4, 13, 12, -5]
tire_temp= [14, 23, 59, 31, 90, 60, 9, 78, 14, 27, 18, 72, 70, 83, 69, 11, 47, 63, 71, 17, 50, 51, 18, 12, 15, 58, 51, 14, 37, 16, 4, 7, 48, 16, 16, 1, 51, 29, 59, 17, 74, 19, 61, 18, 80, 62, 41, 62, 65, 80, 64, 0, 79, 16, 35, 86, 23, 66, 49, 34, 27, 73, 78, 11, 23, 55, 80, 67, 44, 50, 77, 7, 11, 58, 78, 6, 32, 35, 28, 63, 32, 86, 48, 28, 6, 35, 60, 53, 40, 21, 46, 66, 0, 62, 32, 68, 16, 0, 26, 34, 41, 45, 23, 1, 81, 33, 8, 30, 53, 2, 68, 64, 47, 15, 42, 80, 3, 13, 31, 56, 65, 38, 34, 55, 25, 23, 6, 10, 31, 49, 39, 68, 5, 26, 1, 43, 32, 85, 45, 69, 78, 74, 16, 79, 44, 65, 8, 71, 2, 42]
tire_pressure= [192, 191, 292, 288, 447, 252, 196, 206, 195, 198, 193, 201, 288, 396, 233, 199, 277, 276, 237, 198, 211, 280, 200, 191, 190, 201, 283, 198, 274, 190, 191, 198, 293, 197, 196, 200, 267, 193, 267, 191, 259, 190, 292, 198, 427, 300, 295, 226, 222, 360, 219, 199, 281, 199, 207, 449, 192, 235, 213, 222, 197, 250, 249, 199, 190, 241, 439, 201, 250, 244, 206, 197, 195, 234, 220, 195, 275, 236, 196, 238, 279, 475, 256, 192, 190, 275, 271, 271, 246, 191, 280, 207, 195, 257, 228, 282, 194, 197, 194, 213, 241, 286, 193, 195, 456, 256, 196, 199, 270, 193, 201, 239, 205, 191, 260, 331, 200, 190, 261, 201, 203, 270, 260, 253, 191, 198, 200, 197, 290, 218, 228, 235, 195, 198, 192, 242, 215, 458, 238, 242, 246, 271, 191, 231, 234, 277, 199, 259, 191, 256]
road_wetness= [0, 0, 1.63, 0.15, 1.77, 0.19, 0, 0.21, 0.52, 0.75, 0.05, 0.66, 3, 24, 23, 9, 24, 0, 0.22, 0, 0.21, 0.83, 0, 0.37, 2, 2, 0, 0, 0.34, 29, 2, 0, 2, 0.43, 0.07, 42, 0.21, 0, 9, 0, 0.03, 0.15, 0, 3, 0, 0.17, 3, 0, 1.26, 0.48, 1.05, 3, 0, 26, 0, 0.35, 0.09, 0.47, 0, 4, 4, 1.44, 0.19, 0, 48, 0.4, 0, 1, 0.12, 0.45, 3, 37, 0, 0, 0, 0.24, 2, 5, 6, 2, 0, 0.58, 0.15, 0.23, 39, 4, 0, 0.16, 0.01, 0, 0.23, 0.42, 0.13, 0.1, 0.04, 1.03, 0, 0.93, 0.05, 33, 2, 22, 0.12, 2, 42, 0.45, 2, 1.35, 0, 0, 0, 0, 0, 1.59, 1, 0.39, 0, 10, 1.29, 3, 0.04, 0, 0.21, 0.22, 1.8, 1.45, 0.43, 0.23, 49, 46, 0.16, 0.03, 0, 0.74, 0.43, 0.48, 2, 0, 1, 0.16, 0, 44, 1.92, 3, 0, 5, 3, 0, 6, 1.82]
rainfall_voltage= [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.24, 1.42, 1.44, 0.97, 1.96, 0, 0, 0, 0, 0, 0, 0, 0.32, 0.2, 0, 0, 0, 1.46, 0.35, 0, 0.11, 0, 0, 1.17, 0, 0, 0.9, 0, 0, 0, 0, 0.15, 0, 0, 0.37, 0, 0, 0, 0, 0.2, 0, 1.22, 0, 0, 0, 0, 0, 0.1, 0.34, 0, 0, 0, 1.8, 0, 0, 0.2, 0, 0, 0.36, 1.19, 0, 0, 0, 0, 0.16, 0.57, 0.55, 0.19, 0, 0, 0, 0, 1.59, 0.29, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.49, 0.21, 1.05, 0, 0.43, 1.45, 0, 0.37, 0, 0, 0, 0, 0, 0, 0, 0.14, 0, 0, 0.75, 0, 0.38, 0, 0, 0, 0, 0, 0, 0, 0, 1.25, 1.51, 0, 0, 0, 0, 0, 0, 0.37, 0, 0.39, 0, 0, 1.44, 0, 0.22, 0, 0.99, 0.12, 0, 0.79, 0]

# --- Friction Coefficient Calculation ---
# This formula is an example of how friction might be modeled.
# It combines various factors with arbitrary weights.
friction_coefficient = [
    round(0.7 - 0.002 * (h - 50) + 0.005 * (rt - 15) + 0.003 * (tt - 75) - 0.002 * (rw - 1.5) + 0.01 * rv, 2)
    for h, rt, tt, rw, rv in zip(humidity, road_temp, tire_temp, road_wetness, rainfall_voltage)
]

# --- Data Structuring with Pandas ---
data = {
    'humidity': humidity,
    'road_temp': road_temp,
    'tire_temp': tire_temp,
    'tire_pressure': tire_pressure,
    'road_wetness': road_wetness,
    'rainfall_voltage': rainfall_voltage,
    'friction_coefficient': friction_coefficient
}

# Create a Pandas DataFrame from the generated data.
df = pd.DataFrame(data)

# --- Data Normalization ---
# Normalizing data can be important for some machine learning algorithms or statistical models.
# The specific normalization methods used here are simple scaling or transformations.
df['humidity_norm'] = (1 - df['humidity'] / 100)
df['road_temp_norm'] = df['road_temp'] / 20  # Assuming typical max/range for road temp
df['tire_temp_norm'] = df['tire_temp'] / 90  # Assuming typical max/range for tire temp
df['tire_pressure_norm'] = df['tire_pressure'] / 500  # Assuming typical max/range for tire pressure
df['road_wetness_norm'] = df['road_wetness'] / 50  # Assuming typical max/range for road wetness

# --- Regression Analysis ---
# Define independent variables (features, X) and the dependent variable (target, y).
X = df[['humidity_norm', 'road_temp_norm', 'tire_temp_norm', 'tire_pressure_norm', 'road_wetness_norm', 'rainfall_voltage']]
y = df['friction_coefficient']

# Add a constant term to the independent variables to account for the intercept in the linear model.
X = sm.add_constant(X)

# Perform Ordinary Least Squares (OLS) multiple linear regression.
# This fits a linear model to predict 'friction_coefficient' based on the selected features.
model = sm.OLS(y, X).fit()

# --- Results Output ---
# Print a summary of the regression model, including coefficients, R-squared, etc.
print(model.summary())
