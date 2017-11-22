import numpy as np
from scipy.stats.stats import pearsonr


def utility_derivative(wealth): 
	
	return (1/wealth)**2
	
def weight_point(x1,x2,verbose=False):
	'''
	Returns the 
	x1 = %change in asset 1
	x2 = %change in asset 2 
	'''
	old_wealth = 1
	new_wealth = (old_wealth/2.0)*(1+x1/100.0) + (old_wealth/2.0)*(1+x2/100.0)
	if verbose: print x1,x2,new_wealth, abs(utility_derivative(new_wealth))
	return abs(utility_derivative(new_wealth))


def weighted_covariance(X1,X2,W):
	X1,X2,W = np.array(X1),np.array(X2),np.array(W)

	sum_weights = sum(W)

	X1_bar = np.dot(X1,W)/float(sum_weights)
	X2_bar = np.dot(X2,W)/float(sum_weights)

	X1_norm = X1 - X1_bar
	X2_norm = X2 - X2_bar

	X1_norm_w = np.multiply(X1_norm,W)

	cov = np.dot(X1_norm_w,X2_norm)/sum_weights
	
	return cov


def weighted_correlation(X1,X2):
	#Calculates weighted correlation 
	weights = [weight_point(x1,x2) for x1,x2 in zip(X1,X2)]
	
	cov = weighted_covariance(X1,X2,weights)
	var1 = weighted_covariance(X1,X1,weights)
	var2 = weighted_covariance(X2,X2,weights)
	
	return cov/((var1*var2)**(1.0/2))


def test_data():
	return [1,2,3],[12,6,7]


if __name__ == "__main__":
	x1,x2 = test_data()
	print utility_derivative(1.1)
