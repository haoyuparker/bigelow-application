#wordPrime.py 
#the functions needed to do analysis and visulization of wordPrime.csv
import csv 
import data 
import classifiers 




'''
calculate the levenshteinDistance between two words,
which measures how similar two string patterns are 
use dynamic programming
'''
def levenstein(s,t):
	
	
	m=len(t)
	n=len(s)
	
	
	if n==0:
		return m
	if m==0:
		return n 
		
	#set up 
	matrix=[]
	for i in range(m+1):
		matrix.append([])
		for j in range(n+1):
			matrix[i].append(0)
			
	for i in range(n+1):
		matrix[0][i]=i
		
	for i in range(m+1):
		matrix[i][0]=i
		
	
	#use dynamic programming 
	for i in range(1,m+1):
		for j in range(1,n+1):
			if s[j-1]==t[i-1]:
				cost=0
			else:	
				cost=1 
			
			m1=matrix[i-1][j]+1
			m2=matrix[i][j-1]+1
			m3=matrix[i-1][j-1]+cost
			
			matrix[i][j]=min(m1,m2,m3)
			
			
	return matrix[m][n]
	
			





	




'''
clean the data and write the result to a csv file
'''
def clean_data():
	
	fp=open("wordPrime.csv","rU")
	lines=fp.readlines()
	length=len(lines)-2
	headers=lines[0].split(",")
	types=lines[1].split(",")
	
	
	#pay particular attention to numeric columns 
	numeric=[]
	for i in range(len(types)):
		if types[i]=='numeric' or types[i]=='numeric\n':
			numeric.append(i)

	with open("wordPrimeClean.csv",'wb') as f:
		writer = csv.writer(f)
		writer.writerow(headers)
		writer.writerow(types)
		for i in range(2,length):
			bad=False #indicating whether there is a bad value in numeric column
			row=lines[i].split(",")
			for j in numeric:
				word=row[j].strip('\n')
				if isFloat(word)==False:
					bad=True
					break 
					
					
			
			if bad==False:
				writer.writerow(row)
				
				
		
			
'''
measure the distribution of the frequency of the data pair 
and make classifications according to the distribution 
'''
def countFrequency():
	distribution=[0,0,0,0,0]
	d=data.Data("wordPrimeClean.csv")
	for i in range(2,d.get_raw_num_rows()):
		freq=int(d.get_raw_value(i,"Frequency"))
		if freq==1:
			distribution[0]=distribution[0]+1
		elif freq==2:
			distribution[1]=distribution[1]+1
		elif freq==3:
			distribution[2]=distribution[2]+1
		elif freq==4:
			distribution[3]=distribution[3]+1
		else:
			distribution[4]=distribution[4]+1
	
	print "the pair with frequency 1 is ",distribution[0]
	print "\n the pair with frequency 2 is ",distribution[1] 
	print "\n the pair with frquency 3,4 is ",distribution[2]+distribution[3]
	print "\n the pair with frequency no smaller than 5 is ",distribution[4]
				
				
				


'''
add two columns of levenstein distances for spelling and pronouncation respectively
also add the category label column 
'''
def complete_data():		
	
	clean_data();
	d=data.Data("wordPrimeClean.csv")
	
 
	spelling_dist=[]
	pro_dist=[]
	categories=[]
	
	for i in range(2,d.get_raw_num_rows()):
		
		#set l_distance for spelling 
		target=d.get_raw_value(i,"Target")
		cue=d.get_raw_value(i,"Cue")
		spelling_dist.append(levenstein(cue,target))
		
		#set l_distance for pronouncation
		target_pro=d.get_raw_value(i,"PhonTarget")
		cue_pro=d.get_raw_value(i,"PronCue")
		pro_dist.append(levenstein(target_pro,cue_pro))
		
		#set category column 
		cat=int(d.get_raw_value(i,"Frequency"))
		if cat==1:
			categories.append(0)
		elif cat==2:
			categories.append(1)
		elif cat==3 or cat==4:
			categories.append(2)
		else:
			categories.append(3)
		
	
	
	d=d.add_column("word_dist","numeric",spelling_dist)
	d=d.add_column("pron_dist","numeric",pro_dist)
	d=d.add_column("category","numeric",categories)
	
	
	
	
	d.write("wordPrimeComplete.csv")
	
	
	
	
	
	
				
				
				
				
				
				
			


'''
divide wordPrime.csv into training and testing set 
here I use a 9:1 ration
'''
def divide_train_test():

	complete_data(); 
	d=data.Data("wordPrimeComplete.csv")
	headers=d.get_raw_headers()
	types=d.get_raw_types()
	length=d.get_raw_num_rows()-2
	
	
	
	with open("wordPrimeTrain.csv",'wb') as f:
		with open ("wordPrimeTest.csv",'wb') as g:
		
			trainWriter=csv.writer(f)
			trainWriter.writerow(headers)
			trainWriter.writerow(types)
			
			testWriter=csv.writer(g)
			testWriter.writerow(headers)
			testWriter.writerow(types)
		
		
			for i in range(2,length):
				row=d.get_raw_row(i)
				if i%2==0:
					trainWriter.writerow(row)
				else:
					testWriter.writerow(row)
				
			



'''
build a Naive Bayes classifier based on word distance, pronunication distance, 
target frequency, and cue frequency
'''
def NB_classify():
	# read the training and test sets
	dtrain = data.Data("wordPrimeTrain.csv")
	dtest = data.Data("wordPrimeTest.csv")
	
	
	A = dtrain.get_columns( ["word_dist","pron_dist","Target_Freq_N","cue_Freq_N"] )
	B = dtest.get_columns( ["word_dist","pron_dist","Target_Freq_N","cue_Freq_N"] )
	traincats= dtrain.get_columns(["category"] )
	testcats = dtest.get_columns(["category"])
	
	
	
	
	# create a new classifier
	nbc = classifiers.NaiveBayes()
	
	# build the classifier using the training data
	nbc.build( A, traincats,5)
	
	# use the classifier on the training data
	print "\nNaive Bayes,confusion matrix\n"
	print "on train data\n"
	ctraincats, ctrainlabels = nbc.classify( A )
	confusion=nbc.confusion_matrix(traincats,ctrainlabels)
	print nbc.confusion_matrix_str(confusion)
	
	print "on test data\n"
	ctestcats, ctestlabels = nbc.classify( B )
	confusion=nbc.confusion_matrix(testcats,ctestlabels)
	print nbc.confusion_matrix_str(confusion)
	
	

'''
build a KNN classifier based on word distance, pronunciation distance, 
target freuency, and cue frequency
'''
def KNN_classify_partial():
	# read the training and test sets
	dtrain = data.Data("wordPrimeTrain.csv")
	dtest = data.Data("wordPrimeTest.csv")
	
	
	A = dtrain.get_columns( ["word_dist","pron_dist","Target_Freq_N","cue_Freq_N"] )
	B = dtest.get_columns( ["word_dist","pron_dist","Target_Freq_N","cue_Freq_N"] )
	traincats= dtrain.get_columns(["category"] )
	testcats = dtest.get_columns(["category"])
	
	
	
	
	# create a new classifier
	nbc = classifiers.KNN()
	

	# build the classifier using the training data
	nbc.build( A, traincats,5)
	
	
	# use the classifier on the training data
	print "partial KNN, confusion matrix\n"
	print "on train data\n"
	ctraincats, ctrainlabels = nbc.classify( A)
	confusion=nbc.confusion_matrix(traincats,ctrainlabels)
	print nbc.confusion_matrix_str(confusion)
	
	print "on test data\n"
	ctestcats, ctestlabels = nbc.classify( B)
	confusion=nbc.confusion_matrix(testcats,ctestlabels)
	print nbc.confusion_matrix_str(confusion)
	




'''
build a KNN classifier based on ALL parameters 
'''
def KNN_classify_complete():
	# read the training and test sets
	dtrain = data.Data("wordPrimeTrain.csv")
	dtest = data.Data("wordPrimeTest.csv")
	
	
	A = dtrain.get_columns(dtrain.get_headers()[:-1])
	B = dtest.get_columns(dtest.get_headers()[:-1])
	traincats= dtrain.get_columns(["category"] )
	testcats = dtest.get_columns(["category"])
	
	
	
	
	# create a new classifier
	nbc = classifiers.KNN()
	
	# build the classifier using the training data
	nbc.build( A, traincats,5)
	
    
	# use the classifier on the training data
	print "complete KNN, confusion matrix\n"
	print "on train data\n"
	ctraincats, ctrainlabels = nbc.classify( A)
	confusion=nbc.confusion_matrix(traincats,ctrainlabels)
	print nbc.confusion_matrix_str(confusion)
	
	print "on test data\n"
	ctestcats, ctestlabels = nbc.classify( B)
	confusion=nbc.confusion_matrix(testcats,ctestlabels)
	print nbc.confusion_matrix_str(confusion)





'''
helper function to test whether a string represents a float value
'''
def isFloat(string):
	
	try:
		float(string)
		return True
 	except ValueError:
 		return False
		
	


	

	
	
if __name__=="__main__":
	divide_train_test()
	NB_classify()
	KNN_classify_partial()
	KNN_classify_complete()
	
