# Модель данных

## Источники данных
- FlightRadar24 API - источник сырых данных о рейсах

## База данных &mdash; flightradardb (база данных PostgreSQL, пароль и имя пользователя смотрите в docker-compose.yml) имеет следующие сущности (таблицы):

### 1. parse (сырые данные)
Структура:
- icao VARCHAR(10), &mdash; icao маршрута
- callsign VARCHAR(10) PRIMARY KEY, &mdash; позывной маршрута (считаем его ключевым признаком)
- model VARCHAR(50), &mdash; модель самолета
- airline VARCHAR(50), &mdash; авиалиния
- trail FLOAT[][], &mdash; маршрут самолета
- time TIMESTAMP &mdash; время получения информации

### 2. hourly_report (часовой отчет). Сюда записываются данные за последний час. Если маршрут вышел из акватории Черного моря более часа назад, то он удаляется. 
### Если самолет все еще над Черным морем, то его маршрут обновляется с учетом свежих данных
Структура:
- icao VARCHAR(10), &mdash; icao маршрута
- callsign VARCHAR(10) PRIMARY KEY, &mdash; позывной маршрута (считаем его ключевым признаком)
- model VARCHAR(50), &mdash; модель самолета
- airline VARCHAR(50), &mdash; авиалиния
- trail FLOAT[][], &mdash; маршрут самолета
- time TIMESTAMP &mdash; время получения информации

Правила обновления:
- Данные сохраняются только за последние 60 минут
- Устаревшие записи удаляются каждые 3.5 минуты

### 3. airline_report (отчет по авиакомпаниям)
Структура:
- airline VARCHAR(50), &mdash; список всех авиалиний
- numb Smallint &mdash; количество самолетов, принадлежащих данной авиалинии

### 4. model_report.csv (отчет по моделям самолетов)
Структура:
- model VARCHAR(50), &mdash; список всех моделей самолетов
- numb Smallint &mdash; список всех моделей самолетов

## ER-диаграмма

[![er-db.png](https://i.postimg.cc/sxVGts7h/er-db.png)](https://postimg.cc/S2vK90ZS)

## Диаграмма взаимодействия
    A[main.py] --> B[collector.py] 
    A --> C[processing.py]
    A --> D[dashboard.py]
    E[FlightRadar24 API] --> B
    
    B --> F [parse]
    
    F --> C
    
    C --> G[hourly_report]
    
    C --> H[airline_report]
    
    C --> I[model_report]
    
    G --> D
    
    H --> D
    
    I --> D
