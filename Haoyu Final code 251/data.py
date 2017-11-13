#Filename:data.py 
#CS251, Project 2 
#Haoyu Song 
#Feb 22, 2016 

import csv 
import numpy as np 
import datetime 
import copy 


'''
read and write csv files 
used top query the object for information 
'''

class Data:

	def __init__(self,filename=None):
		
		#raw data fields 
		self.raw_headers=[]  #list of all headers 
		self.raw_types=[]  #list of all types 
		self.raw_data=[]   #list of list of all data; each row is a list of strings 
		self.header2raw={} #dictionary mapping header string to index of column in raw data
		
		#numeric data fields 
		self.headers=[] #list of headers of numeric columns 
		self.matrix_data=np.matrix([])#matrix of numeric data 
		self.header2matrix={} #dictionary 
		
		#enumerated data type 
		self.enumerated={} #a dictionary mapping a header to a dictionary of all items in that column 
		
		
		if filename!=None:
			self.read(filename)
	
	'''
	convert the csv input file into a list of lists
	assign values to all data_fields
	I also take the effort to strip away all blank spaces  
	'''	
	def read(self,filename=None):
		
		try:
			fp=open(filename,"rU")
			lines=fp.readlines()
				
					
		except IOError:
			print "Error: invalid file name" ,filename 
			return 
		else:
			print "file", filename, "successfully opened" 
			data=csv.reader(lines)
			fp.close()
			
		self.raw_headers=strip(data.next()) #the first line contains headers 
		self.raw_types=strip(data.next()) #the second line contains types 
		
	
		for i in range(len(lines)-2): #raw_data
			try:
				line=strip(data.next())
				self.raw_data.append(line)
			except StopIteration:
				pass
			
		for i in range(len(self.raw_headers)):#header2raw 
			self.header2raw[self.raw_headers[i]]=i
			
		self.set_numeric() #this method sets headers, matrix_data,header2matrix
		
		
		
	
	'''
	write out the data as a csv file 
	use raw input 
	'''
	def write(self,name):
		with open(name, 'wb') as f:
			writer = csv.writer(f)
			writer.writerow(self.raw_headers)
			writer.writerow(self.raw_types)
			for row in self.raw_data:
				writer.writerow(row)
				
				
	
	
	
	#first deal with raw data 
	
	 
	'''
	return the list of all header 
	'''
	def get_raw_headers(self):
		return self.raw_headers
	
	'''
	return the list of all types 
	'''
	def get_raw_types(self):
		return self.raw_types
		
 
	
		
	'''
	return the number of rows in a data set
	'''
	def get_raw_num_rows(self):
		return len(self.raw_data)+2
		
	
	'''
	returns the number of columns in a data set
	'''
	def get_raw_num_columns(self):
		return len(self.raw_headers) 
	
	
		
	'''
	returns a row of data (the type is list) given a row index (int)
	'''
	def get_raw_row(self,index):
		
		if index<=self.get_raw_num_rows():
			if index==0:
				return self.raw_headers
			elif index==1:
				return self.raw_types 
			else:
				return self.raw_data[index-2]
 		else:
 			print(index, "is an invalid index") 
			return 
	
	
		
	
	'''
	takes a row index (an int) and column header (a string) 
	return the raw data in that location 	
	output is a string 
	'''
	def get_raw_value(self,index,header):
		
		if header not in self.raw_headers:
			print(header, "is not a valid header") 
			return
		
		row=self.get_raw_row(index) 
		column=self.header2raw[header]
		return row[column]
	
	'''
	takes a header and return the column
	'''
	def get_raw_col(self,header):
		
		col=[]
		for i in range(self.get_raw_num_rows()):
			col.append(self.get_raw_value(i,header))
		return col 
	
	
			
		
	'''
	takes a row index (an int) and column header(a string) and a value 
	set the raw data in that location 
	'''
	def set_raw_value(self,index,header,value):
		
		if header not in self.raw_headers:
			print(header,"is not a valid header")
			return 
		if index>len(self.raw_data):
			print(index,"is not a valid index")
			
		col=self.header2raw[header]
		self.raw_data[index][col]=value 
			
				
	
	
	
	
	'''
	print out all data raw by raw 
	'''	
	def printRaw(self): 	
		
		for i in range(self.get_raw_num_rows()):
			output=""
			for header in self.raw_headers:
				output+=" "
				output+=str(self.get_raw_value(i,header))
				
			print output
			
	

	#now deal with numeric form of data
	
	
	
	'''
	set fields headers,matrix_data,header2matrix
	'''
	def set_numeric(self):
		
		#first set headers and header2matrix 
		column=0
		for header in self.raw_headers:
			type=self.get_raw_value(1,header) 
			if type=="numeric":
				self.headers.append(header)
				self.header2matrix[header]=column
				column=column+1 
		

		#now set matrix_data
		listOfRows=[]
		for index in range(2,self.get_raw_num_rows()):
			row=[]
			for header in self.headers:
				row.append(self.get_raw_value(index,header))
			listOfRows.append(row)
		self.matrix_data=np.matrix(listOfRows)
		self.matrix_data=self.matrix_data.astype(np.float)	
	
		
		 
		
		
	
	'''
	return the list of headers of numeric columns 
	'''
	def get_headers(self):
		return self.headers
		
	
	'''
	given an index, return the corresponding row in the numeric index 
	'''
	def get_row(self,index):
		return self.matrix_data[index,:]
	
	
	
	
	'''
	return the number of columns of the numeric data 
	'''	
	def get_num_columns(self):
		return len(self.headers)
		
		
	'''
	given a list of indexes and headers, 
	return the corresponding matrix 
	indexes is the list of integers specifying rows
	'''
	def get_data(self,headers,indexes):
	
		listOfRows=[]
		for index in indexes:
			if index>self.get_raw_num_rows() or index<2:
				print index,"is an invalid index for numeric data"
				return 
			else:
				row=[]
				for header in headers:
					if header in self.headers:
						col=self.header2matrix[header]
						row.append(self.matrix_data[index-2,col])
			listOfRows.append(row) 
			
		
		
		matrix=np.matrix(listOfRows)
		matrix=matrix.astype(np.float)				
		return matrix 	
		
	
	'''
	gives headers and returns corresponding numeric columns  
	'''
	def get_columns(self,headers):
		
		rows=self.get_raw_num_rows()
		return self.get_data(headers,range(2,rows))
		
	
	
	
	#project 2 extensions 
	'''
	given a header, a type, and a correct number of points, 
	add a column of data to the Data object 
	update all fields correspondinly 
	'''
	def add_column(self,header,type,dat):	
		
		new=self.copy_data()
		
		#first check whether the number of points is correct 
		if len(dat)!=len(new.raw_data):
			print "the number of points should be", len(new.raw_data)
			return 
		
		#first modify the raw field 	
		new.raw_headers.append(header)
		new.raw_types.append(type)
		for i in range(0,len(new.raw_data)):
			new.raw_data[i].append(str(dat[i]))
		new.header2raw[header]=len(new.raw_headers)-1
			
			
		#now modify the numeric field 
		if type=="numeric":
			new.headers.append(header)
			new.header2matrix[header]=len(new.headers)-1
			
			col=[]
			for i in range(0,len(dat)):
				col.append([dat[i]])
			
			matrix_data=np.concatenate((new.matrix_data,col),axis=1)
			new.matrix_data=matrix_data
			
	
			
		return new 
		
		
	
	
	
	#now try to deal with multiple data formats 
	
	

	
	'''
	given a header of columns with enumerated data type, 
	convert all items in that column to numeric type 
	and updated self.enumerated dictionary 
	make a rule that the 2nd element of every enumerated column must be "enumerated" 
	'''
	def convert_enum_to_numeric(self,header): 
		
		#first check whether the data type is of enumerated 
		if self.get_raw_value(1,header)!="enumerated":
			print "the column with header", header,"is not of enumerated type"
			return 
			
		#generating a dictionary corresponding each item to a number 
		#converting the enumerated data to numbers
		dict={}
		index=0
		for i in range(len(self.raw_data)):
			item=self.get_raw_value(i+2,header)
			if item not in dict:
				index=index+1
				dict[item]=index
			self.set_raw_value(i,header,dict[item])
			
		self.enumerated[header]=dict
		
	
	'''
	return headers with columns of enumerated data type 
	'''
	def get_enum_headers(self):
		
		list=[]
		for header in self.raw_headers:
			if self.get_raw_value(1,header)=="enumerated":
				list.append(header)
		return list 
	
	
	
	
	
	
	
	'''
	given a header of columns with date data type, 
	convert all items in that column to numeric type  
	make a rule that the 2nd element of every date column must be "date" 
	allow three types of date formats 
	USA:mm/dd/yyyy;China:yyyy-mm-dd;Korea:yyyy.mm.dd
	'''
	def convert_dates_to_numeric(self,header):
	
		#first check whether the data type is of date 
		if self.get_raw_value(1,header)!="date":
			print "the column with header",header,"is not of date type" 
			return 
			
		for i in range(len(self.raw_data)):
			item=str(self.get_raw_value(i+2,header))
			
			
			#USA format
			if '/' in item: 
				time=item.split('/')
				date=datetime.date(int(time[2]),int(time[0]),int(time[1]))

			#China format 
			elif '-' in item:
				time=item.split('-')
				date=datetime.date(int(time[0]),int(time[1]),int(time[2]))
				
			#Korea format 
			elif '.' in item:
				time=item.split('.')
				date=datetime.date(int(time[0]),int(time[1]),int(time[2]))
				
			else:
				print "unknown format" 
				return 
				
			self.set_raw_value(i,header,date.toordinal())

	
	
	'''
	return headers of columns of date data type 
	'''
	def get_date_headers(self): 
		
		list=[]
		for header in self.raw_headers:
			if self.get_raw_value(1,header)=="date":
				list.append(header)
				
		return list 
		
		
		
		
		
	#methods designed for project 6 	
	'''
	return a copy of a data object 
	'''
	def copy_data(self):
		
		#raw data fields 
		new=Data()
		new.raw_headers=copy.deepcopy(self.raw_headers)
		new.raw_types=copy.deepcopy(self.raw_types)
		new.raw_data=copy.deepcopy(self.raw_data)
		new.header2raw=copy.deepcopy(self.header2raw)
		
		#numeric data fields 
		new.headers=copy.deepcopy(self.headers)
		new.matrix_data=self.matrix_data.copy()
		new.header2matrix=copy.deepcopy(self.header2matrix) 
		
		#enumerated data type 
		new.enumerated=copy.deepcopy(self.enumerated)
	
		return new 
		
	
	
	'''
	merge two data objects together to get a new one
	the merging operation is valid only if the two data objects has same lengh  
	'''	
	def merge(self,dat):
		new=self.copy_data()
		headers=dat.headers 
		if self.get_raw_num_rows()!=dat.get_raw_num_rows():
			print "dimension not match!"
			return 
		for header in headers:
			column=dat.get_raw_col(header)
			type=column[1]
			items=column[2:]
			new=new.add_column(header,type,items)
			
		return new 
		
		
	'''
	add numeric column, which is a n*1 matrix 
	'''
	def add_numeric_column(self,header,column):
		
		list=[]
		for i in range(column.shape[0]):
			list.append(column[i,0])
		
		return self.add_column(header,"numeric",list)
		
		
			
	
	
	
'''
a handy helper method
given a list of strings, return a list whose elements are stripped of blank space 
'''
def strip(list):
	newList=[]
	for word in list:
		newWord=word.strip()
		newList.append(newWord)
			
	return newList		
	
	

if __name__=="__main__":
	data=Data("AustraliaCoast.csv")
	data.write("output.csv")
	
