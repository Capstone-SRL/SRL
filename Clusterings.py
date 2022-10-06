from sklearn import cluster


#  Affinity Propagation
def affi_prop(X, damping=0.9):
    # define model
    model = cluster.AffinityPropagation(damping=damping,random_state=5)
    # fit model
    model.fit(X)
    return model


# DBSCAN
def DBSCAN(X, eps=0.30, min_samples=9):
    # define model
    model = cluster.DBSCAN(eps=eps, min_samples=min_samples).fit(X)
    #clusters = unique(yhat)
    return model


# meanShift
def meanShift(X, bandwidth=2):
    # define model
    model = cluster.MeanShift(bandwidth=bandwidth).fit(X)
    return model


# miniBatch
def miniBatch(X, n_clusters=3):
    # define model
    model = cluster.MiniBatchKMeans(n_clusters=n_clusters).fit(X)
    return model


