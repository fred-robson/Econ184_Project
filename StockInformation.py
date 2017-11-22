import csv
from collections import defaultdict,OrderedDict
from datetime import datetime,timedelta
from itertools import combinations
import matplotlib.pyplot as plt
import matplotlib
from tqdm import tqdm

QUANDL_API_KEY = "XwCG5EsTRsY4yLRUPLXv"

class StockInformation():

	def __init__(self,working_days=5,verbose=False):
		self.working_days = working_days
		self.Data = defaultdict(lambda:OrderedDict())
		self.RecordedDays = set()
		self.populate_StockHistory()
		self.PairedReturns = defaultdict(lambda:list())
		self.get_PairwiseReturns()
		self.verbose = verbose
		

	def populate_StockHistory(self):
		#Reads the csv and puts relevant info in Data
		with open("prices.csv") as csv_file: 
			reader = csv.DictReader(csv_file)
			prev_row = None
			for i,row in tqdm(enumerate(reader)):
				try: 
					ticker = row['ticker']
					date = datetime.strptime(row['date'],"%Y-%m-%d")
					adj_close = float(row["adj_close"])#adj_close = Close adjusted for stock splits and dividends
					self.Data[ticker][date] = adj_close #Note that it 
					self.RecordedDays.add(date)
				except:
					if self.verbose: print row
				#if i == 100000: break

		if self.verbose: print "Finished Reading CSV"
		self.RecordedDays = list(self.RecordedDays)
		self.RecordedDays.sort()

	def get_return(self,ticker,start,end):
		if start in self.Data[ticker]: start_p = self.Data[ticker][start]
		else: return None
		
		if end in self.Data[ticker]: end_p = self.Data[ticker][end]
		else: return None

		return ((end_p / start_p) -1.0)*100 #Returns in percentage terms

	def get_PairwiseReturns(self):
		'''
		Gets the paired returns for each of the stocks. Returns are measured over @working_days in work days 
		'''
		for t1,t2 in combinations(self.Data,2):
			if len(self.Data[t1])<len(self.Data[t2]): tsmall,tlarge = t1,t2
			else: tlarge,tsmall = t2,t1
			
			dates = list(self.Data[tsmall])
			curr_index = 0 
			start = dates[0]

			while(True):
				curr_index += self.working_days
				if curr_index>len(dates)-1: break
				end = dates[curr_index]
				
				ts_return = self.get_return(tsmall,start,end)
				tl_return = self.get_return(tlarge,start,end)
				
				if ts_return !=None and tl_return !=None:
					self.PairedReturns[(tsmall,tlarge)].append(((start,end),ts_return,tl_return))

				start = end

	

	def plot_stockprice(self,ticker):
		prices = self.Data[ticker]
		dates = matplotlib.dates.date2num([x for x in prices])
		values = [x for x in prices.values()]
		plt.clf()
		plt.plot(dates, values)
		plt.title("Adjusted Closing Price of "+ticker)
		plt.show()

	def plot_pairwise(self,ticker_pair,weights=None):
		returns = self.PairedReturns[ticker_pair]
		plt.clf()
		
		ax = plt.gca()
		ax.spines['right'].set_color('none')
		ax.spines['top'].set_color('none')
		ax.xaxis.set_ticks_position('bottom')
		ax.spines['bottom'].set_position(('data',0))
		ax.yaxis.set_ticks_position('left')
		ax.spines['left'].set_position(('data',0))
		ax.set_xlabel(ticker_pair[0])
		ax.set_ylabel(ticker_pair[1])

		plt.xlim([-50,50])
		plt.ylim([-50,50])
		
		if weights is None: plt.scatter([x[1] for x in returns],[y[2] for y in returns],c="b")
		else: plt.scatter([x[1] for x in returns],[y[2] for y in returns],c="r",s=weights)
		
		
		name = "figures/"+ticker_pair[0]+"|"+ticker_pair[1]+str(self.working_days)+("_w" if weights!=None else "")+".png"


		plt.title("Returns for "+ticker_pair[0]+" and "+ticker_pair[1]+" over "+str(self.working_days)+" days")
		plt.savefig("figures/"+ticker_pair[0]+ticker_pair[1]+str(self.working_days)+".png")

	def get_PairedReturns(self):
		return_dict = defaultdict(lambda:(list(),list()))
		for tickers,data in self.PairedReturns.iteritems():
			for d in data:
				return_dict[tickers][0].append(d[1])
				return_dict[tickers][1].append(d[2])
		return return_dict



if __name__ =="__main__":
	SI = StockInformation()
	print SI.RecordedDays[0]

