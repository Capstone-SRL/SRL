from calGrade import final_grade
import warnings
warnings.filterwarnings('ignore')

if __name__ == '__main__':
    df_name = '17781'
    subject_id = '128130'

    print(final_grade(df_name, subject_id))
