import requests
import time
from datetime import datetime, timedelta
import pandas as pd
from retrying import retry

API_KEY = 'I83BX4NV4JGIG618UFF9VCDPNGFI8PFJB8'

# Функции получения списка транзакций за определенный период в сети блокчейн

def get_block_number_by_timestamp(timestamp):
    
    # Получить номер блока по метке времени.
    # Args:
    # - timestamp (int): Метка времени для запроса.
    # Returns:
    # - int: Номер блока.
    
    url = f'https://api.etherscan.io/api?module=block&action=getblocknobytime&timestamp={timestamp}&closest=before&apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    if data['status'] == '1':
        return int(data['result'])
    else:
        raise ValueError(f"Ошибка получения номера блока: {data['message']} (код ошибки: {data['status']}")

@retry(stop_max_attempt_number=10, wait_fixed=3000)
def get_transactions_by_block_range(start_block, end_block, max_addresses):
    
    # Получить список транзакций между двумя блоками.

    # Args:
    # - start_block (int): Начальный блок для запроса.
    # - end_block (int): Конечный блок для запроса.
    # - max_addresses (int): Максимальное количество адресов.

    # Returns:
    # - list: Список адресов транзакций.
    
    time.sleep(0.5)
    addresses = []
    current_block = start_block

    while True:
        url = f'https://api.etherscan.io/api?module=account&action=txlistinternal&startblock={current_block}&endblock={end_block}&sort=asc&apikey={API_KEY}'
        try:
            response = requests.get(url)
            response.raise_for_status()  # Проверка наличия ошибок в ответе
            data = response.json()

            if data['status'] == '1' and data['result']:
                addresses.extend(tx['from'] for tx in data['result'])
                current_block = int(data['result'][-1]['blockNumber']) + 1  # Устанавливаем следующий блок для запроса

                if len(addresses) >= max_addresses:
                    addresses = addresses[:max_addresses]
                    break
            else:
                print(f"Ошибка получения транзакций: {data['message']} (код ошибки: {data['status']}), блок {current_block}")
                break
            
            if current_block > end_block:
                break

            time.sleep(1)  # Увеличиваем задержку между запросами
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            time.sleep(2)  # Увеличиваем время ожидания перед повторной попыткой

    return addresses

def get_transactions_in_time_range(min):
    
    # Получить список транзакций за последние `hours` часов.

    # Args:
    # - hours (int): Количество минут для анализа.

    # Returns:
    # - list: Список адресов транзакций.
    
    end_time = int(time.time())
    start_time = end_time - (min * 60)  # 60 секунд в минуте

    try:
        end_block = get_block_number_by_timestamp(end_time)
        start_block = get_block_number_by_timestamp(start_time)
    except ValueError as e:
        print(e)
        return []

    transactions = []
    block_step = 10000  # Количество блоков в одном запросе (регулируйте по необходимости)

    for block in range(start_block, end_block, block_step):
        current_end_block = min(block + block_step - 1, end_block)
        try:
            block_transactions = get_transactions_by_block_range(block, current_end_block, 300)
            transactions.extend(block_transactions)
            time.sleep(1)
        except ValueError as e:
            print(e)
            continue

    return transactions

###########################################################################################################

# Функции для расчета основных показателей RFM анализа

def get_balance(address):
    # Получить текущий баланс кошелька в ETH.
    url = f'https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={API_KEY}'
    response = requests.get(url)
    
    if response.status_code == 502:
        print('Ошибка при выполнении запроса: 502')
        return None

    if response.status_code == 200:
        data = response.json()
        if data['status'] == '1':
            balance = int(data['result']) / (10 ** 18)  # Баланс возвращается в Wei, конвертируем в Ether
            return balance
        else:
            print('Ошибка в ответе API:', data['message'])
    else:
        print('Ошибка при выполнении запроса:', response.status_code)

def get_transactions(address):
    # Получить список всех транзакций для заданного кошелька.
    url = f'https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey={API_KEY}'
    response = requests.get(url)
    
    if response.status_code == 502:
        print('Ошибка при выполнении запроса: 502')
        return []

    if response.status_code == 200:
        data = response.json()
        if data['status'] == '1':
            transactions = data['result']
            return transactions
        else:
            print('Ошибка в ответе API:', data['message'])
    else:
        print('Ошибка при выполнении запроса:', response.status_code)

def get_last_transaction_date(transactions):
    # Получить дату последней транзакции.
    if transactions:
        last_tx_date = datetime.fromtimestamp(int(transactions[0]['timeStamp'])).strftime('%Y-%m-%d %H:%M:%S')
        return last_tx_date
    else:
        return None

def calculate_average_tx_per_month(transactions):
    # Рассчитать среднее количество транзакций в месяц.
    if not transactions:
        return 0
    
    first_tx_date = datetime.fromtimestamp(int(transactions[0]['timeStamp']))
    last_tx_date = datetime.fromtimestamp(int(transactions[-1]['timeStamp']))
    
    total_months = (last_tx_date.year - first_tx_date.year) * 12 + last_tx_date.month - first_tx_date.month + 1
    total_transactions = len(transactions)
    
    average_tx_per_month = total_transactions / total_months
    return average_tx_per_month

def calculate_average_volume_last_month(transactions):
    # Рассчитать средний объем переводимых средств за последний месяц.
    if not transactions:
        return 0
    
    total_volume = sum(int(tx['value']) for tx in transactions)
    average_volume = total_volume / len(transactions) / (10 ** 18)  # Конвертация из Wei в ETH
    return average_volume

###########################################################################################################

# Пример использования для получения транзакций за последнюю минуту
min = 1  # 1 минута
transactions = get_transactions_in_time_range(min)

# Создаем пустой список для сбора данных
data = []

# Заполнение списка информацией
for address in transactions:
    balance = get_balance(address)
    time.sleep(1)
    address_transaction = get_transactions(address)
    time.sleep(1)
    last_tx_date = get_last_transaction_date(address_transaction)
    time.sleep(1)
    average_tx_per_month = calculate_average_tx_per_month(address_transaction)
    time.sleep(1)
    average_volume_last_month = calculate_average_volume_last_month(address_transaction)
    time.sleep(1)

    # Создаем словарь для текущей транзакции
    tx_data = {
        'Адрес кошелька': address,
        'Текущий баланс в ETH': balance,
        'Дата последней транзакции': last_tx_date,
        'Среднее количество транзакций в месяц в ETH': average_tx_per_month,
        'Средний объем транзакции в ETH': average_volume_last_month
    }

    # Добавляем словарь в список
    data.append(tx_data)

# Создаем DataFrame из списка
df = pd.DataFrame(data)
print(df)

# Указываем путь к файлу, куда сохранить CSV
csv_filename = 'transactions_data.csv'

# Сохраняем DataFrame в CSV файл
df.to_csv(csv_filename, index=False)

print(f"DataFrame сохранен в файл {csv_filename}")