import numpy as np
from scipy.stats.stats import pearsonr
#np.warnings.filterwarnings('ignore')

def weighted_covariance(X1,X2,W):
	X1,X2,W = np.array(X1),np.array(X2),np.array(W)

	sum_weights = sum(W)

	X1_bar = np.dot(X1,W)/float(sum_weights)
	X2_bar = np.dot(X2,W)/float(sum_weights)

	X1_norm = X1 - X1_bar
	X2_norm = X2 - X2_bar

	X1_norm_w = np.multiply(X1_norm,W)

	cov = np.dot(X1_norm_w,X2_norm)/sum_weights

	return float(cov)
	

def weighted_correlation(X1,X2,weights):
	if len(X1) == 0: return None
	#Calculates weighted correlation 
	
	cov = weighted_covariance(X1,X2,weights)
	var1 = weighted_covariance(X1,X1,weights)
	var2 = weighted_covariance(X2,X2,weights)
	
	return cov/((var1*var2)**(1.0/2))


def test_data():
	return [1,2,3],[12,6,7]


if __name__ == "__main__":
	x1,x2 = test_data()
	w = [1,1,1]
	#print weighted_correlation(x1,x2,w)
	print weighted_covariance(x1,x2,w)

