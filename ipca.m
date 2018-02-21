function [X_mean, X_singular, X_component] = ipca(X, batch_size, n_component)
persistent X_mean=0;
persistent X_singular=0;
persistent X_component=0;
persistent n_sample_seen=0;

%display(X_singular');
%display(X_mean); ---------Totally Correct
col_batch_mean=mean(X);
col_mean=col_batch_mean;

if(n_sample_seen>0)
col_mean = (X_mean*n_sample_seen + col_batch_mean*batch_size)/(n_sample_seen+batch_size);
end;

if(n_sample_seen==0)
X=X.-col_mean;
else
X=X.-col_batch_mean;
mean_correction = sqrt((n_sample_seen*batch_size)/(n_sample_seen+batch_size))*(X_mean-col_batch_mean);
X=[X_singular.*X_component; X; mean_correction];
#display(X_singular.*X_component);
%display(mean_correction);--------------------Totally Correct
end;
%display(col_mean); ----------------------Totally Correct
X_mean=col_mean;
n_sample_seen=n_sample_seen+batch_size;
%display(col_batch_mean);
%display(X_mean);
%display(X(1:2, :));
[U S V] = svd(X, 'econ');
X_singular=diag(S);
X_singular=X_singular(1:n_component, :);
X_component=V(1:n_component, :);
end