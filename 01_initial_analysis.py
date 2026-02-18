
# Первичный анализ датасетов

import pandas as pd
import os

# Проверяем, где мы находимся
print("Текущая папка:", os.getcwd())

# Загружаем датасеты
try:
    ecom = pd.read_csv('data/raw/ecommerce_data.csv')
    print("E-commerce датасет загружен")
except FileNotFoundError:
    print("Ошибка: не найден файл ecommerce_data.csv в папке data/raw/")
    ecom = None

try:
    telco = pd.read_csv('data/raw/telco_data.csv')
    print("Telco датасет загружен")
except FileNotFoundError:
    print("Ошибка: не найден файл telco_data.csv в папке data/raw/")
    telco = None

print("АНАЛИЗ E-COMMERCE ДАТАСЕТА")
if ecom is not None:
    # Количество записей и признаков
    print(f"Количество записей (строк): {ecom.shape[0]}")
    print(f"Количество признаков (колонок): {ecom.shape[1]}")
    
    # Названия колонок
    print("\nНазвания колонок:")
    for i, col in enumerate(ecom.columns):
        print(f"  {i+1}. {col}")
    
    # Типы данных
    print("\nТипы данных:")
    print(ecom.dtypes)
    
    # Пропуски
    print("\nПропуски (количество):")
    missing = ecom.isnull().sum()
    missing_percent = (missing / len(ecom)) * 100
    missing_df = pd.DataFrame({
        'Пропусков': missing,
        'Процент': missing_percent
    })
    print(missing_df[missing_df['Пропусков'] > 0])
    
    # Первые строки
    print("\nПервые 5 строк:")
    print(ecom.head())
    
    # Основная статистика
    print("\nОсновная статистика по числовым колонкам:")
    print(ecom.describe())
    
    # Сохраняем сводку в файл
    with open('reports/ecommerce_summary.txt', 'w', encoding='utf-8') as f:
        f.write("E-COMMERCE ДАТАСЕТ - итог\n")
        f.write("=" * 40 + "\n")
        f.write(f"Записей: {ecom.shape[0]}\n")
        f.write(f"Признаков: {ecom.shape[1]}\n")
        f.write(f"\nКолонки: {list(ecom.columns)}\n")
        f.write(f"\nПропуски:\n")
        for col in ecom.columns:
            if ecom[col].isnull().sum() > 0:
                f.write(f"  {col}: {ecom[col].isnull().sum()} пропусков\n")
    
    print("\nСводка сохранена в reports/ecommerce_summary.txt")
else:
    print("Пропускаем анализ e-commerce - файл не загружен")

print("АНАЛИЗ TELCO ДАТАСЕТА")
if telco is not None:
    # Количество записей и признаков
    print(f"Количество записей (строк): {telco.shape[0]}")
    print(f"Количество признаков (колонок): {telco.shape[1]}")
    
    # Названия колонок
    print("\nНазвания колонок:")
    for i, col in enumerate(telco.columns):
        print(f"  {i+1}. {col}")
    
    # Типы данных
    print("\nТипы данных:")
    print(telco.dtypes)
    
    # Пропуски
    print("\nПропуски (количество):")
    missing = telco.isnull().sum()
    missing_percent = (missing / len(telco)) * 100
    missing_df = pd.DataFrame({
        'Пропусков': missing,
        'Процент': missing_percent
    })
    print(missing_df[missing_df['Пропусков'] > 0])
    
    # Первые строки
    print("\nПервые 5 строк:")
    print(telco.head())
    
    # Проверяем целевую переменную Churn
    if 'Churn' in telco.columns:
        print("\nАнализ целевой переменной Churn:")
        print(telco['Churn'].value_counts())
        print(f"Доля ушедших клиентов: {telco['Churn'].value_counts(normalize=True)['Yes']:.1%}")
    else:
        print("\nВнимание: не найдена колонка 'Churn'")
        print("Ищем похожие названия...")
        for col in telco.columns:
            if 'churn' in col.lower():
                print(f"  Возможно, целевая колонка: {col}")
    
    # Сохраняем сводку в файл
    with open('reports/telco_summary.txt', 'w', encoding='utf-8') as f:
        f.write("TELCO ДАТАСЕТ - СВОДКА\n")
        f.write(f"Записей: {telco.shape[0]}\n")
        f.write(f"Признаков: {telco.shape[1]}\n")
        f.write(f"\nКолонки: {list(telco.columns)}\n")
        f.write(f"\nПропуски:\n")
        for col in telco.columns:
            if telco[col].isnull().sum() > 0:
                f.write(f"  {col}: {telco[col].isnull().sum()} пропусков\n")
    
    print("\nСводка сохранена в reports/telco_summary.txt")
else:
    print("Пропускаем анализ telco - файл не загружен")
