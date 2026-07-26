import pandas as pd
import numpy as np
import joblib
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import matplotlib.pyplot as plt
import os

os.makedirs('models', exist_ok=True)
os.makedirs('reports/figures', exist_ok=True)

print("спринт 7: обучение моделей")
print("\n1. загрузка данных")
ecom = pd.read_csv('data/processed/ecommerce_prepared.csv')
X_train = pd.read_csv('data/processed/telco_X_train.csv')
X_test = pd.read_csv('data/processed/telco_X_test.csv')
y_train = pd.read_csv('data/processed/telco_y_train.csv').values.ravel()
y_test = pd.read_csv('data/processed/telco_y_test.csv').values.ravel()

print(f"  e-commerce клиентов: {len(ecom)}")
print(f"  telco train: {len(X_train)}, test: {len(X_test)}")


# k-means на rfm признаках
print("\n2. обучение k-means")
rfm_scaled = ecom[['Recency', 'Frequency', 'Monetary']].values

# метод локтя для выбора k
inertia = []
k_range = range(1, 11)
for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(rfm_scaled)
    inertia.append(kmeans.inertia_)

# график метода локтя
plt.figure(figsize=(8, 5))
plt.plot(k_range, inertia, 'bo-')
plt.xlabel('k')
plt.ylabel('инерция')
plt.title('метод локтя для выбора k')
plt.savefig('reports/figures/elbow_method.png')
plt.show()
print("  график метода локтя сохранен")

# выбираем оптимальное k (например, 3 или 4)
optimal_k = 4
kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
ecom['cluster'] = kmeans.fit_predict(rfm_scaled)

print(f"  оптимальное k: {optimal_k}")
print(f"  распределение по кластерам:\n{ecom['cluster'].value_counts().sort_index()}")

# анализ сегментов
segment_means = ecom.groupby('cluster')[['Recency', 'Frequency', 'Monetary']].mean()
print("\n  средние значения по кластерам:")
print(segment_means)

# сохраняем модель
joblib.dump(kmeans, 'models/kmeans.pkl')
print("  модель kmeans.pkl сохранена")

# random forest на telco
classes = np.unique(y_train)
weights = compute_class_weight('balanced', classes=classes, y=y_train)
class_weight = dict(zip(classes, weights))
print(f"  веса классов: {class_weight}")

rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    class_weight=class_weight,
    random_state=42
)
rf.fit(X_train, y_train)

y_pred = rf.predict(X_test)

acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred, pos_label='Yes')
rec = recall_score(y_test, y_pred, pos_label='Yes')
f1 = f1_score(y_test, y_pred, pos_label='Yes')
cm = confusion_matrix(y_test, y_pred)

print(f"  accuracy: {acc:.4f}")
print(f"  precision: {prec:.4f}")
print(f"  recall: {rec:.4f}")
print(f"  f1-score: {f1:.4f}")
print(f"\n  матрица ошибок:")
print(cm)

# сохраняем новую модель
joblib.dump(rf, 'models/rf_churn.pkl')
print("  модель rf_churn.pkl сохранена")
print("  модель rf_churn.pkl сохранена")

print("\n4. сохранение результатов")
ecom[['CustomerID', 'Recency', 'Frequency', 'Monetary', 'cluster', 'is_churn']].to_csv('data/processed/ecommerce_with_segments.csv', index=False)
print("  ecommerce_with_segments.csv сохранен")

# сохраняем метрики в файл
with open('reports/model_metrics.txt', 'w') as f:
    f.write("метрики random forest на telco\n")
    f.write(f"accuracy: {acc:.4f}\n")
    f.write(f"precision: {prec:.4f}\n")
    f.write(f"recall: {rec:.4f}\n")
    f.write(f"f1-score: {f1:.4f}\n\n")
    f.write("матрица ошибок:\n")
    f.write(str(cm))

print("\nготово. модели сохранены в папке models/")
print("  - models/kmeans.pkl")
print("  - models/rf_churn.pkl")
