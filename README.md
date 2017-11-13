# bigelow-application

This is my final project of CS251, data analysis and visualization. This project, unlike previous ones, has little instructions 
and I completed it on my own. The main work is in wordPrime.py. 

The project is based on wordPrime.py, which records how many times people associate one word (cue) with another word (target)
in lingustic experiments. 

1)  Use "python wordPrime.py" to execute 


wordPrime.py first cleans and adds more information to the original data and save them in wordPrimeComplete.CSV. Then it 
divides the pairs of words into four categories based on their frequencies of associations and splits wordPrimeComplete.csv
into train and test data. Next it buids a Naive Bayes classifier based on four parameters, a KNN classifier based on four 
paramters, a KNN classifier based on ALL prameters. It turns out that the first two classifiers are not good enought but 
the complete KNN classifier can give very good predictions. 

Due to the nature of KNN classifier, the program might take about 10 minutes to finish. 


2) use "python display.py" to execute 

A GUI application will appear. Then click "File" and choose "wordPrimeComplete.csv." Then one can apply principal component 
analysis, linear regression etc. to the data and see its visual effect.

NOTE: I have thought of using my project at Purdue cs deparmtnet instead. But that project contains too much number theory 
stuff to fully understand. So I end up choosing my final project of cs251, which I belive is very relevant to the Bigelow 
summer internship. 
