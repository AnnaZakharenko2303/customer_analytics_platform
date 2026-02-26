import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Создаем папку для графиков
os.makedirs('reports/figures', exist_ok=True)

ecom = pd.read_csv('data/processed/ecommerce_clean.csv')
telco = pd.read_csv('data/processed/telco_clean.csv')

# Ищем колонки
product_col = next((col for col in ecom.columns if 'product' in col.lower() or 'stock' in col.lower() or 'item' in col.lower()), ecom.columns[0])
qty_col = next((col for col in ecom.columns if 'qty' in col.lower() or 'quantity' in col.lower()), None)

if qty_col:
    top_products = ecom.groupby(product_col)[qty_col].sum().sort_values(ascending=False).head(10).reset_index()
    fig = px.bar(top_products, x=product_col, y=qty_col, title='Топ-10 товаров по количеству продаж')
    fig.write_html('reports/figures/top_products.html')
    fig.write_image('reports/figures/top_products.png')
    print("✓ Топ-10 товаров: сохранено")

customer_col = next((col for col in ecom.columns if 'customer' in col.lower() and 'id' in col.lower()), None)
invoice_col = next((col for col in ecom.columns if 'invoice' in col.lower() or 'order' in col.lower()), None)

if customer_col and invoice_col:
    purchases_per_customer = ecom.groupby(customer_col)[invoice_col].nunique().reset_index()
    purchases_per_customer.columns = [customer_col, 'purchase_count']
    
    fig = px.histogram(purchases_per_customer, x='purchase_count', nbins=30, 
                       title='Распределение количества покупок на клиента',
                       labels={'purchase_count': 'Количество покупок', 'count': 'Количество клиентов'})
    fig.write_html('reports/figures/purchases_distribution.html')
    fig.write_image('reports/figures/purchases_distribution.png')
    print("✓ Распределение покупок: сохранено")

date_col = next((col for col in ecom.columns if 'date' in col.lower() or 'time' in col.lower() or 'day' in col.lower()), None)
amount_col = next((col for col in ecom.columns if 'amount' in col.lower() or 'total' in col.lower() or 'price' in col.lower() or 'spend' in col.lower()), None)

if date_col and amount_col:
    ecom[date_col] = pd.to_datetime(ecom[date_col])
    ecom['Month'] = ecom[date_col].dt.to_period('M').astype(str)
    monthly_sales = ecom.groupby('Month')[amount_col].sum().reset_index()
    
    fig = px.line(monthly_sales, x='Month', y=amount_col, markers=True,
                  title='Динамика продаж по месяцам',
                  labels={'Month': 'Месяц', amount_col: 'Сумма продаж'})
    fig.write_html('reports/figures/monthly_sales.html')
    fig.write_image('reports/figures/monthly_sales.png')
    print("✓ Динамика продаж: сохранено")

if customer_col and amount_col:
    top_customers = ecom.groupby(customer_col)[amount_col].sum().sort_values(ascending=False).head(10).reset_index()
    top_customers[customer_col] = top_customers[customer_col].astype(str)
    
    fig = px.bar(top_customers, x=customer_col, y=amount_col, 
                 title='Топ-10 клиентов по сумме потраченных денег')
    fig.write_html('reports/figures/top_customers.html')
    fig.write_image('reports/figures/top_customers.png')
    print("✓ Топ-10 клиентов: сохранено")

if 'Churn' in telco.columns:
    churn_counts = telco['Churn'].value_counts().reset_index()
    churn_counts.columns = ['Churn', 'count']
    
    fig = px.pie(churn_counts, values='count', names='Churn', 
                 title='Распределение оттока клиентов',
                 hole=0.3)
    fig.write_html('reports/figures/churn_pie.html')
    fig.write_image('reports/figures/churn_pie.png')
    print("✓ Распределение Churn: сохранено")

contract_col = next((col for col in telco.columns if 'contract' in col.lower()), None)
if contract_col and 'Churn' in telco.columns:
    contract_churn = telco.groupby(contract_col)['Churn'].value_counts(normalize=True).reset_index()
    contract_churn.columns = [contract_col, 'Churn', 'proportion']
    
    fig = px.bar(contract_churn, x=contract_col, y='proportion', color='Churn',
                 title='Зависимость оттока от типа контракта',
                 labels={contract_col: 'Тип контракта', 'proportion': 'Доля клиентов', 'Churn': 'Отток'},
                 barmode='group')
    fig.write_html('reports/figures/churn_by_contract.html')
    fig.write_image('reports/figures/churn_by_contract.png')
    print("✓ Отток по типу контракта: сохранено")

tenure_col = next((col for col in telco.columns if 'tenure' in col.lower() or 'month' in col.lower()), None)
if tenure_col and 'Churn' in telco.columns:
    fig = make_subplots(rows=1, cols=2, 
                        subplot_titles=('Клиенты, которые остались', 'Клиенты, которые ушли'))
    
    for i, churn_value in enumerate([0, 1] if 0 in telco['Churn'].unique() else ['No', 'Yes']):
        subset = telco[telco['Churn'] == churn_value]
        fig.add_trace(
            go.Histogram(x=subset[tenure_col], nbinsx=30, name=f'Churn={churn_value}'),
            row=1, col=i+1
        )
    
    fig.update_layout(title_text='Распределение длительности обслуживания по оттоку',
                      showlegend=False)
    fig.update_xaxes(title_text="Tenure (месяцы)")
    fig.update_yaxes(title_text="Количество клиентов")
    
    fig.write_html('reports/figures/churn_by_tenure.html')
    fig.write_image('reports/figures/churn_by_tenure.png')
    print("✓ Отток от длительности: сохранено")

print("\n✓ Все графики сохранены в папку reports/figures/")
print("  - HTML файлы можно открыть в браузере (интерактивные)")
print("  - PNG файлы для отчета")
