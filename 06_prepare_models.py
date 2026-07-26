import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# проверка колонок с категориями
print("проверка наличия категорий товаров")
ecom = pd.read_csv('data/processed/ecommerce_clean.csv')
category_cols = [col for col in ecom.columns if 'category' in col.lower() or 'product' in col.lower()]
print(f"колонки с категориями: {category_cols}")
if category_cols:
    print(f"пример категорий: {ecom[category_cols[0]].unique()[:5]}")
else:
    print("категорий товаров в датасете нет")

# e-commerce: масштабирование rfm и создание целевой метки
print("e-commerce: масштабирование rfm и создание целевой метки")
rfm = pd.read_csv('data/processed/rfm_features.csv')

scaler = StandardScaler()
rfm_scaled = rfm.copy()
rfm_scaled[['Recency', 'Frequency', 'Monetary']] = scaler.fit_transform(rfm[['Recency', 'Frequency', 'Monetary']])

threshold = rfm['Recency'].quantile(0.9)
rfm_scaled['is_churn'] = (rfm['Recency'] > threshold).astype(int)

rfm_scaled.to_csv('data/processed/ecommerce_prepared.csv', index=False)
print(f"порог оттока (90-й перцентиль recency): {threshold:.1f} дней")
print(f"клиентов с оттоком: {rfm_scaled['is_churn'].sum()} из {len(rfm_scaled)}")

# telco: выделение целевой переменной churn
print("telco: выделение целевой переменной churn")
telco = pd.read_csv('data/processed/telco_clean.csv')

if 'Churn' in telco.columns:
    y = telco['Churn']
    X = telco.drop('Churn', axis=1)
    print(f"распределение churn: {y.value_counts().to_dict()}")
else:
    print("колонка churn не найдена")
    exit()

# telco: кодирование категориальных признаков
print("telco: кодирование категориальных признаков")
categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
print(f"категориальные колонки: {categorical_cols}")

X_encoded = pd.get_dummies(X, columns=categorical_cols, drop_first=True)
print(f"после кодирования: {X_encoded.shape[1]} признаков")

# telco: масштабирование числовых признаков
print("telco: масштабирование числовых признаков")
numeric_cols = X_encoded.select_dtypes(include=['int64', 'float64']).columns.tolist()
print(f"числовые колонки: {numeric_cols}")

scaler = StandardScaler()
X_scaled = X_encoded.copy()
X_scaled[numeric_cols] = scaler.fit_transform(X_encoded[numeric_cols])

# telco: разделение на train/test
print("telco: разделение на train/test (70/30)")
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.3, random_state=42, stratify=y
)

print(f"train: {len(X_train)} записей")
print(f"test: {len(X_test)} записей")
print(f"churn в train: {y_train.value_counts(normalize=True).to_dict()}")

# сохранение
X_train.to_csv('data/processed/telco_X_train.csv', index=False)
X_test.to_csv('data/processed/telco_X_test.csv', index=False)
y_train.to_csv('data/processed/telco_y_train.csv', index=False)
y_test.to_csv('data/processed/telco_y_test.csv', index=False)

print("готово. сохранены файлы:")
print("  - data/processed/ecommerce_prepared.csv")
print("  - data/processed/telco_X_train.csv")
print("  - data/processed/telco_X_test.csv")
print("  - data/processed/telco_y_train.csv")
print("  - data/processed/telco_y_test.csv")
