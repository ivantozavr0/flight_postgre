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

### 4. models_report.csv (отчет по моделям самолетов)
Структура:
- model VARCHAR(50), &mdash; список всех моделей самолетов
- numb Smallint &mdash; список всех моделей самолетов

## Диаграмма взаимодействия
    A[FlightRadar24 API] --> B[collector.py] 

    B --> C [parse]
    
    C --> D{processing.py}
    
    D --> E[hourly_report]
    
    D --> F[airline_report]
    
    D --> G[model_report]
    
    E --> H[dashboard.py]
    
    F --> G
    
    G --> G
