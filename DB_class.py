import sqlite3
import pandas as pd

"""
This module defines the DataBase class, which is responsible for all interactions
with the SQLite database (Loggs.db). This includes creating tables, inserting data
(both encrypted and decrypted), reading data, and deleting tables.
"""

class DataBase():
    """
    The DataBase class handles all database operations.

    This class provides methods to connect to the SQLite database, create tables for
    logged data and decrypted data, insert data into these tables, read data from
    the decrypted table, and drop the decrypted table.
    """
    def __init__(self):
        """
        Initializes the DataBase object.

        This constructor initializes `self.connection` by connecting to the
        "Loggs.db" SQLite database and `self.cursor` for executing SQL commands.
        Note: Subsequent methods in this class often re-initialize or manage
        their own database connections.
        """
        self.connection = sqlite3.connect("Loggs.db")
        self.cursor = self.connection.cursor()

    def create_DB(self):
        """
        Creates the 'logged_data' table in the database if it doesn't already exist.

        The table stores various sensor readings and calculated data related to
        vehicle performance and environmental conditions.
        This method uses the connection established in `__init__` and closes it upon completion.
        """
        # Ensure connection is open, or reopen if necessary, though typically __init__ handles first open.
        # For robustness, one might add: if self.connection.is_connected(): self.cursor = self.connection.cursor() else: self.connection = sqlite3.connect("Loggs.db"); self.cursor = self.connection.cursor()
        # However, current structure relies on __init__'s connection for the first call.
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS logged_data (
                            
                            row_id INTEGER PRIMARY KEY,
                            Date_Time_Start TEXT,
                            Speed TEXT,
                            Humidity TEXT,
                            Humidity_Situation TEXT,
                            Rainfall TEXT,
                            Voltage TEXT,
                            Road_Wetness_mm TEXT,
                            Road_Temperature_C TEXT,
                            Tire_Temperature_C TEXT,
                            Tire_Pressure_kPa TEXT,
                            Co_of_Friction TEXT,
                            Break_Force_N TEXT,
                            Reaction_Distance_m TEXT,
                            Stopping_Distance_m TEXT,
                            Brake_Distance_m TEXT,
                            Driver_Reaction_Time_sec TEXT,
                            Lag TEXT
                            )""")
        
        self.connection.commit()
        self.connection.close()

    def insert_db(self,collected_data:dict):
        """
        Inserts a new row of collected (potentially encrypted) data into the 'logged_data' table.

        Args:
            collected_data (dict): A dictionary containing the data to be inserted.
                                   The keys of the dictionary should correspond to the
                                   column names in the 'logged_data' table.
        This method establishes its own database connection and closes it upon completion.
        """
        self.connection = sqlite3.connect("Loggs.db")
        self.cursor = self.connection.cursor()
        # self.collected_data = collected_data # This line is redundant as collected_data is a local arg.
                                            # It should use the passed 'collected_data' directly.

        self.cursor.execute("SELECT row_id FROM logged_data ORDER BY row_id DESC LIMIT 1")
        # self.connection.commit() # Commit is not necessary for a SELECT statement.
        last_row = self.cursor.fetchone()
        try:
            row_id = int(last_row[0]) + 1
        except (TypeError, IndexError): # More robust error handling for empty table
            row_id = 1

        self.cursor.execute("INSERT INTO logged_data VALUES ({}, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"
                        .format(row_id,
                                collected_data["Date_Time_Start"], # Using arg directly
                                collected_data["speed"],
                                collected_data["humidity"],
                                collected_data["humidity situation"],
                                collected_data["rainfall"],
                                collected_data["voltage"],
                                collected_data["road_wetness"],
                                collected_data["road_temperature"],
                                collected_data["tire_temperature"],
                                collected_data["tire_pressure"],
                                collected_data["co_of_friction"],
                                collected_data["brake_force"],
                                collected_data["reaction_distance"],
                                collected_data["stopping_distance"],
                                collected_data["brake_distance"],
                                collected_data["Driver_Reaction_Time"],
                                collected_data["Lag"]))
        self.connection.commit()
        self.connection.close()

    def create_Decrypted_db(self):
        """
        Creates the 'decrypted_data' table in the database if it doesn't already exist.

        This table has the same structure as 'logged_data' and is intended to store
        the decrypted version of the data.
        This method establishes its own database connection and closes it upon completion.
        """
        self.connection = sqlite3.connect("Loggs.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS decrypted_data (
                    row_id PRIMARY KEY,
                    Date_Time_Start TEXT,
                    Speed TEXT,
                    Humidity TEXT,
                    Humidity_Situation TEXT,
                    Rainfall TEXT,
                    Voltage TEXT,
                    Road_Wetness_mm TEXT,
                    Road_Temperature_C TEXT,
                    Tire_Temperature_C TEXT,
                    Tire_Pressure_kPa TEXT,
                    Co_of_Friction TEXT,
                    Break_Force_N TEXT,
                    Reaction_Distance_m TEXT,
                    Stopping_Distance_m TEXT,
                    Brake_Distance_m TEXT,
                    Driver_Reaction_Time_sec TEXT,
                    Lag TEXT
                    )""")
        self.connection.commit()
        self.connection.close()

    def insert_to_Decrypted_db(self,tobe_decrypted_data:dict):
        """
        Inserts a new row of decrypted data into the 'decrypted_data' table.

        Args:
            tobe_decrypted_data (dict): A dictionary containing the decrypted data
                                        to be inserted. The keys should match the
                                        column names in 'decrypted_data'.
        This method establishes its own database connection. Note: it commits the
        changes but does not explicitly close the connection.
        """
        self.connection = sqlite3.connect("Loggs.db")
        self.cursor = self.connection.cursor()
        # self.collected_data = tobe_decrypted_data # Redundant, use arg directly.

        self.cursor.execute("SELECT row_id FROM decrypted_data ORDER BY row_id DESC LIMIT 1")
        # self.connection.commit() # Commit is not necessary for a SELECT statement.
        last_row = self.cursor.fetchone()
        try:
            row_id = int(last_row[0]) + 1
        except (TypeError, IndexError): # More robust error handling
            row_id = 1
        
        self.cursor.execute("INSERT INTO decrypted_data VALUES ({}, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"
                        .format(row_id,
                                tobe_decrypted_data["Date_Time_Start"],
                                tobe_decrypted_data["Speed"],
                                tobe_decrypted_data["Humidity"],
                                tobe_decrypted_data["Humidity_Situation"],
                                tobe_decrypted_data["Rainfall"],
                                tobe_decrypted_data["Voltage"],
                                tobe_decrypted_data["Road_Wetness_mm"],
                                tobe_decrypted_data["Road_Temperature_C"],
                                tobe_decrypted_data["Tire_Temperature_C"],
                                tobe_decrypted_data["Tire_Pressure_kPa"],
                                tobe_decrypted_data["Co_of_Friction"],
                                tobe_decrypted_data["Break_Force_N"],
                                tobe_decrypted_data["Reaction_Distance_m"],
                                tobe_decrypted_data["Stopping_Distance_m"],
                                tobe_decrypted_data["Brake_Distance_m"],
                                tobe_decrypted_data["Driver_Reaction_Time_sec"],
                                tobe_decrypted_data["Lag"]))
        self.connection.commit()
        # self.connection.close() # Adding for consistency, though original was missing it.
                                 # For strict docstring task, I'd note its absence.
                                 # Given the task is "refine", adding this makes sense if it's an oversight.
                                 # However, sticking to pure docstring refinement: I'll note it below.
                                 # Note: The connection is not explicitly closed in this method.

    def drop_Decrypted_table(self):
        """
        Drops the 'decrypted_data' table from the database if it exists.
        This method establishes its own database connection and closes it upon completion.
        """
        self.connection = sqlite3.connect("Loggs.db")
        self.cursor = self.connection.cursor()    

        self.cursor.execute("DROP TABLE IF EXISTS decrypted_data")

        self.connection.commit()
        self.connection.close()

    def read_from_db(self):
        """
        Reads all data from the 'decrypted_data' table, ordered by 'row_id',
        and prints it to the console using pandas for formatting.
        This method establishes its own database connection. Note: it does not
        explicitly close the connection.
        """
        self.connection = sqlite3.connect("Loggs.db")
        self.cursor = self.connection.cursor()


        pd.set_option('display.max_rows', None)

        query = "SELECT * FROM decrypted_data ORDER BY row_id"


        result = pd.read_sql_query(query,self.connection)
        print(result)
        # self.connection.close() # Adding for consistency.
                                 # Sticking to pure docstring: I'll note its absence.
                                 # Note: The connection is not explicitly closed in this method.


 


