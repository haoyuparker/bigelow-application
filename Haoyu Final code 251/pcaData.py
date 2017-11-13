#Filename:pcaData.py 
#CS251, Project 6 
#used to support PCA analysis 
#Haoyu Song 
#Feb 22, 2017 


import data 
import copy 


class PCAData(data.Data):
	
	def __init__(self,headers,matrix,evals,evecs,means,name=""):
		
		data.Data.__init__(self)
		
		
		#first set original fields 
		#notice that pdata is completely numeric 
		for i in range (matrix.shape[1]):
			self.raw_headers.append(name+"_"+"PC"+str(i))  
			self.raw_types.append("numeric")
			self.headers.append(name+"_"+"PC"+str(i))

		
		for i in range(matrix.shape[0]):
			numbers=[]
			for j in range(matrix.shape[1]):
				numbers.append(str(matrix[i,j]))
			self.raw_data.append(numbers)
		
		#set self.raw_headers
		col= 0
		for item in self.headers:
			self.header2raw[item] = col
			self.header2matrix[item]=col
			col+=1

		self.matrix_data=matrix
		
		
		#new fields 
		self.data_headers=headers #the headers of the original data used to create projected data
		self.evals=evals #a single row matrix keeping the eigen values 
		self.evecs=evecs #numpy matrix with each eigen vector saved as a row 
		self.means=means #a single row matrix keeping the means  
		
		
		
		
		
		
		
	def get_eigenvalues(self):
		return self.evals.copy()
		
	
	def get_eigenvectors(self):
		return self.evecs.copy()
		
		
	def get_data_means(self):
		return self.means.copy()
		
	def get_data_headers(self):
		return copy.deepcopy(self.data_headers)
		
	
	'''
	return the list of cumulative percentage of each eigen vector 
	'''
	def get_cumulative(self):
		sum=0
		for eval in self.evals:
			sum=sum+eval
		
		cumulative=[]
		cumu=0
		for eval in self.evals:
			cumu=cumu+eval
			cumulative.append(cumu/sum)
			
		return cumulative













