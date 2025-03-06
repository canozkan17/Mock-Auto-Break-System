import sqlite3
import pandas as pd

class DataBase():
    def __init__(self):
        self.connection = sqlite3.connect("Loggs.db")
        self.cursor = self.connection.cursor()

    def create_DB(self):
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
        self.connection = sqlite3.connect("Loggs.db")
        self.cursor = self.connection.cursor()
        self.collected_data = collected_data

        self.cursor.execute("SELECT * FROM logged_data ORDER BY row_id DESC LIMIT 1")
        self.connection.commit()
        try:
            row_id = int(self.cursor.fetchone()[0]) + 1
        except TypeError:
            row_id = 1

        self.cursor.execute("INSERT INTO logged_data VALUES ({}, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"
                        .format(row_id,
                                self.collected_data["Date_Time_Start"], 
                                self.collected_data["speed"],
                                self.collected_data["humidity"],
                                self.collected_data["humidity situation"], 
                                self.collected_data["rainfall"], 
                                self.collected_data["voltage"],
                                self.collected_data["road_wetness"], 
                                self.collected_data["road_temperature"], 
                                self.collected_data["tire_temperature"],
                                self.collected_data["tire_pressure"], 
                                self.collected_data["co_of_friction"],
                                self.collected_data["brake_force"], 
                                self.collected_data["reaction_distance"],
                                self.collected_data["stopping_distance"], 
                                self.collected_data["brake_distance"], 
                                self.collected_data["Driver_Reaction_Time"],
                                self.collected_data["Lag"]))
        self.connection.commit()
        self.connection.close()

    def create_Decrypted_db(self):
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
        self.connection = sqlite3.connect("Loggs.db")
        self.cursor = self.connection.cursor()
        self.collected_data = tobe_decrypted_data

        self.cursor.execute("SELECT * FROM decrypted_data ORDER BY row_id DESC LIMIT 1")
        self.connection.commit()
        try:
            row_id = int(self.cursor.fetchone()[0]) + 1
        except TypeError:
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

    def drop_Decrypted_table(self):
        self.connection = sqlite3.connect("Loggs.db")
        self.cursor = self.connection.cursor()    

        self.cursor.execute("DROP TABLE IF EXISTS decrypted_data")

        self.connection.commit()
        self.connection.close()

    def read_from_db(self):
        self.connection = sqlite3.connect("Loggs.db")
        self.cursor = self.connection.cursor()


        pd.set_option('display.max_rows', None)

        query = "SELECT * FROM decrypted_data ORDER BY row_id"


        result = pd.read_sql_query(query,self.connection)
        print(result)


 


