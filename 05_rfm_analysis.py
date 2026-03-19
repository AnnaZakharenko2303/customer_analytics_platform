import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

os.makedirs('data/processed', exist_ok=True)
os.makedirs('reports/figures', exist_ok=True)

print("RFM-АНАЛИЗ")

df = pd.read_csv('data/processed/ecommerce_clean.csv')
print(f"Загружено строк: {len(df)}")
print(f"Колонки: {list(df.columns)}")

rfm = df.copy()

# Преобразуем Days Since Last Purchase в числа
def extract_days(value):
    # Если это строка вида "1970-01-01 00:00:00.000000025"
    # то берем последние цифры после точки
    if isinstance(value, str) and '1970' in value:
        try:
            # Разбиваем по точке и берем последнюю часть
            return int(value.split('.')[-1])
        except:
            return 0
    return value

rfm['Days Since Last Purchase'] = rfm['Days Since Last Purchase'].apply(extract_days)

rfm = rfm.rename(columns={
    'Customer ID': 'CustomerID',
    'Days Since Last Purchase': 'Recency',
    'Total Spend': 'Monetary'
})

frequency_df = df.groupby('Customer ID').size().reset_index(name='Frequency')

rfm = pd.merge(rfm, frequency_df, left_on='CustomerID', right_on='Customer ID', how='left')

rfm = rfm[['CustomerID', 'Recency', 'Frequency', 'Monetary']].drop_duplicates()

print(f"Найдено уникальных клиентов: {len(rfm)}")
print("Первые 5 клиентов:")
print(rfm.head())

# Теперь Recency - это числа, можно считать статистику
stats = rfm[['Recency', 'Frequency', 'Monetary']].describe()
print("Описательные статистики:")
print(stats)

with open('reports/rfm_stats.txt', 'w', encoding='utf-8') as f:
    f.write("RFM СТАТИСТИКА\n")
    f.write(stats.to_string())

fig1 = px.histogram(rfm, x='Recency', nbins=30, title='Распределение Recency (дней с последней покупки)', labels={'Recency': 'Дней с последней покупки', 'count': 'Количество клиентов'})
fig1.write_html('reports/figures/rfm_recency.html')
fig1.write_image('reports/figures/rfm_recency.png')
print("Recency распределение сохранено")

fig2 = px.histogram(rfm, x='Frequency', nbins=30, title='Распределение Frequency (количество покупок)', labels={'Frequency': 'Количество покупок', 'count': 'Количество клиентов'})
fig2.write_html('reports/figures/rfm_frequency.html')
fig2.write_image('reports/figures/rfm_frequency.png')
print("Frequency распределение сохранено")

fig3 = px.histogram(rfm, x='Monetary', nbins=30, title='Распределение Monetary (сумма потраченных денег)', labels={'Monetary': 'Сумма', 'count': 'Количество клиентов'})
fig3.write_html('reports/figures/rfm_monetary.html')
fig3.write_image('reports/figures/rfm_monetary.png')
print("Monetary распределение сохранено")

rfm.to_csv('data/processed/rfm_features.csv', index=False)
print(f"RFM таблица сохранена: data/processed/rfm_features.csv")
print(f"Всего клиентов: {len(rfm)}")

r_mean = rfm['Recency'].mean()
r_median = rfm['Recency'].median()
r_min = rfm['Recency'].min()
r_max = rfm['Recency'].max()

f_mean = rfm['Frequency'].mean()
f_max = rfm['Frequency'].max()
one_time = (rfm['Frequency'] == 1).sum()
one_time_pct = (one_time / len(rfm)) * 100

m_mean = rfm['Monetary'].mean()
m_median = rfm['Monetary'].median()
m_min = rfm['Monetary'].min()
m_max = rfm['Monetary'].max()
m_sum = rfm['Monetary'].sum()

print("Анализ распределений:")
print(f"Recency - среднее: {r_mean:.1f} дней, медиана: {r_median:.1f} дней, мин: {r_min}, макс: {r_max}")
print(f"Frequency - среднее: {f_mean:.2f} покупок, максимум: {f_max}, 1 покупка: {one_time} ({one_time_pct:.1f}%)")
print(f"Monetary - общая выручка: {m_sum:.2f}, среднее: {m_mean:.2f}, медиана: {m_median:.2f}, мин: {m_min}, макс: {m_max}")

with open('reports/rfm_conclusions.txt', 'w', encoding='utf-8') as f:
    f.write("ВЫВОДЫ ПО RFM-АНАЛИЗУ\n\n")
    f.write(f"Recency: среднее {r_mean:.1f} дней, медиана {r_median:.1f} дней, от {r_min} до {r_max}\n\n")
    f.write(f"Frequency: среднее {f_mean:.2f} покупок, максимум {f_max}, {one_time_pct:.1f}% с 1 покупкой\n\n")
    f.write(f"Monetary: общая выручка {m_sum:.2f}, среднее {m_mean:.2f}, медиана {m_median:.2f}, от {m_min} до {m_max}\n")

print("RFM-АНАЛИЗ ЗАВЕРШЕН")
print("Результаты в data/processed/rfm_features.csv и reports/figures/")
