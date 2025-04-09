-- Создание основной таблицы для сырых данных
CREATE TABLE IF NOT EXISTS parse (
    icao VARCHAR(10),
    callsign VARCHAR(10) PRIMARY KEY,
    model VARCHAR(50),
    airline VARCHAR(50),
    trail FLOAT[][],
    time TIMESTAMP
);

-- Таблица для часовых отчетов
CREATE TABLE IF NOT EXISTS hourly_report (
    icao VARCHAR(10),
    callsign VARCHAR(10) PRIMARY KEY,
    model VARCHAR(50),
    airline VARCHAR(50),
    trail FLOAT[][],
    time TIMESTAMP
);

-- Таблица отчетов по авиакомпаниям
CREATE TABLE IF NOT EXISTS airline_report (
    airline VARCHAR(50),
    numb Smallint
);

-- Таблица отчетов по моделям самолетов
CREATE TABLE IF NOT EXISTS model_report (
    model VARCHAR(50),
    numb Smallint
);
