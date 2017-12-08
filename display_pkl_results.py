import pickle 
from collections import defaultdict


def print_every_return(all_returns):
	for dates in sorted(all_returns): 
		year_returns = all_returns[dates]
		for i,_ in enumerate(year_returns[0]):
			print dates[0][1],
			for y in year_returns: print y[i],
			print

def get_mean_variances(all_returns):
	returns = defaultdict(lambda: list())
	for dates in sorted(all_returns): 
		year_returns = all_returns[dates]
		for i,r in enumerate(year_returns):
			returns[i]+=r

	for i,vals in returns.iteritems():
		print i,sum(vals)/len(vals),

def get_rmsdi(all_rmsdi):
	for  dates in sorted(all_rmsdi):
		for x,y in all_rmsdi.iteritems():
			for z in y:
				print z
		year_returns = all_rmsdi[dates]
		print year_returns

		



if __name__ == "__main__":
	
	returns_file = "results/10_day_returns.pkl"
	rmsdi_file = "results/10_day_RMSDI.pkl"
	with open(returns_file) as f:
		all_returns = pickle.load(f)
	with open(rmsdi_file) as f:
		all_rmsdi = pickle.load(f)
	get_rmsdi(all_rmsdi)
	#get_mean_variances(all_returns)
	#print_every_return(all_returns)




