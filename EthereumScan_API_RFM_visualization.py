import pandas as pd
import matplotlib.pyplot as plt
from colorama import Fore, Style

# Загрузка данных из CSV-файла
df = pd.read_csv('segmented_transactions_data.csv')

# Преобразование типов для удобства
df['Сумма категорий'] = df['Сумма категорий'].astype(str)
df['Категория давности'] = df['Категория давности'].astype(int)
df['Категория частоты транзакций'] = df['Категория частоты транзакций'].astype(int)
df['Категория объема транзакций'] = df['Категория объема транзакций'].astype(int)

# Описание категорий по каждому из трех массивов (давность, частота, объем)
recency_descriptions = [
    "Транзакции более года назад",
    "Транзакция за последний года",   
    "Транзакция в последний квартал",  
    "Транзакция в последний месяц",   
    "Транзакция в последнюю неделю",   
    "Транзакция в последний день"      
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

# Дополнительные градации для категорий
recency_descriptions_words = [
    "Совершал транзакции более года назад",
    "Редко совершает транзакции",
    "Иногда совершает транзакции",
    "Относительно часто совершает транзакции",
    "Часто совершает транзакции",
    "Очень часто совершает транзакции"
    
]

frequency_descriptions_words = [
    "Мало транзакций в месяц",
    "Немного транзакций в месяц",
    "Умеренное количество транзакций в месяц",
    "Достаточное количество транзакций в месяц",
    "Много транзакций в месяц"
]

volume_descriptions_words = [
    "Малый объем транзакций",
    "Небольшой объем транзакций",
    "Умеренный объем транзакций",
    "Большой объем транзакций",
    "Очень большой объем транзакций"
]

# Замена числовых категорий на описания
# df['Категория давности опис'] = df['Категория давности'].replace(range(1, 7), recency_descriptions)
# df['Категория частоты транзакций опис'] = df['Категория частоты транзакций'].replace(range(1, 6), frequency_descriptions)
# df['Категория объема транзакций опис'] = df['Категория объема транзакций'].replace(range(1, 6), volume_descriptions)

# Aнализ сегментов

# Считаем количество записей для каждой категории
categories_counts = df['Сумма категорий'].value_counts().sort_index(ascending=False)

# Общее количество записей в столбце 'Сумма категорий'
total_count = df.shape[0]

percentages = []
colored_percentages = []

for category, count in categories_counts.items():
    percent = round((count / total_count) * 100, 2)
    percentages.append(percent)

percentages_sorted = sorted(percentages, reverse=True)

total_elements = len(percentages_sorted)
max_value = max(percentages_sorted)
min_value = min(percentages_sorted)
center_index  = int(total_elements / 2)

for percent in percentages_sorted:
    if percent == max_value:
        color = Fore.GREEN + Style.BRIGHT
    elif percent == min_value:
        color = Fore.RED + Style.BRIGHT
    elif percent == center_index:
        color = Fore.YELLOW + Style.BRIGHT
    else:
        index = percentages_sorted.index(percent)
        if index < center_index:  # От максимального к центральному
            s_s = int(center_index / 2)
            if index == s_s:
                color = Fore.GREEN + Style.DIM
            elif index == (s_s+1):
                color = Fore.YELLOW + Style.DIM
            elif index < s_s and index != max_value:
                color = Fore.GREEN + Style.NORMAL
            elif index > s_s + 1 and index != center_index:
                color = Fore.YELLOW + Style.NORMAL
                
        elif index > center_index:  # От центрального к минимальному
            s_s_2 = int(center_index / 2)
            if index == (center_index + s_s_2):
                color = Fore.RED + Style.DIM
            elif index == (center_index + s_s_2 - 1):
                color = Fore.YELLOW + Style.DIM
            elif index < center_index + s_s_2 and index != center_index:
                color = Fore.YELLOW + Style.NORMAL
            elif index > (center_index + s_s_2) + 1 and index != min_value:
                color = Fore.RED + Style.NORMAL
    
    colored_percentages.append((percent, color))
    
def get_color_for_percent(percent, percent_colors):
    try:
        # Находим цвет для данного процентного значения
        for percent_value, color in percent_colors:
            if percent == percent_value:
                return color
        # Если точного соответствия не найдено, можно выбрать ближайший цвет или вернуть стандартный цвет
        return Fore.RESET  # возвращаем стандартный цвет
    except Exception as e:
        print(f"Ошибка при получении цвета: {e}")
        return Fore.RESET  # возвращаем стандартный цвет

# Вывод результатов с описаниями на основе цифр категории
for category, count in categories_counts.items():
    recency_cat = int(category[0])  # первая цифра в категории - давность
    frequency_cat = int(category[1])  # вторая цифра в категории - частота
    volume_cat = int(category[2])  # третья цифра в категории - объем
    
    recency_description = recency_descriptions[recency_cat - 1]  # отнимаем 1, так как индексация в массивах начинается с 0
    frequency_description = frequency_descriptions[frequency_cat - 1]
    volume_description = volume_descriptions[volume_cat - 1]
    
    recency_description_words = recency_descriptions_words[recency_cat - 1]  # отнимаем 1, так как индексация в массивах начинается с 0
    frequency_description_words = frequency_descriptions_words[frequency_cat - 1]
    volume_description_words = volume_descriptions_words[volume_cat - 1]
    
    percent = round((count / total_count) * 100, 2)
    
    # Get color gradient based on percent
    percent_color = get_color_for_percent(percent, colored_percentages)
    
    # Форматированный вывод
    
    print(f"{Style.RESET_ALL}Категория \033[1m{category}\033[0m: Количество записей - {count}, Процентное соотношение - {percent_color}{percent:.2f}%{Style.RESET_ALL}")
    print(f"Описание: {recency_description}, {frequency_description}, {volume_description}")
    print(f"Описание: {recency_description_words}, {frequency_description_words}, {volume_description_words}")

# После цикла, если нужно, сбросим цвет на стандартный
print(Style.RESET_ALL)

# Данные для построения диаграммы пирога
labels = categories_counts.index.astype(str)  # Названия частей пирога (приведены к строковому типу)
sizes = categories_counts.values  # Размеры частей пирога (количество записей)
total_count = df.shape[0]

# Цветовая палитра для диаграммы пирога
colors = plt.cm.Set1.colors  # Пример цветовой палитры Set3

# Устанавливаем порог для отображения меток
threshold = 2.0  # проценты меньше 2% будут скрыты

# Построение диаграммы пирога
plt.figure(figsize=(10, 6))
explode = [0.1] * len(labels)  # Выделение всех частей пирога для акцентирования

def autopct_func(pct):
    return ('%.1f%%' % pct) if pct > threshold else ''

# Скрытие меток категорий с процентами меньше threshold
filtered_labels = [label if (size / total_count * 100) > threshold else '' for label, size in zip(labels, sizes)]

plt.pie(
    sizes, 
    labels=filtered_labels, 
    autopct=autopct_func, 
    startangle=140, 
    colors=colors, 
    explode=explode,
    pctdistance=0.80,  # Расстояние меток процентов от центра
    labeldistance=1.12  # Расстояние меток от центра
)

plt.title('Круговая диаграмма категорий')
plt.axis('equal')  # Сделать круговую диаграмму круглой

# Добавление легенды
plt.legend(labels, loc="upper left", bbox_to_anchor=(1, 1))

plt.show()

# Построение точечной диаграммы с matplotlib
plt.figure(figsize=(10, 6))  # Размер графика
plt.scatter(df['Среднее количество транзакций в месяц в ETH'], df['Средний объем транзакции в ETH'], s=50, alpha=0.7)  # s - размер точек, alpha - прозрачность
plt.title('Точечная диаграмма по частоте и объему транзакций')
plt.xlabel('Среднее количество транзакций в месяц в ETH')
plt.ylabel('Средний объем транзакции в ETH')
# plt.xscale('log')
# plt.yscale('log')
# plt.xlim(0, 5)  # Диапазон значений для оси X
# plt.ylim(0, 0.1)  # Диапазон значений для оси Y
plt.grid(True)  # Включение сетки
plt.tight_layout()  # Улучшение компоновки графика
plt.show()  # Отображение графика в отдельном окне
