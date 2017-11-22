from StockInformation import StockInformation
from WeightedCorrelation import weighted_correlation,weight_point
from scipy.stats import pearsonr 

SI = StockInformation(1)

returns = SI.get_PairedReturns()

all_results = list()

for (ticker1,ticker2),(return1,return2) in returns.iteritems(): 
	single_result = (ticker1,ticker2,weighted_correlation(return1,return2), pearsonr(return1,return2)[0])
	all_results.append(single_result)


all_results.sort(key= lambda x: abs(x[2]-x[3]))

for r in all_results: print r

for x in all_results[:5]:
	r1,r2 = returns[(x[0],x[1])]
	weights = [weight_point(x1,x2)*100 for x1,x2 in zip(r1,r2)]
	SI.plot_pairwise((x[0],x[1]),weights)

