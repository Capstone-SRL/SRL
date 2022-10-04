import numpy as np
from sklearn.preprocessing import MaxAbsScaler
from sklearn.decomposition import PCA
from sklearn import model_selection
from sklearn.cross_decomposition import PLSRegression, PLSSVD
import pickle as pk
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error


def generate_training_data(df):
    df = preprocess(df)

    X, y_level = split(df)          # Data splitting
    X_train = scale(X)              # Scale
    X_pca = pca(X_train)            # PCA
    X_pls, y_level_pls = pls(X_train, y_level)

    names = list(X.columns)
    with open(r'Streamlit/col_name.txt', 'w') as fp:
        for item in names:
            fp.write("%s\n" % item)

    return X, X_train, X_pca, X_pls, y_level, y_level_pls


# data preprocessing
def preprocess(df, train=True):
    col = df.columns

    # remove data without grade
    if train == True:
        df = df[(~df['final_grade_score'].isnull()) & (df['final_grade_level']!='N')]

    min_col = [i for i in col if ('ass_grade_level' in i or 'check_grade' in i)]
    spec = [i for i in col if 'when_submit_ass' in i]
    mean_col = [i for i in col if (i not in spec+min_col+['subject_id', 'student_id', 'final_grade_level', 'final_grade_score'])]

    # use mean for same subject
    mean_df = df[['subject_id']+mean_col].groupby(['subject_id']).mean().reset_index()
    df = fill_in(df, mean_df, mean_col)

    # use min for same subject
    min_df = df[['subject_id']+min_col].groupby(['subject_id']).min().reset_index()
    df = fill_in(df, min_df, min_col)

    # specific changes
    col = spec
    for i in col:
        null_index = list(df[df[i].isnull()].index)
        col_index = df.columns.get_loc(i)
        for index in null_index:
            df.loc[index, i] = 'late'

    # category to ordinal
    col = spec + ['subject_id']
    for i in col:
        category = list(set(df[i]))
        for j in range(len(category)):
            df[f'{i}_{j}'] = 0
            df.loc[df[i] == category[j], f'{i}_{j}'] = 1
        df.drop(i, axis=1, inplace=True)

    if train == False:
        names = []
        with open(r'Streamlit/col_name.txt', 'r') as fp:
            for line in fp:
                x = line[:-1]
                names.append(x)
        print('aaaaaaaaa', len(names))
        df = df[names+['student_id', 'final_grade_level', 'final_grade_score']]

    return df


# fill in missing values
def fill_in(df, gb_df, col):
    for i in col:
        null_index = list(df[df[i].isnull()].index)
        col_index = df.columns.get_loc(i)
        for index in null_index:
            info = df.loc[index]
            sub_id = info[0]
            fill = gb_df.loc[gb_df['subject_id']==sub_id, i].values[0]
            if np.isnan(fill):
                fill = 0
            df.loc[index, i] = fill
    return df


def split(df):
    y_li = ['final_grade_score', 'final_grade_level']
    # y_score = df['final_grade_score']
    y_level = df['final_grade_level']
    X = df
    X.drop(y_li, axis=1, inplace=True)
    X.drop('student_id', axis=1, inplace=True)

    return X, y_level


def scale(X):
    max_abs_scaler = MaxAbsScaler()
    X_train = max_abs_scaler.fit_transform(X)

    return X_train


def pca(X_train):
    Pca = PCA(n_components=0.98, svd_solver='full')
    X_pca = Pca.fit_transform(X_train)
    pk.dump(Pca, open("Streamlit/pca.pkl", "wb"))

    return X_pca


def pls(X_train, y_level):
    # transfer categorical y to numerical
    scores = {'H1': 5, 'H2A': 4, 'H2B': 3, 'H3': 2, 'P': 1}
    y_level_score = y_level.copy()
    for i in scores:
        y_level_score[y_level_score == i] = scores[i]

    # choose num of component by CV
    n = len(X_train)
    kf_10 = model_selection.KFold(n_splits=10, shuffle=True, random_state=1)
    mse = []
    for i in np.arange(1, 50):
        pls = PLSRegression(n_components=i, scale=False)
        score = model_selection.cross_val_score(pls, X_train, y_level_score, cv=kf_10,
                                                scoring='neg_mean_squared_error').mean()
        mse.append(-score)
    cop = mse.index(min(mse))

    # dimension reduction by PLS
    Pls = PLSRegression(n_components=cop, scale=False)
    X_pls, y_level_pls = Pls.fit_transform(X_train, y_level_score)

    return X_pls, y_level_pls

