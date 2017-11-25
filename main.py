from StockInformation import StockInformation
from WeightedCorrelation import weighted_correlation,weight_point
from scipy.stats import pearsonr 
from itertools import combinations
import datetime
import pickle as pkl

def get_all_results():
	limit = 10000
	SI = StockInformation(1,verbose=True,start_year=2006,end_year=2016)

	all_results = list()
	print len(list(combinations(SI.Data,2)))
	tickers = list(SI.Data)
	print tickers
	for i,ticker1 in enumerate(tickers):
		for j,ticker2 in enumerate(tickers[i+1:]):
			dates,return1,return2 = SI.get_PairwiseReturn(ticker1,ticker2)
			weights = [weight_point(r1,r2) for r1,r2 in zip(return1,return2)]
			w_corr = weighted_correlation(return1,return2,weights)
			corr = pearsonr(return1,return2)[0]
			try:
				diff = abs(w_corr - corr)
			except: 
				diff = None

			single_result = (ticker1,ticker2,w_corr,corr,diff)
			all_results.append(single_result)
			print i,j,single_result,len(return1)


	all_results.sort(key= lambda x: x[4],reverse=True)

	pkl_name = str("results/"+str(datetime.datetime.now())+"-"+str(limit)+".pkl")
	with open(pkl_name,"w+") as pkl_dump_file:
		pkl.dump(all_results,pkl_dump_file)
	return all_results

def print_top(all_results,num_to_print):
	print "\n"
	print "Largest Spreads"
	print "---------------"
	for i,r in enumerate(all_results[:num_to_print]): 
		print i+1,".",r

def plot_top_results(all_results,num_to_plot):
	for r in all_results[:num_to_plot]:
		t1,t2,w_corr,corr,_ = r
		weights = None
		SI.plot_pairwise((t1,t2),)

if __name__ == '__main__':
	all_results = get_all_results()
	print_top(all_results,10)
	#plot_top_results(all_results)
