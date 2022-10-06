# import packages
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import Clusterings
from sklearn.decomposition import PCA
import plotly.express as px

# import data
# csv file
# df = pd.read_excel('data/res3.0.xlsx')
# MF_scores = df[['c1','c2', 'c3_grade', 'c4_grade', 'c5grade', 'c7_grade']]
# MF_scores.rename(columns={'c1':'Itme1', 'c2':'Item2', 'c3_grade':'Itme3', 'c4_grade':'Itme4', 'c5grade':'Item5', 'c7_grade':'Item7'}, inplace=True)
full_data = pd.read_csv('full_Data.csv')

# output statistical description of each cluster
def classify(data, labels, file):
    dic = {}
    for i in range(len(labels)):
        if labels[i] in dic:
            dic[labels[i]].append(data.iloc[i, :])
        else:
            dic[labels[i]] = [data.iloc[i, :]]
    for key,val in dic.items():
        dic[key] = pd.DataFrame(val)
        print(f'Cluster {key}:')
        print(dic[key].describe())
        dic[key].describe().to_csv(f'Clustering/{file}/Cluster {key}.csv')
        #os.mkdir(file)
        # dic[key].describe().to_csv(f'{file}/Cluster {key}.csv') ## output the descriptions to files
    return


# principal components analysis and visualize clustering results
def pca(data,labels, dimension=4):
    # data preparation
    y = [str(i) for i in labels]
    x = data
    # PCA
    pca = PCA()
    components = pca.fit_transform(x)
    label = {
        str(i): f"PC {i+1} ({var:.1f}%)"
        for i, var in enumerate(pca.explained_variance_ratio_ * 100)
    }
    fig = px.scatter_matrix(
        components,
        labels=label,
        dimensions=range(dimension),
        color=y
    )
    fig.update_traces(diagonal_visible=False)
    fig.show()
    return

# ### Mean Shift
# num_clu = []
# num_noise = []
# eps = np.arange(1,11)
# for i in eps:
#     model = Clusterings.meanShift(MF_scores, i)
#     n_clusters_ = len(set(model.labels_)) - (1 if -1 in model.labels_ else 0)
#     num_clu.append(n_clusters_)
#     n_noise_ = list(model.labels_).count(-1)
#     num_noise.append(n_noise_)
#
# fig, ax = plt.subplots()
# ax.scatter(eps, num_clu, linewidth=2.0)
# plt.show()
#
# fig, ax = plt.subplots()
# ax.plot(eps, num_noise, linewidth=2.0)
# plt.show()

pca(full_data,Clusterings.miniBatch(full_data, 2).labels_,4)



