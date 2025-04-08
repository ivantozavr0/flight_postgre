# flight_postgre
## Информация о представляемой программе:
- Данная программа отслеживает авиамаршруты над акваторией Черного моря, загружая информацию через FlightRadar24 API
- Полученная информация используется для составления отчета обо всех маршрутах за последний час (или с момента запуска программы) и для составления отсчетов о количестве рейсов в зависимости от моделей самолетов и авиалиний
- Вся информация будет доступна в графическом представлении на дашборде по порту 8070 (откройте в браузере страницу "http://localhost:8070"). Освободите этот порт предварительно!
- Загрузка данных производится каждые 3.5 минуты, т.к. во избежание блокировки IP-адреса приходится делать задержки в отправке запросов
- Дашборд автоматически обновляется каждые 3 минуты 
- Не для коммерческого использования!

## Требования к пользователю
- Установленный на вашей машине Docker и docker-compose
- Запустите программу после скачивания командой "docker compose up -d"
- !!! БД использует порт по умолчанию (5432), освободите его!
- !!! Дашборд использует порт 8070, освободите его!

## Техническая реализация
- После запуска программы будет развернут контейнер с базой данных PostgreSQL
- Работой программы управляют 4 скрипта &mdash; collector.py (парсинг данных), processing.py (формирование отчетов), dashboard.py (вывод на дашборд графических данных &mdash; карты с маршрутами за последний час и столбчатых диаграмм с распределением самолетов по моделям и авиалиниям), main.py &mdash; запускает фоновый процесс dashboard.py и периодически запускает парсинг и обработку данных
## Модель данных - смотрите файл Model.md
