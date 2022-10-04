from Extraction.calGrade import final_grade
from Extraction.preprocess import unpack
from Model.Model_selection import model_select
from Model.Model_prediction import prediction

import os
import pandas as pd
import argparse
import subprocess
import warnings
warnings.filterwarnings('ignore')


folder = 'Data/pageview'


def extraction():
    res = []
    subject_ids = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]

    for j in subject_ids:
        subject_id = j
        ids = [i for i in os.listdir(f'{folder}/{j}') if 'xlsx' in i]
        for k in ids:
            student_id = k.split('_')[1]
            print(student_id, subject_id)
            # print(final_grade(student_id, subject_id))
            unpack_data = unpack(final_grade(student_id, subject_id))
            res.append(unpack_data)
    pd.DataFrame(res).to_excel('res.xlsx', index=False)

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract", default=1, required=False, help="Data Extraction", type=int)
    parser.add_argument("--select", default=1, required=False, help="Model Selection", type=int)
    parser.add_argument("--predict", default=1, required=False, help="Model Prediction", type=int)
    parser.add_argument("--test", default=None, required=False, help="test file to make predictions", type=str)
    parser.add_argument("--display", default=0, required=False, help="report for SRL", type=int)

    args = parser.parse_args()
    df_name = 'res.xlsx'
    if args.extract == 1:
        extraction()
    if args.select == 1:
        df = pd.read_excel(df_name)
        model_select(df)
    if args.predict == 1:
        if args.test != None:
            df_name = args.test
        df = pd.read_excel(df_name)
        pre = prediction(df, 'best')
    if args.display == 1:
        subprocess.call(["streamlit", "run", "Streamlit/display_main.py"])

