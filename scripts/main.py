import time
import schedule
import subprocess
from signal import signal, SIGINT
import logging

# переменная для фонового процесса - дашборда
dashboard_process = None

#логирование
logging.basicConfig(
    filename='logs/main.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def run_data_job():
    """запуск только сбора и обработки данных"""
    try:
        logging.info("Starting collector")
        subprocess.run(['python', 'scripts/collector.py'], check=True)
        logging.info("Starting processing")
        subprocess.run(['python', 'scripts/processing.py'], check=True)
    except subprocess.CalledProcessError as e:
        logging.info(f"Ошибка в задаче: {e}")
        print(f"Ошибка в задаче: {e}")

def start_dashboard():
    """запуск дашборда в отдельном фоновом процессе"""
    global dashboard_process
    dashboard_process = subprocess.Popen(
        ['python', 'scripts/dashboard.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def shutdown(signal_received, frame):
    """обработка завершения работы"""
    if dashboard_process:
        dashboard_process.terminate()
    exit(0)

def main():

    logging.info("Starting application")

    # время между сборами информации
    time_to_wait = 3.5
    
    print("\033[1;37;40m \n----Вы начали выполнение мониторинга полетов над Черным морем")
    print(f"\033[1;37;40m ----Ожидание между обновлениями данных составит {time_to_wait} минут.")
    print("\033[1;36;40m Дашборд доступен по порту 8030")
    print(f"\033[1;37;40m ----Дашборд будет обновляться каждые 2.5 минуты \n")
    signal(SIGINT, shutdown)  # Обработка Ctrl+C
    
    # первоначальный запуск
    start_dashboard()
    
    #time.sleep(45)
    
    run_data_job()  # Первый сбор данных
    
    # настройка расписания
    schedule.every(time_to_wait).minutes.do(run_data_job)
   
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
    
    
    
    
    
