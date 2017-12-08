from StockInformation import StockInformation
from WeightedCorrelation import weighted_covariance
from itertools import combinations
from random import shuffle
from OptimalPortfolioFinder import OptimalPortfolioFinder
import datetime, pickle

SAMPLE_SIZE = 10 #Only roughly true, will more in some buckets
WORKING_DAYS = 10

#Weighting Functions
#----------------------------
def my_weighting(x1,x2,k):
	'''
	Returns the 
	x1 = %change in asset 1
	x2 = %change in asset 2 
	'''
	if k == 0: return 1 #janky way of doing standard weighting
	old_wealth = 1
	new_wealth = (old_wealth/2.0)*(1+x1/100.0) + (old_wealth/2.0)*(1+x2/100.0)
	return (1/new_wealth)**k


def standard_weighting(x1,x2): return 1

#Build Optimal Portfolios
#------------------------
def initialize(train_dates,test_dates,limit,verbose=False):
	'''
	Initializes the train and the test dataset and ensures that every stock is complete
	'''

	def ensure_overlap(Train_SI,Test_SI):
		#Ensures that everything in Test is also in train
		to_delete_no_overlap = set()
		for stock in Test_SI.Data:
			if not stock in Train_SI.Data: to_delete_no_overlap.add(stock)
		return to_delete_no_overlap

	Train_SI = StockInformation(WORKING_DAYS,start_year=train_dates[0],end_year=train_dates[1],limit=limit,verbose=False)
	Test_SI = StockInformation(WORKING_DAYS,start_year=test_dates[0],end_year=test_dates[1],limit=limit,verbose=False)
	
	#Ensure that all the data is consistent
	to_delete_test = Test_SI.ensure_data_complete()
	to_delete_train = Train_SI.ensure_data_complete()
	to_delete_no_overlap = ensure_overlap(Train_SI,Test_SI)
	if verbose:
		print "Train:",len(Train_SI.Data),"Test:",len(Test_SI.Data)
		print "To Delete Test",len(to_delete_test)
		print "To Delete Train",len(to_delete_train)
		print "To Delete No overlap",len(to_delete_no_overlap)
		print "Combined:", len(to_delete_train | to_delete_test | to_delete_no_overlap)
	
	
	for stock in to_delete_train | to_delete_test | to_delete_no_overlap: 
		if stock in Train_SI.Data: Train_SI.Data.pop(stock)
		if stock in Test_SI.Data: Test_SI.Data.pop(stock)

	return Train_SI,Test_SI

def build_sample_portfolios(Train_SI,Test_SI):
	'''
	Splits the portfolio into dofferent samples
	'''
	stocks = list(Test_SI.Data)
	shuffle(stocks)
	samples = [list() for _ in range((len(stocks)/SAMPLE_SIZE)+1)]
	for i,s in enumerate(stocks):
		index = i % len(samples)
		samples[index].append(s)
	return samples

def create_cov_matrix_and_returns(sample_portfolios,Train_SI):
	covariance_matrices = []
	semi_covariance_matrices = []
	weighted_covariance_matrices = []
	returns = []
	for i,sample in enumerate(sample_portfolios):

		cov_standard= create_cov_matrix(Train_SI,sample,standard_weighting)
		cov_weighted = create_cov_matrix(Train_SI,sample,my_weighting) 
		covariance_matrices.append([cov_standard,cov_semi,cov_weighted])

		return_i = create_expected_returns(Train_SI,sample)
		returns.append(return_i)

	return returns,covariance_matrices


def create_cov_matrix(Train_SI,sample,weight_func,k):
	matrix = [[0 for _ in sample] for __ in sample]
	for i,s1 in enumerate(sample):
		for j,s2 in enumerate(sample[i:]):
			dates,return1,return2 = Train_SI.get_PairwiseReturn(s1,s2)
			weights = [weight_func(r1,r2,k) for r1,r2 in zip(return1,return2)] 
			cov = weighted_covariance(return1,return2,weights)
			#if not type(cov) is float: print s1,s2,cov
			matrix[i][i+j] = cov
			matrix[j+i][j] = cov
	return matrix
		

def create_expected_returns(Train_SI,sample):
	all_returns = list()
	for stock in sample:
		sum_return = 0 
		price_data = Train_SI.Data[stock]
		for start,end in zip(list(price_data),list(price_data)[1:]):
			sum_return+=price_data[start] / price_data[end]
		all_returns.append((sum_return/len(price_data)-1)*100)
	return all_returns

def discover_optimal_portfolio_weights(expected_returns,covariance_matrix):
	op = OptimalPortfolioFinder(expected_returns,covariance_matrix,0)
	num_iterations = 1000
	return op.find_optimal_weights(num_iterations)




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

def RMSDI(w1,w2):
	'''
	Calculates the RMSDI between two portfolio weights 
	'''
	total = 0
	for p1,p2 in zip(w1,w2):
		total+=abs((100*(p1-p2)))**2
	return total/len(w1)


#Main
#-------------
def compare_methods(train_dates,test_dates,limit,verbose=False):
	'''
	Returns the results of each of the methods using the parameters above 
	'''
	Train_SI,Test_SI = initialize(train_dates,test_dates,limit)
	sample_portfolios = build_sample_portfolios(Train_SI,Test_SI)
	k_range = [0,1,5,10,15,30,50]
	results = [list() for x in k_range]
	RMSDI_results = [list() for _ in k_range]

	for i,sample in enumerate(sample_portfolios):
		
		if verbose: print sample,"|",train_dates[1],
		past_return = create_expected_returns(Train_SI,sample)
		standard_weights = None
		weight_func = my_weighting
		for j,k in enumerate(k_range):
			
			cov = create_cov_matrix(Train_SI,sample,weight_func,k)
			weights = discover_optimal_portfolio_weights(past_return,cov)
			test_return = test_portfolio(Test_SI,sample,weights)
			if j!=0: 
				rmsdi_j = RMSDI(standard_weights,weights)
				RMSDI_results[j].append(rmsdi_j)
			else: 
				standard_weights = weights
				rmsdi_j =0
				RMSDI_results[j].append(rmsdi_j)

			if verbose: print "|","k",k,round(test_return,2),round(rmsdi_j,2),round(max(weights),2),
			results[j].append(test_return)
		
		if verbose: print

	if verbose:
		for r in results: 
			print sum(r)/len(r),
		print 
	return results,RMSDI

def compare_methods_across_multiple_time_periods():

	train_period = 5
	test_period = 5
	start_date = 1980
	end_date = 2017

	limit = float("inf")
	#limit = 1000000

	train_start = start_date
	test_start = start_date+train_period+1

	all_periods_results = dict()
	all_periods_rmsdi = dict()
	
	while True:
		train_end = train_start+train_period
		test_start = train_end+1
		test_end = test_start+test_period
		if test_end>end_date: break
		print 
		print ((train_start,train_end),(test_start,test_end))
		print 
		one_year_results,one_year_rmsdi = compare_methods((train_start,train_end),(test_start,test_end),limit,True)
		all_periods_results[((train_start,train_end),(test_start,test_end))] = one_year_results
		all_periods_rmsdi[((train_start,train_end),(test_start,test_end))] = one_year_rmsdi
		train_start+=1

	file_name = "results/"+"returns"+str(datetime.datetime.now())+"|"+str(limit)+".pkl"
	with open(file_name,"w+") as pklfile:
		pickle.dump(all_periods_results,pklfile)
	file_name = "results/"+"RMSDI"+str(datetime.datetime.now())+"|"+str(limit)+".pkl"
	with open(file_name,"w+") as pklfile:
		pickle.dump(all_periods_rmsdi,pklfile)






if __name__ == "__main__":
	compare_methods_across_multiple_time_periods()
