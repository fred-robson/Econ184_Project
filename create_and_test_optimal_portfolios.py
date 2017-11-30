from StockInformation import StockInformation
from WeightedCorrelation import weighted_covariance
from itertools import combinations
from random import shuffle

SAMPLE_SIZE = 5 #Only roughly true, will be  more in some buckets

#Weighting Functions
#----------------------------
def my_weighting(x1,x2,verbose=False):
	'''
	Returns the 
	x1 = %change in asset 1
	x2 = %change in asset 2 
	'''
	old_wealth = 1
	new_wealth = (old_wealth/2.0)*(1+x1/100.0) + (old_wealth/2.0)*(1+x2/100.0)
	return 1/new_wealth

def semi_weighting(x1,x2):
	if (x1+x2)>2: return 0
	return 1

def standard_weighting(x1,x2):
	return 1

#Build Optimal Portfolios
#------------------------
def initialize():

	def ensure_overlap(Train_SI,Test_SI):
		#Ensures that everything in Test is also in train
		to_delete_no_overlap = set()
		for stock in Test_SI.Data:
			if not stock in Train_SI.Data: to_delete_no_overlap.add(stock)
		return to_delete_no_overlap

	limit = 200000
	Train_SI = StockInformation(1,start_year=2000,end_year=2010,limit=limit)
	Test_SI = StockInformation(1,start_year=2011,end_year=2015,limit=limit)
	
	#Ensure that all the data is consistent
	to_delete_test = Test_SI.ensure_data_complete()
	to_delete_train = Train_SI.ensure_data_complete()
	to_delete_no_overlap = ensure_overlap(Train_SI,Test_SI)
	
	for stock in to_delete_train | to_delete_test | to_delete_no_overlap: 
		if stock in Train_SI.Data: Train_SI.Data.pop(stock)
		if stock in Test_SI.Data: Test_SI.Data.pop(stock)

	return Train_SI,Test_SI

def build_sample_portfolios(Train_SI,Test_SI):
	stocks = list(Test_SI.Data)
	print "SAMPLE STOCKS",stocks
	shuffle(stocks)
	samples = [list() for _ in range(len(stocks)/SAMPLE_SIZE)]
	for i,s in enumerate(stocks):
		index = i % len(samples)
		samples[index].append(s)
	return samples

def create_cov_matrix_and_returns(sample_portfolios,Train_SI):
	standard_covariance_matrices = []
	semi_covariance_matrices = []
	weighted_covariance_matrices = []
	returns = []
	for i,sample in enumerate(sample_portfolios):

		cov_standard= create_cov_matrix(Train_SI,sample,standard_weighting)
		standard_covariance_matrices.append(cov_standard) 

		cov_semi = create_cov_matrix(Train_SI,sample,semi_weighting)
		semi_covariance_matrices.append(cov_semi) 

		cov_weighted = create_cov_matrix(Train_SI,sample,my_weighting) 
		weighted_covariance_matrices.append(cov_weighted)

		return_i = create_expected_returns(Train_SI,sample)
		returns.append(return_i)

	return returns,weighted_covariance_matrices,semi_covariance_matrices,standard_covariance_matrices


def create_cov_matrix(Train_SI,sample,weight_func):
	matrix = [[0 for _ in sample] for __ in sample]
	for i,s1 in enumerate(sample):
		for j,s2 in enumerate(sample[i:]):
			print sample,s1,s2,
			dates,return1,return2 = Train_SI.get_PairwiseReturn(s1,s2)
			print len(return1)
			weights = [weight_func(r1,r2) for r1,r2 in zip(return1,return2)] 
			cov = weighted_covariance(return1,return2,weights)
			matrix[i][i+j] = cov
			matrix[j+i][j] = cov
	return matrix
		

def create_expected_returns(Train_SI,sample):
	all_returns = list()
	for stock in sample:
		sum_return = 0 
		price_data = Train_SI.Data[stock]
		print stock,len(price_data)
		for start,end in zip(list(price_data),list(price_data)[1:]):
			sum_return+=price_data[start] / price_data[end]
		all_returns.append(sum_return / len(price_data))
	return all_returns

def discover_optimal_portfolio_weights(expected_returns,covariance_matrix):
	print expected_returns
	return [1.0/len(expected_returns) for _ in expected_returns]

#Test Portfolios
#---------------
def test_portfolio(Test_SI,sample,weights):

	total_return = 0
	for i,stock in enumerate(sample):
		price_data = Test_SI.Data[stock]
		start_price = price_data.values()[0]
		end_price = price_data.values()[-1]
		total_return+=weights[i]*end_price/start_price
		
	return total_return


#Main
#-------------
def compare_all_results():
	Train_SI,Test_SI = initialize()
	sample_portfolios = build_sample_portfolios(Train_SI,Test_SI)
	returns,weighted_covariance_matrices,semi_covariance_matrices,standard_covariance_matrices = create_cov_matrix_and_returns(sample_portfolios,Train_SI)
	for i,sample in enumerate(sample_portfolios):
		r = returns[i]
		cov = standard_covariance_matrices[i]
		weights = discover_optimal_portfolio_weights(r,cov)
		print "Sample",sample
		print "R",r
		print "Weights",weights
		print test_portfolio(Test_SI,sample,weights)





if __name__ == "__main__":
	main()
