#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  5 19:46:11 2021

@author: zmp
"""

import pandas as pd
import argparse

parser = argparse.ArgumentParser(description='Compute feature matrix.')
parser.add_argument("--Positive", help="Positive feature matrix")
parser.add_argument("--Negative", help="Negative feature matrix")
parser.add_argument("--RandomSeed", default=1, type=int, help="RandomSeed for training chromosome selection ")
parser.add_argument("--chrTrainNum", default=1, type=int, help="Number of chromosomes in training set ")
parser.add_argument("--output", help="File output location")


args = parser.parse_args()

seed = args.RandomSeed
chrTrain = args.chrTrainNum



#Load positive and negative matrix
positive = pd.read_csv(args.Positive)
negative = pd.read_csv(args.Negative)


Data = positive.append(negative)

Data[['0','number']] = Data['0'].str.split(':',expand=True)
Data[['number','start']] = Data['number'].str.split('-',expand=True)


chromosomes = ['chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9','chr10',
               'chr11','chr12','chr13','chr14','chr15','chr16','chr17','chr18','chr19',
               'chr20','chr21','chr22','chrX']



import random
random.seed(seed)
chromosomesTrain = random.sample(chromosomes,chrTrain)
print(chromosomesTrain)

Data = Data.drop('number',1)

#Process data into test and training set and scale hits
from sklearn.preprocessing import StandardScaler

DataTrain = Data[Data['0'].isin(chromosomesTrain)]
DataTest = Data[~Data['0'].isin(chromosomesTrain)]



scaler = StandardScaler()


y_train = DataTrain.Class
DataTrain = DataTrain.drop('0',1)
X_train = DataTrain.drop('Class',1)
X_train = scaler.fit_transform(X_train)


y_test = DataTest.Class
DataTest = DataTest.drop('0',1)
X_test = DataTest.drop('Class',1)
X_test = scaler.transform(X_test)

#Train LR Model

from sklearn.linear_model import LogisticRegression

logreg = LogisticRegression(max_iter = 2000) #max_iter = 2000
logreg = logreg.fit(X_train, y_train)

y_pred=logreg.predict(X_test)


#Save Model
import joblib
filename = args.output
joblib.dump(logreg, filename)


#Output AUROC value
from sklearn import metrics
y_pred_proba = logreg.predict_proba(X_test)[::,1]
fpr, tpr, _ = metrics.roc_curve(y_test, y_pred_proba)
auc = metrics.roc_auc_score(y_test, y_pred_proba)
print(auc)

