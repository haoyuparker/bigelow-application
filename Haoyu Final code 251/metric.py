#metric.py 
#author Haoyu Song 
#This file has a bunch of function dealing with different metrics 

import numpy as np
import math  
import scipy.spatial.distance as dis





'''
given a matrix, 
calcuate the mean using specified distance metric 
'''
def calculate_means(matrix,metric="Euclidean"):
	
	if matrix.shape[0]==0 and matrix.shape[1]==0:
		print "EMPTY matrix"
		return 
		
	if metric=="Euclidean":
		means=np.mean(matrix,axis=0)
	
	elif metric=="Manhattan":
		means=np.median(matrx,axis=0)
	
	elif metric=="Cosine": 
		#first normalized to unite length 
		normalized=norm(matrix)
		means=np.mean(normalized,axis=0) 
	
	else:
		return 
		
	return means 
	








'''
given two data points stored as two 1*N np matrices,
calculate their distance using specified metric
'''
def distance(p1,p2,metric="Euclidean"):

	if p1.shape[1]!=p2.shape[1]:
		print "dimension NOT matching"
		return 
		
	if metric=="Euclidean":
		result=dis.euclidean(p1,p2)
		
	
	elif metric=="Manhattan":
		result=dis.cityblock(p1,p2)
		
	
	elif metric=="Cosine":
		result=dis.cosine(p1,p2)
	
	else: 
		return 
		
	
	return result 
	
	
	

'''
given a matrix, convert each row to unit length 
'''	
def norm(matrix):
	
	length=matrix.shape[0]
	width=matrix.shape[1]
	results=[]
	
	for i in range(length):
		square=0
		#first calculate the length of each row 
		for j in range(width):
			square=square+pow(matrix[i,j],2)
		
		length=math.sqrt(square)
	
		result=[]
		for j in range(width):
			result.append(matrix[i,j]/length)
	
		
		
		results.append(result)
			
	
	return np.matrix(results)
		
		


	
	


