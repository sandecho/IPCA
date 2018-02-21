from sklearn.datasets import load_iris
from sklearn.decomposition import PCA
import numpy as np
from scipy import linalg

from sklearn.decomposition.base import _BasePCA
from sklearn.utils import check_array, gen_batches
from sklearn.utils.extmath import svd_flip, _incremental_mean_and_var


iris = load_iris()
X = iris.data
y = iris.target

n_components = 2
a=X[0:10]
print(a)
U, S, V = linalg.svd(a, full_matrices=False)
print(V)
print("\n\n\n")
U, V = svd_flip(U, V, u_based_decision=False)
print(V)
print("\n\n\n")
print(U)
print("\n\n\n")
print(U)

