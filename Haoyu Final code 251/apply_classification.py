#apply_classification.py
#author:Haoyu Song 

import sys
import data
import classifiers
import analysis as a
import csv


'''
command-line method 
reads in train file(s), let the user select classifcation scheme and parameter,
and apply the classifier to test file
'''
def main(argv):
	

	# usage
	if len(argv) < 3:
		print 'Usage: python %s <training data file> <test data file> <optional training category file> <optional test category file> <optional classify method>' % (argv[0])
		exit(-1)

	# read the training and test sets
	#manatory 
	train_data = data.Data(argv[1])
	test_data = data.Data(argv[2])

	
	# let the use select classification type and parameter 
	type = raw_input("Select classfier (NB or KNN)")
	if type=="KNN":
		K=raw_input("how many categories to use?(integer)or skip")
		print K 
		if K=="":
			pass 
		else:
			try:
				K=int(K)
 			except ValueError:
 				print "Integer Value Please"
 				return 
		
		
		
	
		
	#now build the training matrix and category matrix 
	if len(argv)>=4: #train categories 
		trainCatData= data.Data(argv[3])
		trainCats = trainCatData.get_columns( [trainCatData.get_headers()[0]] )
		A = train_data.get_columns( train_data.get_headers() )
	else:
		trainCats = train_data.get_columns( [train_data.get_headers()[-1]] )
		A = train_data.get_columns( train_data.get_headers()[:-1] )
		
		
	#now build classifier 
	if type=="NB":
		classifier=classifiers.NaiveBayes()
		classifier.build(A,trainCats)
	elif type=="KNN":
		classifier=classifiers.KNN()
		if K=="":#classify using all points 
			classifier.build(A, trainCats)
		else:
			classifier.build(A, trainCats,K)
		
	else:
		print "unknown classifier type"
		return 
		
		
	
	#now set test label and test data 
	if len(argv)>=5:
		testCatData=data.Data(argv[4])
		testCats=testCatData.get_columns([testCatData.get_headers()[0]])
		B=test_data.get_columns(test_data.get_headers())
	else: #assume the category is saved at the last column 
		testCats=test_data.get_columns([test_data.get_headers()[-1]])
		B=test_data.get_columns(test_data.get_headers()[:-1])
		
		
	#make the classification and print out the confusion matrix 
	print "first classify the trainning set"
	ctraincats, ctrainlabels=classifier.classify(A)
	confusion=classifier.confusion_matrix(trainCats,ctraincats)
	print "the confusion matrix is\n"
	print classifier.confusion_matrix_str(confusion)
	
	
	print "\n now classifiy the testing set"
	ctestcats,ctestlabels=classifier.classify(B)
	confusion=classifier.confusion_matrix(testCats,ctestcats)
	print "the confusion matrix is\n"
	print classifier.confusion_matrix_str(confusion)
	
		
	#write out to an output file 
	name=raw_input("choose a CSV output file name" )
	name=name+".csv"
	labels=[]
	for i in range(len(ctestcats)):
		labels.append(ctestlabels[i,0])
	d=test_data.add_column("predicted_result","numeric",labels)	
	d.write(name)
		
		
	
	
	

if __name__ == "__main__":
    main(sys.argv)
