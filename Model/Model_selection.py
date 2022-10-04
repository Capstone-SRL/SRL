from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import RidgeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import CategoricalNB
from sklearn.ensemble import BaggingClassifier
from sklearn.ensemble import RandomForestClassifier
from Model.Proprocessing import generate_training_data
import math
import pickle as pk
import json
import os
import shutil
import warnings
warnings.filterwarnings('ignore')

path = os.getcwd()


def model_select(df):
    X, X_train, X_pca, X_pls, y_level, y_level_pls = generate_training_data(df)

    names = ['origin', 'scale', 'pca', 'pls']
    Xs = [X, X_train, X_pca, X_pls]
    ys = [y_level, y_level, y_level, y_level_pls]
    res = []

    # model selection
    for (name, X, y) in zip(names[:3], Xs, ys):
        res.append(format('lg', name, lg(X, y, name)))
        res.append(format('ridge', name, ridge(X, y, name)))
        res.append(format('knn', name, knn(X, y, name)))
        res.append(format('svc', name, svc(X, y, name)))
        res.append(format('bagging', name, bagging(X, y, name)))
        res.append(format('rf', name, rf(X, y, name)))

    with open('model.json', 'w') as f:
        json.dump(res, f)

    # model construction
    best_model = max(res, key=lambda x: x['Accuracy'])
    data = best_model['Data']
    model = best_model["Model"]

    src = f'{path}/pkmodel/{model}_{data}_model.pkl'
    dst = f'{path}/pkmodel/best_{model}_{data}_model.pkl'
    shutil.copyfile(src, dst)

    return 0


# def model_construction(X, y, params, data=None, model=None, best=1):
#     if model == 'lg':
#         best_model = LogisticRegression(**params)
#     elif model == 'ridge':
#         best_model = RidgeClassifier(**params)
#     elif model == 'knn':
#         best_model = KNeighborsClassifier(**params)
#     elif model == 'svc':
#         best_model = SVC(**params)
#     elif model == 'bagging':
#         best_model = BaggingClassifier(**params)
#     elif model == 'rf':
#         best_model = RandomForestClassifier(**params)
#
#     best_model.fit(X, y)
#
#     if best == 1:
#         mn = f"pkmodel/best_{data}_{model}_model.pkl"
#     else:
#         mn = 'auto_model.pkl'
#
#     pk.dump(best_model, open(mn, "wb"))
#
#     return 0



def format(model, name, res):
    return {'Model': model, 'Data': name, 'model_name': f'{model}_{name}', 'Accuracy': res[0], 'Parameter': res[1]}


def grid_search(model, grid, X, y):
    cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
    grid_search = GridSearchCV(estimator=model, param_grid=grid, n_jobs=-1, cv=cv, scoring='accuracy', error_score=0)
    grid_result = grid_search.fit(X, y)
    # summarize results
    print(model)
    print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
    #     means = grid_result.cv_results_['mean_test_score']
    #     stds = grid_result.cv_results_['std_test_score']
    #     params = grid_result.cv_results_['params']
    #     for mean, stdev, param in zip(means, stds, params):
    #         print("%f (%f) with: %r" % (mean, stdev, param))

    return grid_result.best_score_, grid_result.best_params_


def lg(X, y, data):
    # define models and parameters
    model = LogisticRegression()
    solvers = ['newton-cg', 'lbfgs', 'liblinear']
    penalty = ['l2']
    c_values = [100, 10, 1.0, 0.1, 0.01]
    # define grid search
    grid = dict(solver=solvers, penalty=penalty, C=c_values)
    score, params = grid_search(model, grid, X, y)

    model.set_params(**params)
    model.fit(X, y)
    mn = f"{path}/pkmodel/lg_{data}_model.pkl"
    pk.dump(model, open(mn, "wb"))

    return score, params


def ridge(X, y, data):
    # define models and parameters
    model = RidgeClassifier()
    alpha = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    # define grid search
    grid = dict(alpha=alpha)
    score, params = grid_search(model, grid, X, y)

    model.set_params(**params)
    model.fit(X, y)
    mn = f"{path}/pkmodel/ridge_{data}_model.pkl"
    pk.dump(model, open(mn, "wb"))

    return score, params


def knn(X, y, data):
    n = len(y)

    # define models and parameters
    model = KNeighborsClassifier()
    n_neighbors = range(1, n // 10, 2)
    weights = ['uniform', 'distance']
    algorithm = ['auto', 'ball_tree', 'kd_tree', 'brute']
    metric = ['euclidean', 'manhattan', 'minkowski']
    leaf_size = [2 ** i for i in range(1, int(math.log2(len(y))) + 1)]
    # define grid search
    grid = dict(n_neighbors=n_neighbors, weights=weights, algorithm=algorithm, metric=metric, leaf_size=leaf_size)
    score, params = grid_search(model, grid, X, y)

    model.set_params(**params)
    model.fit(X, y)
    mn = f"{path}/pkmodel/knn_{data}_model.pkl"
    pk.dump(model, open(mn, "wb"))

    return score, params


def svc(X, y, data):
    # define model and parameters
    model = SVC()
    kernel = ['linear', 'poly', 'rbf', 'sigmoid']
    C = [100, 50, 10, 1.0, 0.1, 0.01, 0.001, 0.0001]
    gamma = ['scale', 'auto']
    shrinking = [True, False]
    probability = [True, False]
    tol = [1, 0.1, 0.01, 1e-3, 1e-6]
    # define grid search
    grid = dict(kernel=kernel, C=C, gamma=gamma, shrinking=shrinking, probability=probability, tol=tol)
    score, params = grid_search(model, grid, X, y)

    model.set_params(**params)
    model.fit(X, y)
    mn = f"{path}/pkmodel/lg_{data}_model.pkl"
    pk.dump(model, open(mn, "wb"))

    return score, params


def bagging(X, y, data):
    # define models and parameters
    model = BaggingClassifier()
    n_estimators = [1, 10, 100, 1000]
    max_samples = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
    max_features = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
    bootstrap = [True, False]
    bootstrap_features = [True, False]
    # define grid search
    grid = dict(n_estimators=n_estimators, max_samples=max_samples, max_features=max_features,
                bootstrap=bootstrap, bootstrap_features=bootstrap_features)
    score, params = grid_search(model, grid, X, y)

    model.set_params(**params)
    model.fit(X, y)
    mn = f"{path}/pkmodel/bagging_{data}_model.pkl"
    pk.dump(model, open(mn, "wb"))

    return score, params


def rf(X, y, data):
    # define models and parameters
    model = RandomForestClassifier()
    n_estimators = [1, 10, 100, 1000]
    criterion = ['gini', 'entropy', 'log_loss']
    max_features = ['sqrt', 'log2']
    ccp_alpha = [0.1, 0.2, 0.3, 0.4, 0.5]
    # define grid search
    grid = dict(n_estimators=n_estimators, max_features=max_features)
    score, params = grid_search(model, grid, X, y)

    model.set_params(**params)
    model.fit(X, y)
    mn = f"{path}/pkmodel/rf_{data}_model.pkl"
    pk.dump(model, open(mn, "wb"))

    return score, params