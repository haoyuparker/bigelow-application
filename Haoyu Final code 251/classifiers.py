# Template by Bruce Maxwell
# Spring 2015
# CS 251 Project 8
#
# Classifier class and child definitions

import sys
import data
import analysis as an
import numpy as np
import math 
import scipy

class Classifier:

    def __init__(self, type):
        '''The parent Classifier class stores only a single field: the type of
        the classifier.  A string makes the most sense.

        '''
        self._type = type

    def type(self, newtype = None):
        '''Set or get the type with this function'''
        if newtype != None:
            self._type = newtype
        return self._type

    
    
    '''
    this shows the accuracy of the classifier
    '''
    def confusion_matrix( self, truecats, classcats ):
        '''Takes in two Nx1 matrices of zero-index numeric categories and
        computes the confusion matrix. The rows represent true
        categories, and the columns represent the classifier output.
    	'''
    	unique1,mapping1=np.unique(np.array(truecats.T),return_inverse=True)
    	unique2,mapping2=np.unique(np.array(classcats.T),return_inverse=True)
    	N=len(unique1)
    	confusion=np.zeros((N,N))
    	
    	for i in range(len(truecats)):
    		x=mapping1[i]
    		y=mapping2[i]
    		confusion[x,y]=confusion[x,y]+1 
    	
    	return confusion 
		
		
		

    def confusion_matrix_str( self, cmtx ):
        '''Takes in a confusion matrix and returns a string suitable for printing.'''
        N=cmtx.shape[0]
        s = ''
        
        #first deal with the header row 
        first_row="type "
        for i in range(N):
        	index=str(i+1)+" "
        	first_row=first_row+index
        
        s=s+first_row+"\n"
        
        #now deal with each row of the confusion matrix 
        for i in range(N):
        	row=str(i+1)+"    "
        	for j in range(N):
        		index=str(int(cmtx[i,j]))+" "
        		row=row+index
        	s=s+row+"\n"
        	
        	
        return s 
        		
        
        
        
        

        return s

    def __str__(self):
        '''Converts a classifier object to a string.  Prints out the type.'''
        return str(self._type)



class NaiveBayes(Classifier):
    '''NaiveBayes implements a simple NaiveBayes classifier using a
    Gaussian distribution as the pdf.

    '''
    
    def __init__(self, dataObj=None, headers=[], categories=None):
        '''Takes in a Data object with N points, a set of F headers, and a
        matrix of categories, one category label for each data point.'''

        # call the parent init with the type
        Classifier.__init__(self, 'Naive Bayes Classifier')
        
        # store the headers used for classification
        self.headers = headers
        
        # number of classes and number of features
        self.class_num= 0
        self.feature_num = 0
        
        # original class labels
        self.labels = ([])
        
        
        # unique data for the Naive Bayes: means, variances, scales
        self.class_means = ([])
        self.class_vars = ([])
        self.class_scales = ([])
        
       
       
       
        # if given data,
        # call the build function
        if dataObj != None:
        	self.build(dataObj, categories)
    
    
    
    
    

    def build( self, A, categories, K=None):
		'''Builds the classifier give the data points in A and the categories'''

		# figure out how many categories there are and get the mapping (np.unique)
		unique, mapping = np.unique( np.array(categories.T), return_inverse=True)

		# create the matrices for the means, vars, and scales
		# the output matrices will be categories (C) x features (F)
		#first set as zero matrices 
		self.class_means = np.zeros((len(unique),A.shape[1]))
		self.class_vars = np.zeros((len(unique), A.shape[1]))
		self.class_scales = np.zeros((len(unique), A.shape[1]))
		output = np.zeros(len(unique))
	
		# compute the means/vars/scales for each class
		#here we assume Gaussian distribution probability model 
		for i in range (len(unique)):
			self.class_means[i,:] = np.mean(A[(mapping==i),:], axis=0)
			self.class_vars[i,:] = np.var(A[(mapping==i),:], axis=0, ddof=1)
			self.class_scales[i,:] = np.divide(np.ones((1.0,self.class_vars.shape[1])),np.sqrt(2.0*math.pi*self.class_vars[i,:]))

		
		# store any other necessary information: # of classes, # of features, original labels
		self.class_num = unique.shape[0]
		self.feature_num = A.shape[1]
		self.labels = unique

		return

    
    
  

    
    
    def classify( self, A, return_likelihoods=False ):
        '''Classify each row of A into one category. Return a matrix of
        category IDs in the range [0..C-1], and an array of class
        labels using the original label values. If return_likelihoods
        is True, it also returns the NxC likelihood matrix.

        '''

        # error check to see if A has the same number of columns as
        # the class means
        if A.shape[1]!= self.class_means.shape[1]:
        	print "dimension NOT matching"
        	return 
        	
        
        
        
        
        # make a matrix that is N x C to store the probability of each
        # class for each data point
        #P = '' # a matrix of zeros that is N (rows of A) x C (number of classes)
        P=np.zeros((A.shape[0],self.class_num))


        # calculate the probabilities by looping over the classes
        #  with numpy-fu you can do this in one line inside a for loop
        for i in range(A.shape[0]):
        	for j in range(self.class_num):
        		P[i,j] = 1.0/self.class_num * np.prod(np.multiply(self.class_scales[j], (np.exp(-1.0*np.square(np.subtract(A[i,:], self.class_means[j]))/(2.0*self.class_vars[j])))))


        # calculate the most likely class for each data point
        cats = np.matrix(np.argmax(P, axis=1)).T

        # use the class ID as a lookup to generate the original labels
        labels = self.labels[cats]

        if return_likelihoods:
            return cats, labels, P

        return cats, labels

    def __str__(self):
        '''Make a pretty string that prints out the classifier information.'''
        s = "\nNaive Bayes Classifier\n"
        for i in range(self.class_num):
            s += 'Class %d --------------------\n' % (i)
            s += 'Mean  : ' + str(self.class_means[i,:]) + "\n"
            s += 'Var   : ' + str(self.class_vars[i,:]) + "\n"
            s += 'Scales: ' + str(self.class_scales[i,:]) + "\n"

        s += "\n"
        return s
        
    def write(self, filename):
        '''Writes the Bayes classifier to a file.'''
        # extension
        return

    def read(self, filename):
        '''Reads in the Bayes classifier from the file'''
        # extension
        return



'''
easy to implement but computationally expensive
'''

class KNN(Classifier):

    def __init__(self, dataObj=None, headers=[], categories=None, K=None):
        '''Take in a Data object with N points, a set of F headers, and a
        matrix of categories, with one category label for each data point.'''

        # call the parent init with the type
        Classifier.__init__(self, 'KNN Classifier')
        
        # store the headers used for classification
        self.headers = headers
        
     
        # number of classes and number of features
    	self.feature_num = 0
        self.class_num = 0
        
        
        
        # original class labels
        self.labels = ([])
        
       
       
        # unique data for the KNN classifier: list of exemplars (matrices)
        self.exemplars = []
        
        # if given data,
            # call the build function
        if dataObj != None:
        	self.build(dataObj, categories, K)
        

    def build( self, A, categories, K = None ):
		'''Builds the classifier give the data points in A and the categories'''

		# figure out how many categories there are and get the mapping (np.unique)
		unique, mapping = np.unique( np.array(categories.T), return_inverse=True)
		row_num=unique.shape[0]
	
		# for each category i, build the set of exemplars
			# if K is None
				# append to exemplars a matrix with all of the rows of A where the category/mapping is i
			# else
				# run K-means on the rows of A where the category/mapping is i
				# append the codebook to the exemplars
		for i in range(row_num):
			if K == None:
				self.exemplars.append(A[(mapping==i),:]) #use all points 
			else:
				codebook, codes, error = an.Analysis().kmeans_matrix(A[(mapping==i),:], K, whiten=False) #use points after clustering
				self.exemplars.append(codebook)

		# store any other necessary information: # of classes, # of features, original labels
		self.class_num = row_num
		self.feature_num = A.shape[1]
		self.labels = unique
	
		return

    def classify(self, A, K=2, return_distances=False,distance="Euclidean"):
		'''Classify each row of A into one category. Return a matrix of
		category IDs in the range [0..C-1], and an array of class
		labels using the original label values. If return_distances is
		True, it also returns the NxC distance matrix.

		The parameter K specifies how many neighbors to use in the
		distance computation. The default is three.'''

		# error check to see if A has the same number of columns as the class means
		if A.shape[1] != self.exemplars[0].shape[1]:
			print "unmatching size of the data set and the class means"
			return

		# make a matrix that is N x C to store the distance to each class for each data point
		D = np.zeros((A.shape[0],self.class_num))
	
		# for each class i
			# make a temporary matrix that is N x M where M is the number of examplars (rows in exemplars[i])
			# calculate the distance from each point in A to each point in exemplar matrix i (for loop)
			# sort the distances by row
			# sum the first K columns
			# this is the distance to the first class
		for i in range(self.class_num):
			temp = np.zeros((A.shape[0],self.exemplars[i].shape[0]))
			for j in range(A.shape[0]):
				for k in range(self.exemplars[i].shape[0]):
					p1 = A[j]
					p2 = self.exemplars[i][k]
					if distance=="Euclidean":
						temp[j,k] = float(scipy.spatial.distance.euclidean(p1,p2))
					elif distance=="Manhattan":
						temp[j,k]=float(scipy.spatial.distance.cityblock(p1,p2))
					elif distance=="Cosine":
						temp[j,k]=float(scipy.spatial.distance.cosine(p1,p2))
					else:
						print "unknown metric"
						return 
			
			temp = np.matrix(np.sort(temp, axis=1))
			temp = np.matrix(np.sum(temp[:,:K], axis=1))
			D[:,i] = temp[:,0].flatten()

		# calculate the most likely class for each data point
		# take the argmin of D along axis 1
		cats = np.matrix(np.argmin(D, axis=1)).T

		# use the class ID as a lookup to generate the original labels
		labels = self.labels[cats]

		if return_distances:
			return cats, labels, D

		return cats, labels

    def __str__(self):
        '''Make a pretty string that prints out the classifier information.'''
        s = "\nKNN Classifier\n"
        for i in range(self.class_num):
            s += 'Class %d --------------------\n' % (i)
            s += 'Number of Exemplars: %d\n' % (self.exemplars[i].shape[0])
            s += 'Mean of Exemplars  :' + str(np.mean(self.exemplars[i], axis=0)) + "\n"

        s += "\n"
        return s


    def write(self, filename):
        '''Writes the KNN classifier to a file.'''
        # extension
        return

    def read(self, filename):
        '''Reads in the KNN classifier from the file'''
        # extension
        return
    


    

