# from Model.Proprocessing import preprocess, split, scale, pca
import sys
import os
sys.path.append(os.getcwd())
from Model.Model_prediction import prediction
import streamlit as st
import json
import pandas as pd
import pickle as pk
import numpy as np
import base64
from pyexcelerate import Workbook

import warnings
warnings.filterwarnings('ignore')

models = ['lg', 'ridge', 'knn', 'svc', 'bagging', 'rf']
datas = ['origin', 'scale', 'pca', 'pls']

def display(js):
    # PCA
    names = []
    with open(r'Streamlit/col_name.txt', 'r') as fp:
        for line in fp:
            x = line[:-1]
            names.append(x)

    pca_reload = pk.load(open("pkmodel/pca.pkl", 'rb'))

    cop = pca_reload.components_

    st.subheader('PCA component')
    num = st.text_input(
        "Please enter the number of components you want to see",
        5,
    )
    st.write(f'98% variance are remained by PCA. There are {len(cop)} components')
    st.markdown(f"**The first {num} components**")
    st.dataframe(pd.DataFrame(cop[:int(num),:], columns=names))

    st.markdown(f"**Top 10 variables for the first {num} components**")
    ress = []
    for i in range(len(cop)):
        K = np.array(cop[i])
        s = K.argsort()[-10:][::-1]
        name = np.array(names)[s]
        # value = K[s]
        res = [name[i] for i in range(10)]
        ress.append({'PC': f'PC{i+1}', 'Top 10': res})

    c = st.container()
    for i in range(int(num)):
        c.text(f"{ress[i]['PC']}: {ress[i]['Top 10']}")
    # st.write(ress)
    # st.table(pd.DataFrame(ress[:int(num)]))

    # Model
    st.subheader('Model Evaluation')
    f = open(js)
    data = json.load(f)
    f.close()

    dd = pd.DataFrame(data)
    dd = dd.astype(str)
    # st.dataframe(dd)

    st.markdown("**Optimised model for each data**")
    idx = dd.groupby(['Data'])['Accuracy'].transform(max) == dd['Accuracy']
    st.dataframe(dd[idx])

    st.markdown("**Optimised model for each model**")
    idx = dd.groupby(['Model'])['Accuracy'].transform(max) == dd['Accuracy']
    st.dataframe(dd[idx])

    # prediction
    st.subheader("Prediction")
    uploaded_file = st.file_uploader("Choose a test XLSX file", type="xlsx")
    st.write("Select the model and data you want to use. Default is the best model")
    ph = st.empty()

    c1, c2 = st.columns(2)
    with c1:
        model_name = st.selectbox('Model', ['best']+models)
    with c2:
        if model_name == 'best':
            d = st.selectbox('Data', '')
        else:
            d = st.selectbox('Data', datas)

    if uploaded_file:
        df = pd.read_excel(uploaded_file.read())

        show = pd.DataFrame()
        # st.dataframe(df)
        show['subject_id'] = df['subject_id']
        show['student_id'] = df['student_id']

        if (not(model_name and data)) or (model_name=='best'):
            pre, mn = prediction(df, 'best')
        else:
            pre, mn = prediction(df, 'auto', model_name, d)

        ph.write(f"The current used model is {mn}")

        show['predict'] = pre
        st.dataframe(show)

        if st.button('Export predictions'):
            values = [show.columns] + list(show.values)
            wb = Workbook()
            wb.new_sheet('SRL_prediction', data=values)
            wb.save('SRL_prediction.xlsx')
            md = get_binary_file_downloader_html('SRL_prediction.xlsx', 'file')
            st.markdown(md, unsafe_allow_html=True)


# for file download
def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href