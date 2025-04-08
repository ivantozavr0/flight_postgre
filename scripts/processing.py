import psycopg2
import os
import datetime
import logging

logging.basicConfig(
    filename='logs/processing.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)


def process_data():
    #-------------------------------удаляем все строки, которым больше часа

    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        database=os.getenv("POSTGRES_DB", "flightradardb"),
        user=os.getenv("POSTGRES_USER", "admin"),
        password=os.getenv("POSTGRES_PASSWORD", "pass"),
        port="5432"
    )

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hourly_report (
            icao VARCHAR(10),
            callsign VARCHAR(10) PRIMARY KEY,
            model VARCHAR(50),
            airline VARCHAR(50),
            trail FLOAT[][],
            time TIMESTAMP
    )""")
    
    logging.info("start processing")

    cursor.execute("SELECT time FROM parse LIMIT 1") 
    parse_time = cursor.fetchall()[0][0]
    #print(parse_time)

    sql_query = """
        DELETE FROM hourly_report
        WHERE EXTRACT(EPOCH FROM (%s - hourly_report.time)) > 3600
    """
    cursor.execute(sql_query, (parse_time,))
    
    logging.info(f"current time: ---------  {parse_time}")
    
    conn.commit()
    
    logging.info("check time")

    cursor.close()
    conn.close()

    #------------------------сохраняем новые данные

    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        database=os.getenv("POSTGRES_DB", "flightradardb"),
        user=os.getenv("POSTGRES_USER", "admin"),
        password=os.getenv("POSTGRES_PASSWORD", "pass"),
        port="5432"
    )

    cursor = conn.cursor()
    
    # информация по некоторым icao могла обновиться, перезапишем ее
    cursor.execute("""DELETE FROM hourly_report 
WHERE hourly_report.callsign IN (SELECT parse.callsign FROM parse)""")

    conn.commit()
        
    logging.info("delete")
    
    #cursor.execute("""SELECT parse.icao, parse.callsign, parse.model, parse.airline, parse.trail, parse.time
    #FROM parse
    #LEFT JOIN hourly_report ON parse.callsign = hourly_report.callsign
    #WHERE hourly_report.callsign IS NULL""")
    
    # записали
    cursor.execute("""INSERT INTO hourly_report (icao, callsign, model, airline, trail, time)
        SELECT parse.icao, parse.callsign, parse.model, parse.airline, parse.trail, parse.time FROM parse""")
        
    cursor.execute("SELECT COUNT(*) FROM hourly_report") 
    number_of_samples = cursor.fetchall()[0][0]
    
    logging.info(f"Samples in hourly_report = {number_of_samples}")

    conn.commit()

    # Закрытие соединения
    cursor.close()
    conn.close()   

    # -----------------------------------Отчетность

    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        database=os.getenv("POSTGRES_DB", "flightradardb"),
        user=os.getenv("POSTGRES_USER", "admin"),
        password=os.getenv("POSTGRES_PASSWORD", "pass"),
        port="5432"
    )

    cursor = conn.cursor()

    # Отчет по авиалиниям
    cursor.execute("DROP TABLE IF EXISTS airline_report")

    # Создание таблицы
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS airline_report (
            airline VARCHAR(50),
            numb Smallint
    )""")
    conn.commit()

    cursor.execute("SELECT hourly_report.airline, COUNT(*) AS Count FROM hourly_report GROUP BY hourly_report.airline ORDER BY Count ASC") 
    rows = cursor.fetchall() 
    for row in rows: 
        cursor.execute(""" INSERT INTO airline_report (airline, numb)
        VALUES (%s, %s)""", row)
    conn.commit()

    # отчет по моделям
    cursor.execute("DROP TABLE IF EXISTS model_report")

    # создание таблицы
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS model_report (
            model VARCHAR(50),
            numb Smallint
    )""")
    conn.commit()

    cursor.execute("SELECT hourly_report.model, COUNT(*) AS Count FROM hourly_report GROUP BY hourly_report.model ORDER BY Count ASC")
    rows = cursor.fetchall() 
    for row in rows: 
        print(rows)
        cursor.execute(""" INSERT INTO model_report (model, numb)
        VALUES (%s, %s)""", row)
        
    conn.commit()

    cursor.close()
    conn.close()
    
    logging.info("stop processing")


if __name__ == "__main__":
    process_data()








