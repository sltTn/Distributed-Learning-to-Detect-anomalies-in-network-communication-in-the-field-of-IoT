# -*- coding: utf-8 -*-
"""GPU_diverse classifiers.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1AA7-z2Y2lbxlL_Lpwx4ixj1Exhq3UbqE
"""

import time
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report,confusion_matrix,accuracy_score,precision_recall_fscore_support
from sklearn.metrics import f1_score
from sklearn.ensemble import RandomForestClassifier,ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier
import xgboost as xgb
from xgboost import plot_importance
from imblearn.over_sampling import SMOTE
import imageio
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
import os.path
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from google.colab import drive

def label_decoder(labels, encoder):
  return encoder.inverse_transform(labels)

def visualize(y_test, y_predict, name):
  precision, recall, fscore, none = precision_recall_fscore_support(y_test, y_predict, average='weighted')
  print('Precision:\t'+(str(precision)))
  print('Recall: \t'+(str(recall)))
  print('F1-score:\t'+(str(fscore))+'\n')
  print(classification_report(y_test, y_predict))
  cm=confusion_matrix(y_test, y_predict)
  f,ax=plt.subplots(figsize=(7,7))
  sns.heatmap(cm,annot=True,linewidth=0.5,linecolor="green",fmt=".0f",ax=ax, cmap="Blues")
  plt.xlabel("Predictions")
  plt.ylabel("True labels")
  ax.tick_params(axis='both', which='major', labelsize=9)
  ax.xaxis.set_ticklabels(np.unique(y_test));
  ax.yaxis.set_ticklabels(np.unique(y_predict));
  plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
  plt.setp(ax.get_yticklabels(), rotation=45, ha="right", rotation_mode="anchor")
  plt.gcf().savefig(f'{OUTPUT_PATH}/{name}')
  return precision, recall, fscore

MAIN_PATH   = '/content/gdrive/MyDrive/CICIDS_DATASETS'
OUTPUT_PATH = f'{MAIN_PATH}/Output/Diverse_Classifiers'

#Read dataset and mount dataset in google drive
drive.mount('/content/gdrive')
df = pd.read_csv(f'{MAIN_PATH}/df.csv')

pd.Series(df['Label']).value_counts()

# Replacing data labels and making dataset better.replace("DDoS","DoS", inplace=True)
df.replace("Heartbleed","DoS", inplace=True)
df.replace("DDoS","DoS", inplace=True)
df.replace("DoS Hulk","DoS", inplace=True)
df.replace("DoS GoldenEye","DoS", inplace=True)
df.replace("DoS slowloris","DoS", inplace=True)
df.replace("DoS Slowhttptest","DoS", inplace=True)
df.replace("Web Attack � Brute Force","Web Attack", inplace=True)
df.replace("Web Attack � Sql Injection","Web Attack", inplace=True)
df.replace("Web Attack � XSS","Web Attack", inplace=True)
df.replace("FTP-Patator","Brute-Force", inplace=True)
df.replace("SSH-Patator","Brute-Force", inplace=True)

# Min-max normalization
numeric_features = df.dtypes[df.dtypes != 'object'].index
df[numeric_features] = df[numeric_features].apply(
    lambda x: (x - x.min()) / (x.max()-x.min()))
# Fill empty values by 0
df = df.fillna(0)

labelencoder = LabelEncoder()
df.iloc[:, -1] = labelencoder.fit_transform(df.iloc[:, -1])
X = df.drop(['Label'],axis=1).values
y = df.iloc[:, -1].values.reshape(-1,1)
y=np.ravel(y)
X_train, X_test, y_train, y_test = train_test_split(X,y, train_size = 0.8, test_size = 0.2, random_state = 0,stratify = y)

pd.Series(y_train).value_counts()

from imblearn.over_sampling import SMOTE
smote=SMOTE(n_jobs=-1,sampling_strategy={4:1500}) # Create 1500 samples for the minority class "4"

X_train, y_train = smote.fit_resample(X_train, y_train)
y_dec_true= label_decoder(y_test, labelencoder)

# Decision tree training and prediction
dt = DecisionTreeClassifier(random_state = 0)

start = time.time()
dt.fit(X_train,y_train)
DT_duration_of_training_time = time.time() - start

start = time.time()
y_predict_dt = dt.predict(X_test)
dt_preditct_duration = time.time() - start

y_dec_pred = label_decoder(y_predict_dt, labelencoder)
precision_dt, recall_dt, fscore_dt = visualize(y_dec_true, y_dec_pred, 'diverse-DT.png')

# Random Forest training and prediction
rf = RandomForestClassifier(random_state = 0)

start = time.time()
rf.fit(X_train, y_train)
rf_duration_training= time.time() - start

start = time.time()
y_predict_rf=rf.predict(X_test)
rf_time_prediction = time.time()- start

y_dec_pred = label_decoder(y_predict_rf, labelencoder)
precision_rf, recall_rf, fscore_rf = visualize(y_dec_true, y_dec_pred, 'diverse-RF.png')

# Extra trees training and prediction
et = ExtraTreesClassifier(random_state = 0)

start = time.time()
et.fit(X_train, y_train)
et_teraining = time.time() - start

start = time.time()
y_predict_et = et.predict(X_test)
et_prediction = time.time() - start

y_dec_pred = label_decoder(y_predict_et, labelencoder)
precision_et, recall_et, fscore_et = visualize(y_dec_true, y_dec_pred, 'diverse-ET.png')

# XGboost training and prediction
xg = xgb.XGBClassifier(n_estimators = 10)

start = time.time()
xg.fit(X_train,y_train)
xg_training = time.time() - start

start = time.time()
y_predict_xg = xg.predict(X_test)
xg_prediction = time.time() - start

y_dec_pred = label_decoder(y_predict_xg, labelencoder)
precision_xg, recall_xg, fscore_xg = visualize(y_dec_true, y_dec_pred, 'diverse-XGBoost.png')

#  k-Nearest Neighbors (kNN) training and prediction
classifier = KNeighborsClassifier(n_neighbors=3)

start = time.time()
classifier.fit(X_train, y_train)
knn_training= time.time() - start

start = time.time()
y_predict_knn = classifier.predict(X_test)
knn_prediction = time.time() -  start

y_dec_pred = label_decoder(y_predict_knn, labelencoder)
precision_knn, recall_knn, fscore_knn = visualize(y_dec_true, y_dec_pred, 'diverse-KNN.png')

dt_score = np.round(accuracy_score(y_test, y_predict_dt), 5)*100
rf_score = np.round(accuracy_score(y_test, y_predict_rf), 5)*100
et_score = np.round(accuracy_score(y_test, y_predict_et), 5)*100
xg_score = np.round(accuracy_score(y_test, y_predict_xg), 5)*100
kn_score = np.round(accuracy_score(y_test, y_predict_knn), 5)*100

duriations = [f'{datetime.now()}',
               '=====================================',
              'Decison Tree Information',
              f'DT Training Time: {DT_duration_of_training_time} sec',
              f'DT Prediction Time: {dt_preditct_duration}sec',
              f'DT Accuracy:{dt_score}%',
               f'DT Recall:{recall_dt}',
              f'DT F1-Score: {fscore_dt}',
              f'DT precision: {precision_dt}',
              '=====================================',
                'Random Forest Information',
             f'RF Training Time: { rf_duration_training} sec',
              f'RF Prediction Time: {rf_time_prediction}sec',
              f'RF Accuracy:{rf_score}%',
               f'RF Recall:{recall_rf}',
              f'RF F1-Score: {fscore_rf}',
              f'RF precision: {precision_rf}',
              '=====================================',
                  ' Extra Trees Information',
             f'ET Training Time: { et_teraining} sec',
              f'ET Prediction Time: {et_prediction}sec',
              f'ET Accuracy:{et_score}%',
               f'ET Recall:{recall_et}',
              f'ET F1-Score: {fscore_et}',
              f'ET precision: {precision_et}',
              '=====================================',
             ' XGboost Information',
             f'XG Training Time: { xg_training} sec',
              f'XG Prediction Time: {xg_prediction}sec',
              f'XG Accuracy:{xg_score}%',
               f'XG Recall:{recall_xg}',
              f'XG F1-Score: {fscore_xg}',
              f'XG precision: {precision_xg}',
             '=====================================' ,
              ' KNN Information',
             f'KNN Training Time: { knn_training} sec',
              f'KNN Prediction Time: {knn_prediction}sec',
              f'KNN Accuracy:{kn_score}%',
               f'KNN Recall:{recall_knn}',
              f'KNN F1-Score: {fscore_knn}',
              f'KNN precision: {precision_knn}', ]


file_path = f'{OUTPUT_PATH}/Duration_of_diverse_classifier.txt'
writing_mode = 'w' if os.path.exists(OUTPUT_PATH) else 'a'
with open(file_path, writing_mode) as f:
    f.writelines('\n'.join(duriations))