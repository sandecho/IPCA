from __future__ import division
import numpy as np
from scipy import linalg

from sklearn.decomposition.base import _BasePCA
from sklearn.utils import check_array, gen_batches
from sklearn.utils.extmath import svd_flip, _incremental_mean_and_var


class IPCA(_BasePCA):
    def __init__(self, n_components=None, whiten=False, copy=True,
                 batch_size=None):
        self.n_components = n_components
        self.whiten = whiten
        self.copy = copy
        self.batch_size = batch_size

    def fit(self, X, y=None):
        self.components_ = None
        self.n_samples_seen_ = 0
        self.mean_ = .0
        self.var_ = .0
        self.singular_values_ = None
        self.explained_variance_ = None
        self.explained_variance_ratio_ = None
        self.singular_values_ = None
        self.noise_variance_ = None

        X = check_array(X, copy=self.copy, dtype=[np.float64, np.float32])
        n_samples, n_features = X.shape

        if self.batch_size is None:
            self.batch_size_ = 5 * n_features
        else:
            self.batch_size_ = self.batch_size

        for batch in gen_batches(n_samples, self.batch_size_):
            self.partial_fit(X[batch], check_input=False)

        return self

    def partial_fit(self, X, y=None, check_input=True):
        #print(self.components_)
        #print(self.singular_values_ )
        #print(self.mean_)
        n_samples, n_features = X.shape
        if not hasattr(self, 'components_'):
            self.components_ = None

        if self.n_components is None:
            if self.components_ is None:
                self.n_components_ = min(n_samples, n_features)
            else:
                self.n_components_ = self.components_.shape[0]
        elif not 1 <= self.n_components <= n_features:
            raise ValueError("n_components=%r invalid for n_features=%d, need "
                             "more rows than columns for IncrementalPCA "
                             "processing" % (self.n_components, n_features))
        elif not self.n_components <= n_samples:
            raise ValueError("n_components=%r must be less or equal to "
                             "the batch number of samples "
                             "%d." % (self.n_components, n_samples))
        else:
            self.n_components_ = self.n_components

        if (self.components_ is not None) and (self.components_.shape[0] !=
                                               self.n_components_):
            raise ValueError("Number of input features has changed from %i "
                             "to %i between calls to partial_fit! Try "
                             "setting n_components to a fixed value." %
                             (self.components_.shape[0], self.n_components_))

        # This is the first partial_fit
        if not hasattr(self, 'n_samples_seen_'):
            self.n_samples_seen_ = 0
            self.mean_ = .0
            self.var_ = .0

        # Update stats - they are 0 if this is the fisrt step
        col_mean, col_var, n_total_samples = \
            _incremental_mean_and_var(X, last_mean=self.mean_,
                                      last_variance=self.var_,
                                      last_sample_count=self.n_samples_seen_)
	# Whitening
        #print(col_mean) ---------------Totally Correct
        if self.n_samples_seen_ == 0:
            # If it is the first step, simply whiten X
            X -= col_mean
        else:
            col_batch_mean = np.mean(X, axis=0)
            #print(col_batch_mean)  #-----------Totally Correct
            X -= col_batch_mean
            # Build matrix of combined previous basis and new data
            mean_correction = \
                np.sqrt((self.n_samples_seen_ * n_samples) /
                        n_total_samples) * (self.mean_ - col_batch_mean)
            X = np.vstack((self.singular_values_.reshape((-1, 1)) *
                          self.components_, X, mean_correction))
            print(self.singular_values_.reshape((-1, 1)) *self.components_)
            #print(mean_correction) #-------------Totally Correct
        #print(X[:2])
        #print("\n\n\n");

        U, S, V = linalg.svd(X, full_matrices=False)
        #U, V = svd_flip(U, V, u_based_decision=False)
        explained_variance = S ** 2 / (n_total_samples - 1)
        explained_variance_ratio = S ** 2 / np.sum(col_var * n_total_samples)
        
        self.n_samples_seen_ = n_total_samples
        self.components_ = V[:self.n_components_]
        #print(self.components_);
        self.singular_values_ = S[:self.n_components_]
        self.mean_ = col_mean
        #print(self.mean_)
        self.var_ = col_var
        self.explained_variance_ = explained_variance[:self.n_components_]
        self.explained_variance_ratio_ = \
            explained_variance_ratio[:self.n_components_]
        if self.n_components_ < n_features:
            self.noise_variance_ = \
                explained_variance[self.n_components_:].mean()
        else:
            self.noise_variance_ = 0.
        return self
