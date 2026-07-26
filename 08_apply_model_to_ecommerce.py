import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, recall_score

# загрузка данных
ecom_segments = pd.read_csv('data/processed/7 спринт/ecommerce_with_segments.csv', sep=';')
print(f"всего {len(ecom_segments)} клиентов")

# признаки (Recency, Frequency, Monetary)
X = ecom_segments[['Recency', 'Frequency', 'Monetary']]

# целевая метка (is_churn) - мы создали её в спринте 6
y = ecom_segments['is_churn']

print(f"распределение is_churn: {y.value_counts().to_dict()}")

# разделение на train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# обучение модели Random Forest
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# предсказание
y_pred = rf_model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)

print(f"accuracy: {acc:.3f}")
print(f"recall: {rec:.3f}")

# получаем вероятности для всех клиентов
probabilities = rf_model.predict_proba(X)
ecom_segments['churn_probability'] = probabilities[:, 1]

# создаем финальную таблицу
customer_profiles = ecom_segments[['CustomerID', 'Recency', 'Frequency', 'Monetary', 'cluster', 'churn_probability']].copy()
customer_profiles.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary', 'Segment', 'ChurnProbability']

# сохраняем
customer_profiles.to_csv('data/processed/customer_profiles.csv', index=False, sep=';')
print(f"сохранено customer_profiles.csv, {len(customer_profiles)} записей")

# статистика по вероятностям
#print("\nстатистика по вероятностям оттока:")
#print(customer_profiles['ChurnProbability'].describe())

# клиенты с высоким риском (>0.7)
high_risk = customer_profiles[customer_profiles['ChurnProbability'] > 0.7]
high_risk.to_csv('data/processed/high_risk_customers.csv', index=False, sep=';')
print(f"\nклиентов с высоким риском: {len(high_risk)}")

if len(high_risk) == 0:
    # показываем топ-5 самых рискованных
    top5 = customer_profiles.nlargest(5, 'ChurnProbability')
    print("\nтоп-5 клиентов с наибольшим риском:")
    print(top5[['CustomerID', 'Segment', 'ChurnProbability']])

print("\nконец")
