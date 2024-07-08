import pandas as pd
from datetime import datetime

# Загрузка данных из CSV-файла с обработкой ошибок
file_path = r'D:\Programming\Python\Ethereum Scan API\RFM analysis\transactions_data_upd.csv'
try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    print(f"Файл не найден: {file_path}")
    exit(1)
except pd.errors.EmptyDataError:
    print("Файл пуст")
    exit(1)
except pd.errors.ParserError:
    print("Ошибка парсинга файла")
    exit(1)

# Преобразование колонки с датой последней транзакции в datetime
df['Дата последней транзакции'] = pd.to_datetime(df['Дата последней транзакции'])

# Текущая дата для расчета давности
start_date = pd.to_datetime('2024-07-06')

# Сегментация по давности транзакции
def get_recency_category(days):
    days = int(days)
    if days <= 1:
        return 1  # Дневная давность
    elif days <= 7:
        return 2  # Недельная давность
    elif days <= 30:
        return 3  # Месячная давность
    elif days <= 90:
        return 4  # Квартальная давность
    elif days >= 365:
        return 6  # Более чем годовая давность 
    else:
        return 5  # Годовая давность

df['Давность в днях'] = (start_date - df['Дата последней транзакции']).dt.days

# Сегментация по среднему количеству транзакций в месяц
def get_frequency_category(avg_tx_per_month):
    avg_tx_per_month = int(avg_tx_per_month)
    if avg_tx_per_month < 5:
        return 1  # Мало
    elif 5 <= avg_tx_per_month < 15:
        return 2  # Ниже среднего
    elif 15 <= avg_tx_per_month < 25:
        return 3  # Средне
    elif 25 <= avg_tx_per_month < 35:
        return 4  # Выше среднего
    else:
        return 5  # Много

# Сегментация по среднему объему транзакций
def get_volume_category(avg_tx_volume):
    avg_tx_volume = int(avg_tx_volume)
    if avg_tx_volume < 1:
        return 1  # Малый объем
    elif 1 <= avg_tx_volume < 5:
        return 2  # Ниже среднего
    elif 5 <= avg_tx_volume < 10:
        return 3  # Средний объем
    elif 10 <= avg_tx_volume < 20:
        return 4  # Выше среднего
    else:
        return 5  # Большой объем

# Вставка новых столбцов
df.insert(df.columns.get_loc('Дата последней транзакции') + 1, 'Давность в днях', df.pop('Давность в днях'))
df.insert(df.columns.get_loc('Давность в днях') + 1, 'Категория давности', df['Давность в днях'].apply(get_recency_category))
df.insert(df.columns.get_loc('Среднее количество транзакций в месяц в ETH') + 1, 'Категория частоты транзакций', df['Среднее количество транзакций в месяц в ETH'].apply(get_frequency_category))
df.insert(df.columns.get_loc('Средний объем транзакции в ETH') + 1, 'Категория объема транзакций', df['Средний объем транзакции в ETH'].apply(get_volume_category))

# Добавление столбца для суммирования значений категорий
df['Сумма категорий'] = df['Категория давности'].astype(str) + df['Категория частоты транзакций'].astype(str) + df['Категория объема транзакций'].astype(str)

# Вывод результатов
print(df[['Адрес кошелька', 'Дата последней транзакции', 'Категория давности', 'Среднее количество транзакций в месяц в ETH', 'Категория частоты транзакций', 'Средний объем транзакции в ETH', 'Категория объема транзакций', 'Сумма категорий']])

# Сохранение результатов в новый CSV-файл
output_file_path = 'segmented_transactions_data.csv'
df.to_csv(output_file_path, index=False)

# Aнализ сегментов

# Считаем количество записей для каждой категории
categories_counts = df['Сумма категорий'].value_counts().sort_index()

# Общее количество записей в столбце 'Сумма категорий'
total_count = df.shape[0]

# Описание категорий по каждому из трех массивов (давность, частота, объем)
recency_descriptions = [
    "Транзакция в последний день",
    "Транзакция в последнюю неделю",
    "Транзакция в последний месяц",
    "Транзакция в последний квартал",
    "Транзакция за последний года",
    "Транзакции более года назад"
]

frequency_descriptions = [
    "Среднее количество транзакций менее 5 в месяц",
    "Среднее количество транзакций от 5 до 14 в месяц",
    "Среднее количество транзакций от 15 до 24 в месяц",
    "Среднее количество транзакций от 25 до 34 в месяц",
    "Среднее количество транзакций более 35 в месяц"
]

volume_descriptions = [
    "Средний объем транзакций менее 1 ETH",
    "Средний объем транзакций от 1 до 4 ETH",
    "Средний объем транзакций от 5 до 9 ETH",
    "Средний объем транзакций от 10 до 19 ETH",
    "Средний объем транзакций более 20 ETH"
]

# Вывод результатов с описаниями на основе цифр категории
for category, count in categories_counts.items():
    recency_cat = int(category[0])  # первая цифра в категории - давность
    frequency_cat = int(category[1])  # вторая цифра в категории - частота
    volume_cat = int(category[2])  # третья цифра в категории - объем
    
    recency_description = recency_descriptions[recency_cat - 1]  # отнимаем 1, так как индексация в массивах начинается с 0
    frequency_description = frequency_descriptions[frequency_cat - 1]
    volume_description = volume_descriptions[volume_cat - 1]
    
    percent = (count / total_count) * 100
    
    print(f"Категория {category}: Количество записей - {count}, Процентное соотношение - {percent:.2f}%")
    print(f"Описание: {recency_description}, {frequency_description}, {volume_description}\n")
    
