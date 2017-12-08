class OptimalPortfolioFinder():

	def __init__(self,expected_returns,covariances,risk_free_return,verbose=False):
		self.expected_returns = expected_returns
		self.covariances = covariances
		self.risk_free = risk_free_return
		self.weights = [1.0/len(expected_returns) for _ in expected_returns]


	def portfolio_expected_return(self):
		'''
		Finds the expected return for the portfolio given weights = self.weights
		'''
		return sum(self.weights[i]*exp_r for i,exp_r in enumerate(self.expected_returns))

	def portfolio_variance(self):
		#Finds the variance of the portfolio given self.portfolio
		p_variance = 0
		for i,row in enumerate(self.covariances):
			for j,cov_val in enumerate(row):
				p_variance+=self.weights[i]*self.weights[j]*cov_val
		return abs(p_variance)

	def find_optimal_weights(self,numIters,eta=0.01):
		'''
		Uses gradient descent to find the portfolio that maxmizes Sharpes Ratio.
		Updates self.weights to that optimal porfolio
		@params: 
			- numIters: number of iterations for gradient descent
			- eta: the step size
		'''
		for step in range(numIters):
			grad = self.sharpes_ratio_gradient()
			updatedWeights = [w+(eta * grad[i]) for i,w in enumerate(self.weights)]
			self.weights = updatedWeights
			for i,w in enumerate(self.weights): self.weights[i] = max(w,0.0001) #ensure weights never go negative
			self.normalize_weights()

		self.normalize_weights()
		return self.weights

	def normalize_weights(self):
		for i,w in enumerate(self.weights): self.weights[i] = max(w,0.0001) 
		weight_sum = sum(self.weights)
		normalized_weights = [w/weight_sum for w in self.weights]
		self.weights = normalized_weights

	def sharpesRatio(self):
		return (self.portfolio_expected_return() - self.risk_free)/(self.portfolio_variance()**(1.0/2))

	def sharpes_ratio_gradient(self):
		'''
		Calculates the gradient of sharpes ratio
		delta(Sharpe)/delta(w_i) = 
		r_i/Var(Portfolio) - Sum(w_j*Cov(i,j))(E(R_portfolio) - risk_free)/Var(portfolio)^3/2 
		'''
		p_er = self.portfolio_expected_return()
		p_var = self.portfolio_variance() 
		if p_var<=0: print p_var
		p_sd = p_var**(1.0/2)
		grad = []

		for i,w_i in enumerate(self.weights):
			partial_derivative = (self.expected_returns[i]/p_sd) 
			partial_derivative -= sum(self.covariances[i][j]*w_j*(p_er-self.risk_free)for j,w_j in enumerate(self.weights))
			partial_derivative /= (p_sd**3.0)
			grad.append(partial_derivative)								 
		return grad


if __name__ == "__main__":
	expected_returns = [1.3,1.2]
	covariances = [[0.2,-0.1],[-0.1,0.8]]

	op = OptimalPortfolioFinder(expected_returns,covariances,0)
	op.find_optimal_weights(1000,0.01)
	print op.weights