#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 19:27:42 2021

@author: zmp
"""

import pandas as pd
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Compute feature matrix.')
parser.add_argument("--MaxMinFile", help="Provide maxmin file")
parser.add_argument("--MoodsOutput", help="Provide MOODS output file")
parser.add_argument("--SequenceClass", default=1, type=int, help="1 for positive, 0 for negative")
parser.add_argument("--output", help="File output location")

args = parser.parse_args()

Class = args.SequenceClass



MaxMin = args.MaxMinFile

df2 = pd.read_csv(MaxMin)
df2 = df2.set_index('PWM')


file1 = args.MoodsOutput
df = pd.read_csv(file1, header = None)
df = df.drop([6],axis = 1)
df = df.set_index(1)




df2 = df2[['bglogMaxVal','bglogMinVal']]
df = pd.merge(df, df2, left_index=True, right_index=True)

def relScoretest2(value1,value2,value3):
    answer = (value1-value3)/(value2-value3)
    return answer

df['RelativeScore'] = relScoretest2(df[4].values,df['bglogMaxVal'].values,df['bglogMinVal'].values)


### Create an input matrix with motif hits ### ###MAIN###

## Delete hits in the same region. Same enhancer + same start position. Happens when you have a palindromic motif## 
df5 = df.reset_index()
df5 = df5.sort_values('RelativeScore').drop_duplicates(subset=['index',0,2], keep='last')
##Count hits ##
df6 = df5.groupby(['index',0]).size().reset_index(name="Count")

df6 = df6.set_index('index')

df6 = df6.set_index([df6.index, 0])['Count'].unstack()

df6 = df6.T ###Transpose the matrix
df6['Class'] = Class
df6 = df6.fillna(0)
df6.to_csv(args.output, index = True)  
