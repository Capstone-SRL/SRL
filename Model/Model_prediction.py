from Model.Proprocessing import preprocess, split, scale
import json
import pickle as pk
import os
import pandas as pd


def prediction(df, pkmodel, model_name=None, data=None):
    path = os.getcwd()
    models = os.listdir(f'{path}/pkmodel')

    if pkmodel == 'best':
        model_name = models['best' in models]
        data = model_name.split('_')[2]
    elif pkmodel == 'auto':
        model_name = f'{model_name}_{data}_model.pkl'

    # data preprocess
    # df = pd.read_excel(df_name)
    df = preprocess(df, train=False)
    X, y = split(df)  # Data splitting
    if data == 'scale':
        X = scale(X)  # Scale
    elif data == 'pca':
        pca = pk.load(open(f'{path}/pkmodel/pca.pkl', 'rb'))
        X = scale(X)
        X = pca.transform(X)

    model = pk.load(open(f'{path}/pkmodel/{model_name}', 'rb'))
    predict = model.predict(X)

    return predict, model_name

