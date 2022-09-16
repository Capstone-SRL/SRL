from calGrade import final_grade
from preprocess import unpack
import os
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


folder = 'Data/pageview'

if __name__ == '__main__':
    res = []
    subject_ids = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]

    for j in subject_ids:
        subject_id = j
        ids = [i for i in os.listdir(f'{folder}/{j}') if 'xlsx' in i]
        for k in ids:
            student_id = k.split('_')[1]
            print(student_id, subject_id)
    # student_id = '110760'
    # subject_id = '128130'
            unpack_data = unpack(final_grade(student_id, subject_id))
            res.append(unpack_data)
    pd.DataFrame(res).to_excel('res.xlsx', index=False)
