import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor
from sklearn.svm import SVR
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPRegressor
import joblib
import os

# 1. Etiketli veriyi oku
df_train = pd.read_excel("data/training_data.xlsx")
df_test = pd.read_excel("data/analiz_sonuclari2.xlsx")

# 2. TF-IDF vektörleştirici (sadece özet metinleriyle)
vectorizer = TfidfVectorizer(max_features=2000)
X_train = vectorizer.fit_transform(df_train["ozet"].astype(str))
X_test = vectorizer.transform(df_test["ozet"].astype(str))

varliklar = ["dolar_skor", "altin_skor", "borsa_skor", "bitcoin_skor"]
tahminler_rf = {}
tahminler_svm = {}
tahminler_nb = {}
tahminler_ada = {}
tahminler_ann = {}
ann_models = {}
rf_models = {}
svm_models = {}
nb_models = {}
ada_models = {}

os.makedirs("models", exist_ok=True)

for varlik in varliklar:
    y = df_train[varlik]
    # Random Forest
    model_rf = RandomForestRegressor(n_estimators=100, random_state=42)
    model_rf.fit(X_train, y)
    tahmin_rf = model_rf.predict(X_test)
    tahmin_rf = [min(5, max(0, round(t))) for t in tahmin_rf]
    tahminler_rf[varlik + "_rf"] = tahmin_rf
    rf_models[varlik] = model_rf
    joblib.dump(model_rf, f"models/{varlik}_rf_model.pkl")

    # SVM
    model_svm = SVR()
    model_svm.fit(X_train, y)
    tahmin_svm = model_svm.predict(X_test)
    tahmin_svm = [min(5, max(0, round(t))) for t in tahmin_svm]
    tahminler_svm[varlik + "_svm"] = tahmin_svm
    svm_models[varlik] = model_svm
    joblib.dump(model_svm, f"models/{varlik}_svm_model.pkl")

    # Naive Bayes (NB için dense array gerekir)
    model_nb = GaussianNB()
    model_nb.fit(X_train.toarray(), y)
    tahmin_nb = model_nb.predict(X_test.toarray())
    tahmin_nb = [min(5, max(0, round(t))) for t in tahmin_nb]
    tahminler_nb[varlik + "_nb"] = tahmin_nb
    nb_models[varlik] = model_nb
    joblib.dump(model_nb, f"models/{varlik}_nb_model.pkl")

    # AdaBoost (dense array gerekir)
    model_ada = AdaBoostRegressor(n_estimators=100, random_state=42)
    model_ada.fit(X_train.toarray(), y)
    tahmin_ada = model_ada.predict(X_test.toarray())
    tahmin_ada = [min(5, max(0, round(t))) for t in tahmin_ada]
    tahminler_ada[varlik + "_ada"] = tahmin_ada
    ada_models[varlik] = model_ada
    joblib.dump(model_ada, f"models/{varlik}_ada_model.pkl")

    # ANN (MLPRegressor, dense array gerekir)
    model_ann = MLPRegressor(hidden_layer_sizes=(100,), max_iter=300, random_state=42)
    model_ann.fit(X_train.toarray(), y)
    tahmin_ann = model_ann.predict(X_test.toarray())
    tahmin_ann = [min(5, max(0, round(t))) for t in tahmin_ann]
    tahminler_ann[varlik + "_ann"] = tahmin_ann
    ann_models[varlik] = model_ann
    joblib.dump(model_ann, f"models/{varlik}_ann_model.pkl")

# 3. Sonuçları yeni DataFrame'e ekle
for varlik in varliklar:
    df_test[varlik + "_rf"] = tahminler_rf[varlik + "_rf"]
    df_test[varlik + "_svm"] = tahminler_svm[varlik + "_svm"]
    df_test[varlik + "_nb"] = tahminler_nb[varlik + "_nb"]
    df_test[varlik + "_ada"] = tahminler_ada[varlik + "_ada"]
    df_test[varlik + "_ann"] = tahminler_ann[varlik + "_ann"]

# 4. Eğitim seti güncelleme işlemi overfitting nedeniyle durduruldu
# Test verilerinin eğitim setine eklenmesi overfittinge sebep oluyor
print("Not: Test verilerinin eğitim setine eklenmesi overfitting nedeniyle durduruldu.")

# 5. Tahminli sonuçları kaydet
df_test.to_excel("data/analiz_sonuclari2_tahminli_TF-IDF.xlsx", index=False)
print("Tahminler data/analiz_sonuclari2_tahminli_TF-IDF.xlsx dosyasına kaydedildi.")

# TF-IDF vectorizer'ı da kaydet
joblib.dump(vectorizer, "models/tfidf_vectorizer.pkl")
