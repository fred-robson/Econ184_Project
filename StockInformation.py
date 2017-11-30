import csv
from collections import defaultdict,OrderedDict
from datetime import datetime,timedelta
from itertools import combinations
import matplotlib.pyplot as plt
import matplotlib
import sys


QUANDL_API_KEY = "XwCG5EsTRsY4yLRUPLXv"

class StockInformation():

	def __init__(self,working_days=5,start_year = 1990,end_year=2017,verbose=False,limit=float("inf")):
		self.working_days = working_days
		self.verbose = verbose
		self.start_year = start_year
		self.end_year = end_year
		self.limit = limit

		self.Data = defaultdict(lambda:OrderedDict())
		self.RecordedDays = set()
		self.populate_StockHistory()
		
	def populate_StockHistory(self):
		#Reads the csv and puts relevant info in Data
		if self.verbose: print "Reading CSV"
		with open("prices.csv") as csv_file: 
			reader = csv.DictReader(csv_file)
			prev_row = None
			for i,row in enumerate(reader):
				
				if self.verbose and i % 100000 == 0: print str(i)+" rows have been read"
				
				try: 
					ticker = row['ticker']
					date = datetime.strptime(row['date'],"%Y-%m-%d")
					if date.year<self.start_year or date.year>self.end_year: continue
					adj_close = float(row["adj_close"])#adj_close = Close adjusted for stock splits and dividends
					self.Data[ticker][date] = adj_close #Note that it 
					self.RecordedDays.add(date)
				except:
					if self.verbose: print row
				
				if i >= self.limit: break
				
		if self.verbose: print "Finished Reading CSV"
		self.RecordedDays = list(self.RecordedDays)
		self.RecordedDays.sort()

	def ensure_data_complete(self):
		'''
		Returns all the stocks that do not have enough data across the whole time period
		'''
		longest_dates = -1
		for stock,dates in self.Data.iteritems():
			if len(dates) >longest_dates: longest_dates = len(dates)

		to_delete = set()
		for stock,dates in self.Data.iteritems():
			if len(dates) < longest_dates-10: #Give a little bit of leeway
				to_delete.add(stock)
		
		return to_delete
		


	def get_return(self,ticker,start,end):
		if start in self.Data[ticker]: start_p = self.Data[ticker][start]
		else: return None
		
		if end in self.Data[ticker]: end_p = self.Data[ticker][end]
		else: return None

		return ((end_p / start_p) -1.0)*100 #Returns in percentage terms

	def get_PairwiseReturn(self,t1,t2):
		'''
		Gets the paired returns for each of the stocks. Returns are measured over @working_days in work days 
		'''	

		return_val = [[],[],[]]

		if len(self.Data[t1])<len(self.Data[t2]): 
			tsmall,tlarge = t1,t2
			ts_index,tl_index = 1,2
		else: 
			tlarge,tsmall = t1,t2
			ts_index,tl_index = 2,1
			
		dates = list(self.Data[tsmall])
		
		if len(dates) == 0: 
			return return_val

		curr_index = 0 
		start = dates[0]

		while(True):
			curr_index += self.working_days
			if curr_index>len(dates)-1: break
			end = dates[curr_index]
			
			ts_return = self.get_return(tsmall,start,end)
			tl_return = self.get_return(tlarge,start,end)
			
			if ts_return !=None and tl_return !=None:
				return_val[0].append((start,end))
				return_val[ts_index].append(ts_return)
				return_val[tl_index].append(tl_return)

			start = end

		return return_val


	def plot_stockprice(self,ticker):
		prices = self.Data[ticker]
		dates = matplotlib.dates.date2num([x for x in prices])
		values = [x for x in prices.values()]
		plt.clf()
		plt.plot(dates, values)
		plt.title("Adjusted Closing Price of "+ticker)
		plt.show()

	def plot_pairwise(self,ticker_pair,weights=None):
		t1,t2 = ticker_pair
		returns = self.get_PairwiseReturn(t1,t2)
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




if __name__ =="__main__":
	SI = StockInformation(1,2000,2005,limit=100000)
	SI.ensure_data_complete()

	print SI.RecordedDays[0]

