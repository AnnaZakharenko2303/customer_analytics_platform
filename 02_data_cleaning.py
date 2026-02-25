import pandas as pd
import os
from datetime import datetime


print("НАЧАЛО ОЧИСТКИ ДАННЫХ")
print("\n[1] ЗАГРУЗКА ДАННЫХ")

# Загружаем e-commerce
ecom_path = 'data/raw/ecommerce_data.csv'
ecom = pd.read_csv(ecom_path)
print(f"E-commerce: загружено {len(ecom)} строк, {len(ecom.columns)} колонок")

# Загружаем telco
telco_path = 'data/raw/telco_data.csv'
telco = pd.read_csv(telco_path)
print(f"Telco: загружено {len(telco)} строк, {len(telco.columns)} колонок")

print("\n[2] УДАЛЕНИЕ СТРОК БЕЗ CUSTOMER ID")

# E-commerce - ищем колонку с ID
id_columns_ecom = [col for col in ecom.columns if 'customer' in col.lower() and 'id' in col.lower()]
if id_columns_ecom:
    id_col_ecom = id_columns_ecom[0]
    before = len(ecom)
    ecom = ecom.dropna(subset=[id_col_ecom])
    print(f"E-commerce: удалено {before - len(ecom)} строк без {id_col_ecom}")
    print(f"E-commerce: осталось {len(ecom)} строк")
else:
    print("E-commerce: колонка с Customer ID не найдена!")
    print(f"Доступные колонки: {list(ecom.columns)}")

# Telco - обычно customerID
if 'customerID' in telco.columns:
    before = len(telco)
    telco = telco.dropna(subset=['customerID'])
    print(f"Telco: удалено {before - len(telco)} строк без customerID")
    print(f"Telco: осталось {len(telco)} строк")
else:
    print("Telco: колонка customerID не найдена!")

print("\n[3] ОБРАБОТКА ПРОПУСКОВ")

# E-commerce - проверяем пропуски
missing_ecom = ecom.isnull().sum()
missing_ecom = missing_ecom[missing_ecom > 0]
if len(missing_ecom) > 0:
    print("\nПропуски в E-commerce до обработки:")
    for col, count in missing_ecom.items():
        percent = (count / len(ecom)) * 100
        print(f"  {col}: {count} пропусков ({percent:.1f}%)")
    
    # Обрабатываем текстовые колонки
    for col in ecom.select_dtypes(include=['object']).columns:
        if ecom[col].isnull().sum() > 0:
            ecom[col] = ecom[col].fillna('Unknown')
            print(f"  → {col}: заполнено 'Unknown'")
    
    # Обрабатываем числовые колонки
    for col in ecom.select_dtypes(include=['int64', 'float64']).columns:
        if ecom[col].isnull().sum() > 0:
            ecom[col] = ecom[col].fillna(0)
            print(f"  → {col}: заполнено 0")
else:
    print("E-commerce: пропусков нет")

# Telco - проверяем пропуски
missing_telco = telco.isnull().sum()
missing_telco = missing_telco[missing_telco > 0]
if len(missing_telco) > 0:
    print("\nПропуски в Telco до обработки:")
    for col, count in missing_telco.items():
        percent = (count / len(telco)) * 100
        print(f"  {col}: {count} пропусков ({percent:.1f}%)")
    
    # Если пропусков мало - удаляем строки
    before = len(telco)
    telco = telco.dropna()
    print(f"  → удалено {before - len(telco)} строк с пропусками")
else:
    print("Telco: пропусков нет")


print("\n[4] УДАЛЕНИЕ ДУБЛИКАТОВ")
# E-commerce
before = len(ecom)
ecom = ecom.drop_duplicates()
print(f"E-commerce: удалено {before - len(ecom)} дубликатов")
print(f"E-commerce: осталось {len(ecom)} строк")

# Telco
before = len(telco)
telco = telco.drop_duplicates()
print(f"Telco: удалено {before - len(telco)} дубликатов")
print(f"Telco: осталось {len(telco)} строк")

print("\n[5] ПРЕОБРАЗОВАНИЕ ДАТ")

# E-commerce - ищем колонку с датой
date_columns_ecom = [col for col in ecom.columns if any(word in col.lower() for word in ['date', 'time', 'invoice', 'day'])]
if date_columns_ecom:
    date_col = date_columns_ecom[0]
    print(f"E-commerce: найдена колонка {date_col}")
    
    # Пробуем преобразовать
    try:
        # Сохраняем исходный тип для отчета
        original_type = type(ecom[date_col].iloc[0]).__name__
        
        # Пробуем разные форматы
        ecom[date_col] = pd.to_datetime(ecom[date_col], errors='coerce')
        
        # Проверяем, сколько не преобразовалось
        invalid_dates = ecom[date_col].isnull().sum()
        if invalid_dates > 0:
            print(f"  → {invalid_dates} дат не удалось преобразовать (будут удалены)")
            ecom = ecom.dropna(subset=[date_col])
        
        print(f"  → тип данных изменен с {original_type} на datetime")
    except Exception as e:
        print(f"  → ошибка преобразования: {e}")
else:
    print("E-commerce: колонка с датой не найдена")

# Telco - возможно есть даты
date_columns_telco = [col for col in telco.columns if any(word in col.lower() for word in ['date', 'time'])]
if date_columns_telco:
    date_col = date_columns_telco[0]
    print(f"Telco: найдена колонка {date_col}")
    try:
        telco[date_col] = pd.to_datetime(telco[date_col], errors='coerce')
        invalid_dates = telco[date_col].isnull().sum()
        if invalid_dates > 0:
            print(f"  → {invalid_dates} дат не удалось преобразовать")
            telco = telco.dropna(subset=[date_col])
    except:
        print(f"  → не удалось преобразовать {date_col}")


print("\n[6] УДАЛЕНИЕ АНОМАЛИЙ")

# E-commerce - ищем ценовые колонки
price_columns = [col for col in ecom.columns if any(word in col.lower() for word in ['price', 'amount', 'total', 'value', 'spend'])]
if price_columns:
    price_col = price_columns[0]
    before = len(ecom)
    ecom = ecom[ecom[price_col] >= 0]
    print(f"E-commerce: удалено {before - len(ecom)} строк с отрицательной ценой")
    
    # Проверяем на выбросы (опционально)
    q1 = ecom[price_col].quantile(0.25)
    q3 = ecom[price_col].quantile(0.75)
    iqr = q3 - q1
    upper_bound = q3 + 3 * iqr
    
    outliers = len(ecom[ecom[price_col] > upper_bound])
    if outliers > 0:
        print(f"  → найдено {outliers} строк с аномально высокими ценами (> {upper_bound:.0f})")
        # Не удаляем, просто информируем

# Ищем колонки с количеством
qty_columns = [col for col in ecom.columns if any(word in col.lower() for word in ['qty', 'quantity', 'count'])]
if qty_columns:
    qty_col = qty_columns[0]
    before = len(ecom)
    ecom = ecom[ecom[qty_col] > 0]
    print(f"E-commerce: удалено {before - len(ecom)} строк с количеством <= 0")

print("\n[7] СОХРАНЕНИЕ ОЧИЩЕННЫХ ДАННЫХ")

# Создаем папку processed если её нет
os.makedirs('data/processed', exist_ok=True)

# Сохраняем e-commerce
ecom_clean_path = 'data/processed/ecommerce_clean.csv'
ecom.to_csv(ecom_clean_path, index=False)
print(f"E-commerce сохранен: {ecom_clean_path}")
print(f"  → {len(ecom)} строк, {len(ecom.columns)} колонок")

# Сохраняем telco
telco_clean_path = 'data/processed/telco_clean.csv'
telco.to_csv(telco_clean_path, index=False)
print(f"Telco сохранен: {telco_clean_path}")
print(f"  → {len(telco)} строк, {len(telco.columns)} колонок")

print("ИТОГ ОЧИСТКИ ДАННЫХ")
print(f"E-commerce: итоговое количество строк: {len(ecom)}")
print(f"Telco: итоговое количество строк: {len(telco)}")
