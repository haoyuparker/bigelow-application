#Fielname:analysis.py 
#cs 251,Project 2 
#Author: Haoyu Song
#Feb 22,2016 

import numpy as np
import data
import math 
from scipy import stats 
import pcaData 
import scipy.cluster.vq as vq
import scipy.spatial.distance as dis
import metric as m
import random 

'''
a class that analyzes a data object 
'''
class Analysis:
	
	def __init__(self):
		return 

	
	
	
	'''
	takes in a list of column headers and a data object 
	returns a list of 2 elements lists with the minimum and matimum 
	dat specifies a Data object
	'''
	def data_range(self,headers,dat):
	 
		list=[]
		matrix=dat.get_columns(headers)
		width=matrix.shape[1]
		maxList=matrix.max(0)
		minList=matrix.min(0)
		for i in range(width):
			max=maxList[0,i]
			min=minList[0,i]
			list.append([max,min])
		return list
		
		
	'''
	takes in a list of column headers and data object 
	return a list of mean values for each column
	'''
	def mean(self,headers,dat):
		
		matrix=dat.get_columns(headers)
		mean=np.mean(matrix,axis=0)
		return mean
		
		
	'''
	takes in a list of column headers and data object 
	return a list of standard deviation for each column
	'''
	def stdev(self,headers,dat):
		
		matrix=dat.get_columns(headers)
		stdev=matrix.std(0)
		return stdev


	'''
	takes in a list of column headers and data object 
	returns a matrix with each column normalized
	min in each column is mapped to zero and max in each column is mapped to one 
	'''
	def normalize_columns_separately(self,headers,dat):
		
		matrix=dat.get_columns(headers)
		width=matrix.shape[1]
		for j in range(width):
			max=matrix.max(0)[0,j]
			min=matrix.min(0)[0,j]
			for i in range(len(matrix)):
				matrix[i,j]=(matrix[i,j]-min)/(max-min)
		return matrix
		
	
	
	'''
	takes in a list of column headers and data object
	returns a matrix with EVERY entry normalized 
	the overall min is mapped to zero and max is mapped to one 
	'''
	def normalize_columns_together(self,headers,dat):
		
		matrix=dat.get_columns(headers)
		max=matrix.max()
		min=matrix.min()
		for i in range(len(matrix)):
			for j in range(len(headers)):
				matrix[i,j]=(matrix[i,j]-min)/(max-min)
		
		
		return matrix
		
		
	# project 2 extensions 
	#additional methods of manipulating data 
	
	
	
	'''
	taken in a list of column headers and data object 
	returns a list of medians for each column 
	'''	
	def mode(self,headers,dat):
		
		matrix=dat.get_columns(headers)
		mode=stats.mode(matrix)
		return mode[0]
	
	
	
	
	'''
	take in a list of column headers and data object 
	returns a list of median for each column 
	'''
	def median(self,headers,dat):
		
		matrix=dat.get_columns(headers)
		median=np.median(matrix,axis=0)
		return median
		
		
		
		
	#project 5 
	'''
	given a dependent variable and a list of independent variables, 
	return info about the BEST linear fit 
	'''
	def linear_regression(self,dat,ind,dep):
		
		#set up the system y=Ax+b
		row_num=dat.get_raw_num_rows()-2
		ones=np.ones((row_num,1))
		A=np.hstack((dat.get_columns(ind),ones))
		y=dat.get_columns([dep])
		
		
		#using normal equation to find a solution minimizing the residue 
		AAinv=np.linalg.inv(np.dot(A.T,A))
		x=np.linalg.lstsq(A,y)
		b=x[0] #solution 
		
		
		
		#quantities indicating the quality of our model 
		N=len(y) #number of data points 
		C=len(b) #number of coefficients 
		df_e=N-C #degrees of freedom of the error 
		df_r=C-1 #degrees of freedom of the model fit 
		error=y-np.dot(A,b) #error vector 
		sse=np.dot(error.T,error)/df_e #sum squared error 
		stderr=np.sqrt(np.diagonal(sse[0,0]*AAinv ) ) #standard error 
		t =( b.T / stderr )#t_statistic 
		p=(1-stats. t.cdf(abs(t),df_e))#the probability of coefficients indicating random relationship
		r2=1-error.var()/y.var() #the R^2 coefficient indicating the quality of fit 
		
		return [(b.T).tolist()[0],sse.tolist()[0],r2,t.tolist()[0],p.tolist()[0]]
		
	
		 
	
	
	#project 6 
	'''
	given a data object and a list of headers, 
	return a pcaData object
	use singular variable decomposition  
	''' 
	def pca(self,d,headers,normalized=True,name=""):
	
		if normalized==True: 
			A=self.normalize_columns_separately(headers,d)
		else: #homogenous data 
			A=d.get_columns(headers)
		
			
		#use SVD to get eigenvalues and eigenvectors 
		m=np.mean(A,0)
		D=A-m
		U,S,V = np.linalg.svd(D, full_matrices=False)
		evals = S*S/(len(A)-1) 
		evecs = V 
		pdata = (V*D.T).T
		
		
		#create PCA object 
		 
		pca = pcaData.PCAData(headers, pdata, evals, evecs, m,name)
		return pca
		
		
		
		
		



	#project 7 
	#k-means clustering 
	
	
	'''
	perform K-means clustering by Numpy's built-in K-means capacity
	d:data oeject 
	headers:headers used for clustering 
	k:numbers of clusters to create  
	'''
	def kmeans_numpy(self,d,headers,K,whiten=True):
		A = d.get_columns(headers)
		W = vq.whiten(A)
		codebook, bookerror = vq.kmeans(W,K)
		codes, error = vq.vq(W, codebook)		
		return codebook, codes, error

	
	
	
	
	
	
	
	#now write my own k-means function 
	'''
	initialize the first K means for a matrix 
	calcualte the means of the selected categories
	if no preselected categories, just choose K random points 
	'''
	def kmeans_init(self,matrix,K,categories=None,metric="Euclidean"):
		
		
		
		length=matrix.shape[0]
		width=matrix.shape[1]
		if length==0 and width==0:
			print "empty matrix!"
			return 
		
		
		
		if categories==None:
			rowIndexes=[]
			rows=[]
			for i in range(K):
				row_num=random.randint(0,length-1)
				while row_num in rowIndexes: #ensure distinctness 
					row_num=random.randint(0,length-1)
					
				rowIndexes.append(row_num)
				rows.append(matrix[row_num,:])
				
			means=np.concatenate(rows,axis=0)

			
			
		else: 
			#category is a N*1 matrix each indexed from 0 to K-1 
			#first put all rows of the same category together
			categorized=[]
			for i in range(K):
				categorized.append([])
			for i in range(categories.shape[0]):
				id=int(categories[i,0])
				categorized[id].append(matrix[i,:])
				
				
			#now get the mean matrix for each category 
			rows=[]
			for items in categorized:
				new_matrix=np.concatenate(items,axis=0)
				mean=m.calculate_means(new_matrix,metric)
				rows.append(mean)
				
			means=np.concatenate(rows,axis=0)
			
			
		return means 
			

			
				
		
	'''
	given a matrix of means and a data object, 
	assign each point to the closest mean and return the distance 
	'''		
	def kmeans_classify(self,matrix,means,metric="Euclidean"):
		
		if matrix.shape[1]!=means.shape[1]:
			print "dimension NOT matching"
			return 
		
		distances=np.zeros((matrix.shape[0],1))
		indexes=np.zeros((matrix.shape[0],1))
		for i in range(matrix.shape[0]):
			dist=m.distance(matrix[i,:],means[0])
			index=0
			for j in range (1,means.shape[0]):
				new_dist=m.distance(matrix[i,:],means[j],metric)
				if new_dist<dist:
					dist=new_dist 
					index=j 
			
			distances[i,0]=dist 
			indexes[i,0]=index 
			
		return [indexes,distances]
			
		
		
			
		
		
	
	
	'''
	given a matrix and initial mean, keep iterating to 
	reduce the overall distances
	core of the k-means clustering 
	'''
	def kmeans_algorithm(self,A,means,distance="Euclidean"):
	
		
		MIN_CHANGE = 1e-7
		MAX_ITERATIONS=100
		D=means.shape[1]
		K=means.shape[0]
		N=A.shape[0]
	
		 
		# iterate no more than MAX_ITERATIONS
		for i in range(MAX_ITERATIONS):
			# calculate the codes
			
			codes, errors = self.kmeans_classify( A, means, distance)
			
			# calculate the new means
			newmeans = np.zeros_like( means )
			counts = np.zeros( (K, 1) )
			for j in range(N):
				newmeans[codes[j,0],:] += A[j,:]
				counts[codes[j,0],0] += 1.0
			
			# finish calculating the means, taking into account possible zero counts
			for j in range(K):
				if counts[j,0] > 0.0:
					newmeans[j,:] /= counts[j, 0]
				else:
					newmeans[j,:] = A[random.randint(0,A.shape[0]-1),:]
				
				
			# test if the change is small enough
			diff = np.sum(np.square(means - newmeans))
			means = newmeans
			if diff < MIN_CHANGE:
				break
		
		codes, errors = self.kmeans_classify( A, means, distance )
		return (means, codes, errors)
		
	
	
	'''
	Takes in a matrix and the number of clusters to create
	Computes and returns the codebook, codes and representation errors. 
	If given an Nx1 matrix of categories, it uses the category labels 
	to calculate the initial cluster means.
    '''
	def kmeans_matrix(self,A,K,metric="Euclidean", whiten=True,categories=None):
	
		if whiten==True:
			W=vq.whiten(A)
			
		else:
			W=A 
		
		codebook=self.kmeans_init(W,K,categories,metric)
		codebook,codes,error=self.kmeans_algorithm(W, codebook, metric)
		return codebook,codes,error 
		
		
	
	'''
	takes in a data object and a number of clusters to create 
	and do process above
	'''
	def kmeans(self,d,headers,K,metric="Euclidean", whiten=True,categories=None):
		A=d.get_columns(headers)
		return self.kmeans_matrix(A,K,metric,whiten,categories)	
				
				
				
				
				
				
			
				
				
	
	
	
	
	
	


   	

	