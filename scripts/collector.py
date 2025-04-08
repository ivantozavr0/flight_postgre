import requests
import datetime
import time
import os
from FlightRadar24 import FlightRadar24API
import psycopg2
import logging

logging.basicConfig(
    filename='logs/collector.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def parse_data():
    minlat, maxlat, minlon, maxlon = 41.0, 46.0, 28.0, 42.0
    
    #BBOX = "46.0,41.0,28.0,42.0"
    BBOX = str(maxlat) + "," + str(minlat) + "," + str(minlon) + "," + str(maxlon)  # черное море: max lat, min lat, min lon, max lon
    url = f"https://data-cloud.flightradar24.com/zones/fcgi/feed.js?bounds={BBOX}"
    headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    data = response.json() # первые 2 ключа - это служебная информация, а дальше уже то, что нужно (ключи - это id самолета)
    
    flight_ids = list(data.keys())[2:]
    
    cur_time = datetime.datetime.now()
    
    class Foo:
        def __init__(self, id_=None):
            self.id = id_
    
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        database=os.getenv("POSTGRES_DB", "flightradardb"),
        user=os.getenv("POSTGRES_USER", "admin"),
        password=os.getenv("POSTGRES_PASSWORD", "pass"),
        port="5432"
    )
    
    logging.info("start parsing")

    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS parse")
    
    # Создание таблицы
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parse (
            icao VARCHAR(10),
            callsign VARCHAR(10) PRIMARY KEY,
            model VARCHAR(50),
            airline VARCHAR(50),
            trail FLOAT[][],
            time TIMESTAMP
    )""")
    
    foo = Foo()
    
    fr_api = FlightRadar24API()
    
    for j, flight_id in enumerate(flight_ids):
        foo.id = flight_id
        try:
            flight_details = fr_api.get_flight_details(foo)
            if not flight_details:
                continue
            
            airline_name = None
            airline = flight_details.get("airline", {})
            if airline:
                airline_name = airline.get("name")
    
            flighttrack = None
            try:
                flighttrack = flight_details.get("trail") 
            except KeyError:
                print ("No trail data available")
    
            filteredtrack = []
        
            for point in flighttrack:
                latitude = point.get("lat") # или lat, в зависимости от структуры данных
                longitude = point.get("lng") # или lng, в зависимости от структуры данных
                
                if minlat <= latitude <= maxlat and minlon <= longitude <= maxlon:
                    filteredtrack.append([latitude, longitude])
                
            row = [
                data[flight_id][0],          # ICAO-код
                data[flight_id][16],     # Позывной
                flight_details.get("aircraft", {}).get("model", {}).get("text"),         # Модель самолета
                airline_name,     # Авиакомпания
                filteredtrack,      # Маршрут в области черного моря
                cur_time     # Время получения данного маршрута
            ]
            
            cursor.execute(""" INSERT INTO parse (icao, callsign, model, airline, trail, time)
            VALUES (%s, %s, %s, %s, %s, %s)""", row)
            conn.commit() # Committing inside the loop
            time.sleep(0.6)
        except Exception as e:
            print(f"Произошла ошибка при обработке flight_id {flight_id}: {e}")
            logging.info(f"Произошла ошибка при обработке flight_id {flight_id}: {e}")
            conn.rollback()
            time.sleep(0.6)
    
    print("collector HERE!")
    conn.commit()
    
    # Закрытие соединения
    cursor.close()
    conn.close()   
    
    logging.info("successfully parsing")

if __name__ == "__main__":
    parse_data()







