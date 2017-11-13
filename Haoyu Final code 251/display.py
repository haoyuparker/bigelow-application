# Skeleton Tk interface example
# Written by Bruce Maxwell
# Modified by Stephanie Taylor
# Modified by Haoyu Song
# CS 251
# Spring 2017 

import Tkinter as tk
import tkFont as tkf
import math
import random
import copy
import tkMessageBox 
import tkFileDialog 
import os 
import view as vi
import numpy as np
import sys
import data 
import analysis as an
from dialog import Dialog 



'''
create a class to build and manage the display
'''
class DisplayApp:

    def __init__(self, width, height):

        # create a tk object, which is the root window
        self.root = tk.Tk()

        # width and height of the window
        self.initDx = width
        self.initDy = height

        # set up the geometry for the window
        self.root.geometry( "%dx%d+50+30" % (self.initDx, self.initDy) )

        # set the title of the window
        self.root.title("Haoyu Song's data display")

        # set the maximum size of the window for resizing
        self.root.maxsize( 1600, 900 )

        # setup the menus
        self.buildMenus()

        # build the controls
        self.buildControls()

        # build the Canvas
        self.buildCanvas()

        # bring the window to the front
        self.root.lift()

        # - do idle events here to get actual canvas size
        self.root.update_idletasks()

        # now we can ask the size of the canvas
        print self.canvas.winfo_geometry()

        # set up the key bindings
        self.setBindings()

        # set up the application state
        self.filename=None #selected file to analyze 
        self.objects = [] # list of data objects that will be drawn in the canvas
        self.data = None # holding a Data object obtained from file 
        self.data_inuse=None #holding the data object that is currently being plot 
        self.baseClick1=None
        self.baseClick2=None
        self.baseClick3=None
        self.size=5 #default size for data objects 
    
        self.yDistribution=(0,)
        
        
        #view object used to do transformations 
        self.view=vi.View()
        
        #analysis object used to apply data analysis 
        self.analysis=an.Analysis()
       
        #fields storing user's selection of which data to plot 
        self.axes_headers=[None,None,None] # a list of headers specifying x,y,z axes 
        self.size_header=None  #specifying size information 
        self.color_header=None #specifying color information 
        self.shape_header=None #specifying shape information 
        
        #matrix storing the endpoints of x,y,z axis 
       	self.axesPts=np.matrix([[0,0,0,1], [1,0,0,1], [0,0,0,1], [0,1,0,1], [0,0,0,1], [0,0,1,1]])
        self.axes=[]#graphic object for the axes 
        self.labels=[]#label object for the axes 
        self.labelTexts=["X","Y","Z"] 
        
        
        #holding the base information of the canvas 
    	self.base_width=self.canvas.winfo_width()
    	self.base_height=self.canvas.winfo_height()
    	self.base_screen=copy.deepcopy(self.view.screen)
        
        
        #holding the information about linear regression 
        self.ind1=None #independent variables
        self.ind2=None 
        self.dep=None #dependent variables
        self.reg=[]  #regression line objects 
        self.reg_label=None
        self.reg_points=None #matrix storing the end points of the regression line
        self.reg_stats=[]#statistic info about regression  
        
        
        #holding information about PCA analysis 
        self.pca_map={}  #map user's selected PCA name to the corresponding PCA object 
         
        #holding information about clusters 
        self.cluster_map={} #map user's selected name to the corresponding cluster object
        self.clustered=False #indicating whether to plot cluster 
        
        
        
        
        # a list of 15 preselected colors; this is why I limit the number of clusters to 15 
    	self.colors=["red","yellow","green","blue","black","brown","pink","purple",
    		"dark turquoise","rosy brown","wheat","thistle","ivory","dim gray","gold" ]
        
        #set up the axes 
        self.build_axes()
        
        
  
  	'''
  	create the x,y,z axes for display 
  	'''
    def build_axes(self):
    	
    	vtm=self.view.build()
    	pts=(vtm*self.axesPts.T).T #axis endpoints as the row again 
    	
    	
    	#x axis 
    	self.axes.append(self.canvas.create_line(pts[0,0],pts[0,1],pts[1,0],pts[1,1]))
    	self.labels.append(self.canvas.create_text(pts[1,0],pts[1,1],font="Arial",text="X",
    						anchor=tk.SW))
    	
    	#y axis 
    	self.axes.append(self.canvas.create_line(pts[2,0],pts[2,1],pts[3,0],pts[3,1]))
    	self.labels.append(self.canvas.create_text(pts[3,0],pts[3,1],font="Arial",text="Y",
    						anchor=tk.S))
    	
    	#z axis 
    	self.axes.append(self.canvas.create_line(pts[4,0],pts[4,1],pts[5,0],pts[5,1]))
    	self.labels.append(self.canvas.create_text(pts[5,0],pts[5,1],font="Arial",text="Z",
    						anchor=tk.NE))
    	
    	self.axesPoints=pts 
    
    	
    '''
    update the axes and all graphic objects based on a new VTM 
    '''
    def update_axes(self):
    
    	vtm=self.view.build()
    	pts=(vtm*self.axesPts.T).T 
    	
    	
    	#update axes and corresponding labels 
    	for i in range(3):
    		#here 1 corresponds to x-axis, 2 corresponds to y-axis, 3 to z 
    		self.canvas.coords(self.axes[i],pts[2*i,0],pts[2*i,1],pts[2*i+1,0],pts[2*i+1,1]) 
    		self.canvas.coords(self.labels[i],pts[2*i+1,0],pts[2*i+1,1])
    		#this enables the x,y,z labels to move alongside 
    		
    	
    '''
    update labels according to self.labelTexts 
    '''	
    def update_labels(self):
    	for i in range(3):
    		self.canvas.itemconfig(self.labels[i],text=self.labelTexts[i]) 
    
    
    def buildMenus(self):
        
        # create a new menu
        menu = tk.Menu(self.root)

        # set the root menu to our new menu
        self.root.config(menu = menu)

        # create a variable to hold the individual menus
        menulist = []

        # create a file menu
        filemenu = tk.Menu( menu )
        menu.add_cascade( label = "File", menu = filemenu )
        menulist.append(filemenu)

        # create another menu for kicks
        cmdmenu = tk.Menu( menu )
        menu.add_cascade( label = "Command", menu = cmdmenu )
        menulist.append(cmdmenu)

        # menu text for the elements
        # the first sublist is the set of items for the file menu
        # the second sublist is the set of items for the option menu
        menutext = [ [ '-', '-', 'Open  \xE2\x8C\x98-O', '-', '-', 'Clear  \xE2\x8C\x98-N' ,'-','-','Quit  \xE2\x8C\x98-Q'],
                     [ 'Linear Regression', '-', '-' ,'PCA', '-', '-','Clustering','-', '-'] ]

        # menu callback functions (note that some are left blank,
        # so that you can add functions there if you want).
        # the first sublist is the set of callback functions for the file menu
        # the second sublist is the set of callback functions for the option menu
        menucmd = [ [None, None, self.handleOpen,None, None, self.clearData,None, None, self.handleQuit],
                    [self.handleLinearRegression, None, None,self.handlePCA,None,None,
                    self.handleCluster,None, None] ]
        
        # build the menu elements and callbacks
        for i in range( len( menulist ) ):
            for j in range( len( menutext[i]) ):
                if menutext[i][j] != '-':
                    menulist[i].add_command( label = menutext[i][j], command=menucmd[i][j] )
                else:
                    menulist[i].add_separator()
        
        
        
	'''
    create the canvas object
    '''
    def buildCanvas(self):
        self.canvas = tk.Canvas( self.root, width=self.initDx, height=self.initDy )
        self.canvas.pack( expand=tk.YES, fill=tk.BOTH )
        return

    
    
    '''
    build a frame and put controls in it
    also put all relevant information there 
    '''
    def buildControls(self):
        
            
        # right frame 
        rightframe = tk.Frame(self.root)
       	rightframe.pack(side=tk.RIGHT, padx=5, pady=5, fill=tk.Y)
    	
    	#make a separater frame 
    	sep=tk.Frame(self.root, height=self.initDy, width=2,bd=1,relief=tk.SUNKEN)
    	sep.pack(side=tk.RIGHT,padx=2,pady=2,fill=tk.Y)
    	
    	label=tk.Label(rightframe,text="Control Panel",width=20)
    	label.pack(side=tk.TOP,pady=10)
    	
    	#a menu for color options 
    	label=tk.Label(rightframe,text="Set Color")
    	label.pack(side=tk.TOP,pady=10)
    	self.colorOption=tk.StringVar(self.root)
    	self.colorOption.set("green")
    	colorMenu=tk.OptionMenu(rightframe,self.colorOption,"red","black","green","purple")
    	colorMenu.pack(side=tk.TOP)
    	
    	
    	#make a button that handles the process of plotting data 
    	button1=tk.Button(rightframe,text="plot data",command=self.handlePlot)
    	button1.pack(side=tk.TOP)
    	
    	#show stats 
    	button2=tk.Button(rightframe,text="show stats",command=self.handleShowStats)
    	button2.pack(side=tk.TOP)
    	
    	
    	
    	#handles saving linear regression info  
    	button4=tk.Button(rightframe,text="save regression",command=self.handleSaveRegression)
    	button4.pack(side=tk.TOP)
    	
    	#handles saving analysis 
    	button5=tk.Button(rightframe,text="save PCA",command=self.handleSavePCA)
    	button5.pack(side=tk.TOP)
    	
    	
    	#display PCA info 
    	button6=tk.Button(rightframe,text="PCA info",command=self.show_pca_data)
    	button6.pack(side=tk.TOP)
    	
    	#plot PCA
    	button7=tk.Button(rightframe,text="PCA plot",command=self.plotPCA)
    	button7.pack(side=tk.TOP)
    	
    	#delete PCA analysis 
    	button8=tk.Button(rightframe,text="delete PCA" ,command=self.delete_pca)
    	button8.pack(side=tk.TOP)
    	
    	#display cluster info 
    	button9=tk.Button(rightframe,text="Cluster info",command=self.show_cluster_data)
    	button9.pack(side=tk.TOP)
    	
    	#show analysis of selected columns
    	button9=tk.Button(rightframe,text="Show Stats",command=self.handleShowStats)
    	button9.pack(side=tk.TOP)
    	
    	
    	#make an entry box for the translation speed 
    	#input must be between 0 and 5 
    	label=tk.Label(rightframe,text="translation speed")
    	label.pack(side=tk.TOP,pady=10)
    	self.tran_speed=tk.Entry(rightframe,width=15)
    	self.tran_speed.pack(side=tk.TOP)
    	self.tran_speed.insert(0,1)
    	
    	#rotation speed 
    	#input must be between 0 and 5 
    	label=tk.Label(rightframe,text="rotation speed")
    	label.pack(side=tk.TOP,pady=10)
    	self.rot_speed=tk.Entry(rightframe,width=15)
    	self.rot_speed.pack(side=tk.TOP)
    	self.rot_speed.insert(0,1) 
    	
    	
    	
    	#scaling speed 
    	#input must be between 0 and 5 
    	label=tk.Label(rightframe,text="scaling speed")
    	label.pack(side=tk.TOP,pady=10)
    	self.s_speed=tk.Entry(rightframe,width=15)
    	self.s_speed.pack(side=tk.TOP)
    	self.s_speed.insert(0,1)
    	
    
    	#bottom frame
    	#displaying the location 
    	bottomframe=tk.Frame(self.root)
    	bottomframe.pack(side=tk.BOTTOM,padx=3,pady=3,fill=tk.Y)
    	
        self.raw_data=tk.StringVar(self.root)
        raw_data=tk.Label(bottomframe,textvariable=self.raw_data,width=60)
        raw_data.pack(side=tk.BOTTOM,pady=10)
        
        self.location = tk.StringVar( self.root )
        location = tk.Label( bottomframe, textvariable=self.location, width=20 )
        location.pack( side=tk.BOTTOM, pady=10)
        
      
        return

   
   
    def setBindings(self):
        # bind mouse motions to the canvas
        self.canvas.bind( '<Button-1>', self.handleMouseButton1 )
        self.canvas.bind( '<Control-Button-1>', self.handleMouseButton2 )
        self.canvas.bind( '<Button-2>', self.handleMouseButton2 )
        self.canvas.bind( '<Control-Command-Button-1>', self.handleMouseButton3 )
        self.canvas.bind( '<B1-Motion>', self.handleMouseButton1Motion )
        self.canvas.bind( '<B2-Motion>', self.handleMouseButton2Motion )
        self.canvas.bind( '<Control-B1-Motion>', self.handleMouseButton2Motion )
        self.canvas.bind( '<Control-Command-B1-Motion>', self.handleMouseButton3Motion)
        self.canvas.bind( '<Motion>', self.getData )

        # bind command sequences to the root window
        self.root.bind( '<Command-q>', self.handleQuit )
        self.root.bind( '<Command-n>', self.clearData)
        
        #adjust the view frame 
        self.root.bind('<Command-x>',self.viewXZ)#view xy-data 
        self.root.bind('<Command-y>',self.viewYZ)#view yz-data

        
        #add the reset functionality 
        self.root.bind('<Command-r>',self.handleReset)
        
        #handle files 
        self.root.bind('<Command-o>',self.handleOpen)
        
        #handle resizing 
        self.canvas.bind('<Configure>',self.handleResize)
        

   	'''
	update the location of all objects in the object list 
	'''
    def handleMouseButton1(self, event):
        print 'handle mouse button 1: %d %d' % (event.x, event.y)
        self.baseClick1 = (event.x, event.y)
        
        	
        	
        
        
    '''   
	when right clicked, add a new point at the clicked location 
	'''
    def handleMouseButton2(self, event):
        
        self.baseClick2 = (event.x, event.y)
        print 'handle mouse button 2:%d %d'%(event.x,event.y)
        self.baseView=self.view.clone()
    
    
    
    
    def handleMouseButton3(self, event):
    	
    	self.baseClick3=(event.x,event.y)
    	self.baseSize=self.size
    	print 'handle mouse button 3: %d %d' % (event.x, event.y)
    	self.baseView=self.view.clone()
    
    
    
    
    '''
    This is called if the first mouse button is being moved
    vrp is moved according to the mouse motion 
    '''
    def handleMouseButton1Motion(self, event):
    	
    	try:
    		speed=float(self.tran_speed.get())
    	except ValueError:
    		tkMessageBox.showwarning("Attention", "please input a number between 0 and 5") 
    		return
    	
    	if speed>5 or speed<0:
    		tkMessageBox.showwarning("Attention", "please input a number between 0 and 5") 
    		return 
       
       	#convert distance in pixels to distance in the view volume 
        dx = event.x - self.baseClick1[0]
        dy = event.y - self.baseClick1[1] 
        delta0=speed*dx*self.view.extent[0,0]/self.view.screen[0]
        delta1=speed*dy*self.view.extent[0,1]/self.view.screen[1]
        
    	u=np.matrix(self.view.u)
    	vup=np.matrix(self.view.vup)
      	self.view.vrp=self.view.vrp+multiply(delta0,u)+multiply(delta1,vup)
      	self.update_axes()
      	self.updatePoints()
      	self.updateFits()
      	
      	
      	#do not forget to update the base Click 
      	self.baseClick1=(event.x,event.y)

            
   
   	'''
    This is called if the second button of a real mouse has been pressed
    and the mouse is moving. Or if the control key is held down while
    a person moves their finger on the track pad.
    rotate according to the movement of mouse
    horizontal movement controls rotation about x-axis, vertical controls rotation about y-axis 
    '''
    def handleMouseButton2Motion(self, event):
    
    	try:
       		speed=float(self.rot_speed.get())
       	except ValueError:
       		tkMessageBox.showwarning("Attention","please input a number between 0 and 5")
       		return 
       		
       	if speed>5 or speed<0:
       		tkMessageBox.showwarning("Attention","please input a number between 0 and 5") 
       		
        
        
    	#convert pixel to radian 
    	dx=self.baseClick2[0]-event.x
    	dy=self.baseClick2[1]-event.y
    	delta0=speed*math.pi*(float(dx)/200)
    	delta1=speed*math.pi*(float(dy)/200)
    	
    	self.view=self.baseView.clone()
    	self.view.rotateVRC(delta0,-delta1)
    	self.update_axes()
    	self.updatePoints()
    	self.updateFits()
    	

    '''
    this is called if control and command are clicked when the mouse is moving 
    scaling according to the movement of the mouse 
    moving upward:zoom in      moving downward:zoom out 
    '''
    def handleMouseButton3Motion(self,event):
    
    	try:
       		speed=float(self.s_speed.get())
       	except ValueError:
       		tkMessageBox.showwarning("Attention","please input a number between 0 and 5")
       		return 
       		
       	if speed>5 or speed<0:
       		tkMessageBox.showwarning("Attention","please input a number between 0 and 5") 
    	
    
    	
    	dy = self.baseClick3[1]-event.y
    	
    	#convert pixel to factor 
    	#make sure the factor is in (1,3)
    	factor=speed*max(0.1,min(3,1+0.01*dy))
    	self.size=self.baseSize/factor 
    	self.view.extent=multiply(factor,self.baseView.extent)
    	self.update_axes()
    	self.updatePoints()
    	self.updateFits()
    	
    	

    '''	
    get the location of the mouse and return the dimensions of the underlying data object 
    '''	
    def getData(self,event):
    	
    	self.location.set ("location: "+str(event.x) + ", " + str(event.y))   	
    	
    	length=len(self.objects)
    	if length==0:
    		return 
    	
    	for index in range(length):
    		
    		info=""
    		
    		obj=self.objects[index]
    		center_x=(self.canvas.coords(obj)[0]+self.canvas.coords(obj)[2])/2.0
    		center_y=(self.canvas.coords(obj)[1]+self.canvas.coords(obj)[3])/2.0
    		
    		if abs(float(center_x-event.x))<15 and abs(float(center_y-event.y))<15: # if the click is close enough to an object
    		 	headers=self.axes_headers+[self.size_header,self.shape_header]
    		 	for header in headers:
    		 		if header!=None and header in self.data_inuse.get_headers(): 
    		 			string=header+":"+self.data_inuse.get_raw_value(index,header)+" " 
    		 			info+=string 
    		 	
    		 			
    			self.raw_data.set(info)
    			

    
    def handleQuit(self, event=None):
        print 'Terminating'
        self.root.destroy()
	
   	
   
    
    '''
   	enable user to select independent variable and dependent variable(s) to fit,
   	clear all previous data and regression objects 
    '''
    def handleLinearRegression(self,event=None):
    	 
    	 #check whether the user has opened a valid file 
    	 if self.filename==None:
    	 	tkMessageBox.showwarning( "ATTENTION","please open a valid file FIRST")
    	 	return 
    	 
    	 
    	 #call user attention when their selection is invalid 
    	 dialog=regression_dialog(self.root,self.data_inuse.get_headers())
    	 
    	 if count(dialog.result)==0:
    	 	return 
    	 	
    	 if dialog.result[0]==None:
    	 	tkMessageBox.showwarning("ATTENTION","please choose X-independent variable First") 
    	 	return 
    	 
    	 if dialog.result[2]==None:
    	 	tkMessageBox.showwarning("ATTENTION", "please choose a dependent variable") 
    	 	return 
    	 
    	 
    	 #first completely clear previous objects 
    	 self.completeReset()
    	 
    	 #set dependent variable and independent variable(s) based on the user's selection 
    	 headers=self.data_inuse.get_headers()
    	 self.ind1=headers[dialog.result[0]]
    	 if dialog.result[1]!=None:
    	 	self.ind2=headers[dialog.result[1]]
    	 else:
    	 	self.ind2=None
    	 self.dep=headers[dialog.result[2]]
    	 
    	 self.axes_headers=[self.ind1,self.dep,self.ind2]
    	 self.labelTexts=["X","Y","Z"]
    	 for i in range(3):
    	 	if self.axes_headers[i]!=None:
    	 		self.labelTexts[i]+=":"+self.axes_headers[i]
    		
    	 

    	 #build linear regression and points 
    	 if self.ind2==None:
    	 	self.reg_stats=self.analysis.linear_regression(self.data_inuse,[self.ind1],self.dep)
    	 	
    	 	self.buildLinearRegression()
    	 else:
    	 	self.reg_stats=self.analysis.linear_regression(self.data_inuse,[self.ind1,self.ind2],
    	 			self.dep)
    	 	
    	 	self.buildMultipleRegression()
    	 
    	 self.buildPoints()
    	 self.update_labels()
    	
    
    
    
    
    
    '''
    build a regression line object based on selected dependent variable
    and independent variable(s)
    '''
    def buildLinearRegression(self):
    	
    	#get coefficients
    	m,b=self.reg_stats[0]
    	r2=self.reg_stats[2]
    		
    		
    	#calculating endpoints and create a line object 
    		
    	#normalization 
    	xmax,xmin=self.analysis.data_range([self.ind1],self.data_inuse)[0]
    	ymax,ymin=self.analysis.data_range([self.dep],self.data_inuse)[0]
    	x0=0
    	y0=((xmin*m+b)-ymin)/(ymax-ymin)
    	x1=1
    	y1=((xmax*m+b)-ymin)/(ymax-ymin)
    		
    	#matrix manipulation 
    	vtm=self.view.build()
    	matrix=np.matrix([[x0,y0],[x1,y1]])
    	self.reg_points=np.hstack((matrix,np.zeros((2,1)),np.ones((2,1))))
    	pts=(vtm*self.reg_points.T).T
    		
    	#draw line 
    	self.reg.append(self.canvas.create_line(pts[0,0],pts[0,1],pts[1,0],pts[1,1],
    						fill="blue"))
    	
    	#label 
    	text=""
    	equation="  y="+str(round(m,3))+"x"+"+"+str(round(b,3))+"\n"
    	text=text+equation+" r2="+str(round(r2,3))+"\n" 
    	
    	self.reg_label=self.canvas.create_text(pts[1,0],pts[1,1],font="Arial",
    		text=text,anchor=tk.SW)
    		
    	
    	
    '''
    build multiple linear regression
    '''
    def buildMultipleRegression(self):
    		
    	#get coefficients 
    	m1,m2,b=self.reg_stats[0]
    	r2=self.reg_stats[2] 
    
    		
    	#calculating endpoints and then create a plane i.e four lines 
    		
    	#normalization 
    	xmax,xmin=self.analysis.data_range([self.ind1],self.data_inuse)[0]
    	zmax,zmin=self.analysis.data_range([self.ind2],self.data_inuse)[0]
    	ymax,ymin=self.analysis.data_range([self.dep],self.data_inuse)[0]
    	#now calculate points 
    	#x1,x3 are selected to make the plot looks prettier 
    	x0,y0,z0=0,(xmin*m1+zmin*m2+b-ymin)/(ymax-ymin),0
    	x1,y1,z1=0.5,(0.5*(xmax+xmin)*m1+zmin*m2+b-ymin)/(ymax-ymin),0
    	x2,y2,z2=1,(xmax*m1+zmax*m2+b-ymin)/(ymax-ymin),1
    	dx,dy,dz=x1-x0,y1-y0,z1-z0
    	x3,y3,z3=x2-dx,y2-dy,z2-dz
    	
    			
    		
    		
    	#matrix manipulation 
    	vtm=self.view.build()
    	matrix=np.matrix([[x0,y0,z0],[x1,y1,z1],[x2,y2,z2],[x3,y3,z3],[x0,y0,z0]])
    	self.reg_points=np.hstack((matrix,np.ones((5,1))))
    	pts=(vtm*self.reg_points.T).T
    	
    	

    	#draw four lines 
    	for i in range(4): 
    		self.reg.append(self.canvas.create_line(pts[i,0],pts[i,1],pts[i+1,0],pts[i+1,1],fill="blue"))

    		
    	#create texts
    	text=""
    	equation="    y="+str(round(m1,3))+"x+"+str(round(m2,3))+"z+"+str(round(b,3))+"\n"
    	text=text+equation+"     r2="+str(round(r2,3))+"\n" 
    	
		
    	 
    	self.reg_label=self.canvas.create_text(pts[2,0],pts[2,1],font="Arial",
    						text=text,anchor=tk.NW)
    		 
    	 
    
    
    '''
	update the regression line/plane and label according to vtm
    '''	 
    def updateFits(self):

		if len(self.reg)==0:#not in handle linear mode
			return 
		
		vtm=self.view.build()
		pts=(vtm*self.reg_points.T).T 
			
		if len(self.reg)==1:#single linear regression
			self.canvas.coords(self.reg[0],pts[0,0],pts[0,1],pts[1,0],pts[1,1])
			self.canvas.coords(self.reg_label,pts[1,0],pts[1,1])
			
		else: #multiple linear regression 
			for i in range(4):
				self.canvas.coords(self.reg[i],pts[i,0],pts[i,1],pts[i+1,0],pts[i+1,1])
				self.canvas.coords(self.reg_label,pts[2,0],pts[2,1])
			
    
    
    
    
    
        		
    		
    	
    '''
	clear all objects from the canvas 
	'''
    def clearData(self,event=None):
    	
    	for obj in self.objects:
            self.canvas.delete( obj )
        for reg in self.reg:
        	self.canvas.delete(reg)
        self.canvas.delete(self.reg_label)
        
        self.objects = []
        self.reg=[]
        self.reg_label=None
																	
    
    
    ''' 
    reset to the original view xy
    '''
    def handleReset(self,event=None):
    	self.view=vi.View()
    	self.update_axes()
    	self.updatePoints()
    
    
    
    '''
    return to the beginning situation: no data points, xy-view
    '''
    def completeReset(self,event=None):
    	self.clearData()
    	#default view 
    	self.view=vi.View()
    	self.update_axes()
    	
    	
    
    '''
    create data object from selected file 
    '''
    def handleOpen(self,event=None):
    	fn=tkFileDialog.askopenfilename(parent=self.root, title='choose a data file',
    	initialdir='.')
    	self.filename=os.path.basename(fn)
    	if fn:
    		 self.data=data.Data(fn)
    		 self.data_inuse=self.data.copy_data()
    		 self.pca_map={}
    		 self.cluster_map={}
    	else:
    		tkMessageBox.showwarning( "ATTENTION","please open a valid file")
    		return 
    	
    	
    
    
    '''
    handle the process of plotting data 
    '''
    def handlePlot(self,event=None):
    	
    	#check whether the user has already opened a VALID file 
    	if self.data==None: 
    		tkMessageBox.showwarning( "ATTENTION","please open a valid file FIRST")
    		return 
    		
    	self.data_inuse=self.data.copy_data()
    	self.color_header=None 
    	self.size_header=None 
    	self.shape_header=None
    	self.clustered=False 
    	self.colorScheme="smooth"
    	
    	#now allow the user to choose whether to plot using eigens 
    	keys=self.pca_map.keys()
    	if len(keys)!=0:
    		sg=single_Dialog(self.root,keys,"Append a PCA analysis?")
    		result=sg.result
    		if len(result)!=0:
    			if result[0]!=None:
    				key=keys[result[0]]
    				self.data_inuse=self.data.merge(self.pca_map[key])
    
    		
    	
    	#now allow the user to select whether to plot using clustering 
    	keys=self.cluster_map.keys()
    	if len(keys)!=0:
    		c_dialog=cluster_plot_dialog(self.root,keys)
    		result1=c_dialog.result #cluster selection
    		result2=c_dialog.scheme #scheme selection 
    		if len(result1)==0 and len(result2)==0:#no selection or cancelled 
    			pass 
    		elif len(result1)==0:
    			tkMessageBox.showwarning( "ATTENTION","please choose a cluster analysis")
    			return 
    		elif len(result2)==0:
    			tkMessageBox.showwarning("Attention","please choose a color scheme")
    			return 
    		else:
    			self.clustered=True
    			key=self.cluster_map.keys()[result1[0]]
    			cluster=self.cluster_map[key]
    			clusterID=cluster.clusterIDs
    			self.colorScheme=["pre-selected","smooth"][result2[0]] 
    			self.data_inuse=self.data_inuse.add_numeric_column("cluster_"+key,clusterID)
    			self.color_header="cluster_"+key
    	    		
    	
    	
    	self.handleChooseAxes(self.data_inuse) 
    	self.buildPoints()
    	self.update_labels()
    	
    	
   
    	
    '''
    saves an regression analysis 
    '''
    def handleSaveRegression(self,event=None):
    	
    	if len(self.reg_stats)==0:
    		tkMessageBox.showwarning("ATTENTION","please do a linear regression First")
    		return 
    	 
    	#regression stats in a readable format
    	string=""
    	string+="the file to analyze is "+self.filename+"\n"
    	string+= "the dependent variable is "+self.dep+"\n"
    	string+= "the independent varialblels are "+self.ind1
    	if self.ind2!=None:
    	 	string+=" "+self.ind2
    	string+="\n"
    	string+="the best fit linear coefficients are "
    	string=concat_list(string,roundL(self.reg_stats[0]))
    	string+= "the sum squared error is "
    	string=concat_list(string,roundL(self.reg_stats[1]))
    	string+= "the R^2 coefficient is "
    	string+=str(round(self.reg_stats[2],3))
    	string+="the t_statistic is "
    	string=concat_list(string,roundL(self.reg_stats[3]))
    	string+="probability of coefficients indicating random relationship "
    	string=concat_list(string,roundL(self.reg_stats[4]))
		
		#give the user a chance to select analysis filename 
    	name=fileEntry(self.root).result
    	if len(name)==0:
    		tkMessageBox.showwarning("ATTENTION","please input a file name FIRST")
    		return 
    		
    	filename=name[0]+".txt"
    	
    	f=open(filename,'w')
    	f.write(string)
    	f.close()
    	
    	
    
    '''
    create a dialog box which enables the user to set spatial axes, color and size 
    '''
    def handleChooseAxes(self,dat,event=None):
    	
    	dialog=Axes_dialog(self.root,dat,self.clustered)
    	self.axes_headers=[None,None,None]
    	self.labelTexts=["X","Y","Z"] 
    	
    	
    	#completely clear previous data 
    	if count(dialog.result)==0:
    		return 
    	elif dialog.result[0]!=None and dialog.result[1]!=None:
    		self.completeReset()	
    	else:
    		tkMessageBox.showwarning("Attention", "please choose X,Y axes first")
    		return 
    		
    		
    	#set visual dimensions 
    	for i in range(len(dialog.result)):
    		
    		index=dialog.result[i]
    		
    		#set spatial axes 
    		if i>=0 and i<=2:
    			if index!=None:
    				self.axes_headers[i]=dat.headers[index]
    				#give labels to axes 
    				self.labelTexts[i]=self.labelTexts[i]+":"+dat.headers[index]
    			
    			
    		#set size
    		elif i==3:
    			if index!=None:
    				self.size_header=dat.headers[index]
    	
    		#set shape 
    		elif i==4:
    			if index!=None:
    				self.shape_header=dat.headers[index] 
    		
    		#set color
    		else:
    			if index!=None:
    				self.color_header=dat.headers[index]
    				
    		
    		self.update_labels()
    		
		
    		
    	
    	
    '''	
    create data objects based on the spatial axes, size, and color selected by the user
    updated in project 6 to take a data object as parameter  
    '''
    def buildPoints(self):
    	
    	vtm=self.view.build()
    	
    	
    	selection=count(self.axes_headers) #keeping track of how many columns are selected as axes 
    	if selection!=0:
    		self.normalized=self.analysis.normalize_columns_separately(self.axes_headers,self.data_inuse)
    		
    		
    	
    	row_num=self.data_inuse.get_raw_num_rows()-2 #number of rows i.e data points
    	ones=np.ones((row_num,1))
    	zeros=np.zeros((row_num,1))
    	
    	
    	#divide into cases based on how many columns are selected as axes 
    	
    	if selection==0:
    		return 
    		
    	elif selection==1: #create a histogram 
    		
    		x=self.view.offset[0]
    		dx=self.view.screen[0]/row_num/2 
    		matrix=np.zeros((row_num,4))
    		
    		for i in range(row_num):
    			y=self.normalized[i,0]
    			matrix[i,:]=[x/self.view.screen[0],y,0,1]
    			x+=dx+10
    		
    		
    		points=(vtm*matrix.T).T #each row holds the width and height of each column
    		for i in range(row_num):
    			x=points[i,0]
    			y=points[i,1]
    			base = (vtm*np.matrix([0,0,0,1]).T).T[0,1]
    			rt = self.canvas.create_rectangle( x-dx, y, x+dx, base,fill="purple", outline='' )
    			self.objects.append(rt)
				

    		return
    
    
    	elif selection==2: #only x,y axes are selected 
    		self.normalized=np.hstack((self.normalized,zeros,ones))
    			
    	
    	
    	#x,y,z axes are selected 
    	else: # add a column of homogenous column 
    		self.normalized=np.hstack((self.normalized,ones))
    	
    		 	
    	#now adjust color,size,and shape according to the dialog box results 
    	if self.color_header!=None:
    		if self.colorScheme=="smooth":
    			self.color_col=self.analysis.normalize_columns_separately([self.color_header],self.data_inuse)
    		else:
    			self.color_col=self.data_inuse.get_columns([self.color_header])
    		
    	
    	if self.size_header!=None:
    		self.size_col=self.analysis.normalize_columns_separately([self.size_header],self.data_inuse)
    		
    	if self.shape_header!=None:
    		self.shape_col=self.analysis.normalize_columns_separately([self.shape_header],self.data_inuse)
    		
    	
    	points=(vtm*self.normalized.T).T
    	
    	
    	
    	
    	#draw data points 
    	for i in range(len(points)):
    		
    		x=points[i,0]
    		y=points[i,1]
    		
    		#the color depends on the value of the selected color column
    		color=self.colorOption.get()
    		if self.color_header!=None:
    			if self.colorScheme=="smooth":
    				color = "#%02x%02x%02x" % (255*0.5*self.color_col[i,0], 255*0.2*self.color_col[i,0],255*(1-self.color_col[i,0]))
    			else:
    				index=int(self.color_col[i,0])
    				color=self.colors[index]
    		
    		#the size depends on the value of the selected size colum 
    		size=self.size
    		if self.size_header!=None:
    			size=self.size_col[i,0]*4+3
    			
    		
    		#the shape of the data object depends on the value of the selected shape column 
    		if self.shape_header==None:
    			point=self.canvas.create_oval(x,y,x+2*size,y+2*size,fill=color,outline='')
    		
    		else:
    		
    			shape_option=self.shape_col[i,0] 
    			
    			if shape_option<0.25:
    				point=self.canvas.create_oval(x,y,x+2*size,y+2*size,fill=color,outline='')
    				
    			elif shape_option<0.5: 
    				point=self.canvas.create_rectangle(x,y,x+2*size,y+2*size,fill=color,outline='')
    			
    			elif shape_option<0.75:
    				point=self.canvas.create_polygon(x,y,x+2*size,y,x+size,y+size,fill=color,outline='')
    			
    			else: 
    				point=self.canvas.create_arc(x,y,x+2*size,y+2*size,fill=color,outline='')
    				
    				
    		self.objects.append(point) 
    		
    		
    	 
    		
    		
		 
				
		
		
    
    '''
    update all points based on the new VTM 	
    '''
    def updatePoints(self):
    	
    	if len(self.objects)==0:
    		return 
    		
    	if count(self.axes_headers)==1: #only one spatial axis is selected 
    		tkMessageBox.showwarning("Attention", "cannot move historgram")
    		return 
    	
    	vtm=self.view.build()
    	points=(vtm*self.normalized.T).T
    	for i in range(len(points)):
    		obj=self.objects[i]
    		x=points[i,0]
    		y=points[i,1]
    		
    		
    		size=self.size
    		if self.size_header!=None:
    			size=self.size_col[i,0]*4+3
    		self.canvas.coords(obj, x,y, x+2*size, y+2*size)
    	
    
    
    
    '''
    handling the process of showing statistical information of a selected column 
    if the user makes a valid selection, show the corresponding mean, standard deviation etc 
    '''
    def handleShowStats(self):
    	
    	if self.data==None:
    		tkMessageBox.showwarning("Attention","please select a file FIRST")
    		return 
    	
    	headers=self.data_inuse.get_headers()
    	if len(headers)==0:
    		tkMessageBox.showwarning("Attention", "NO numeric data")
    		return 
    	else:
    		dialog=single_Dialog(self.root,headers,"Stats")
    		if len(dialog.result)==0: #the user does not make any selection
    			return 
    		elif dialog.result[0]==None:#same
    			return 
    		else: #a valid selection 
    			header=headers[dialog.result[0]]
    			max=self.analysis.data_range([header],self.data_inuse)[0][0]
    			min=self.analysis.data_range([header],self.data_inuse)[0][1]
    			mean=self.analysis.mean([header],self.data_inuse)[0,0]
    			stdev=self.analysis.stdev([header],self.data_inuse)[0,0]
    			mode=self.analysis.mode([header],self.data_inuse)[0,0]
    			median=self.analysis.median([header],self.data_inuse)[0]
    			
    			#use messageBox to give user stats information 
    			info=""
    			strings=["max: "+str(round(max,3))+"\n","min: "+str(round(min,3))+"\n","mean: "+str(round(mean,3))+"\n",
    			"stdev: "+str(round(stdev,3))+"\n","mode: "+str(round(mode,3))+"\n","median: "+str(round(median,3))]
    			for string in strings:
    				info=info+string
    			tkMessageBox.showinfo("stats information of "+header,info)
    			
    			
    
    
    
    
    
    
    			
   	#project 6 PCA methods 
   
   	'''
    enable the user to apply PCA analysis to the given data object
    '''
    def handlePCA(self):
    	
    	if self.data==None:
    		tkMessageBox.showwarning("Attention","please open a valid file FIRST")
    		return 
    	
    	#create a dialog to let the user to select which dimensions to apply 
    	#PCA analysis 
    	headers=self.data.get_headers()
    	p_dialog=apply_pca_dialog(self.root,headers)
    	pca_indexes=p_dialog.result 
    	normalized=p_dialog.normalized.get()
    	
    	
    	#process user's selection 
    	#first deal with selection dimensions
    	if len(pca_indexes)==0:
    		return 
    	elif len(pca_indexes)<2:
    		tkMessageBox.showwarning("Attention","please select at least TWO dimensions")
    		return 
    	else:
    		pca_headers=[]
    		for index in pca_indexes:
    			pca_headers.append(headers[index])
    	
    	#manipulate the name of the analysis 
    	name=p_dialog.name 
    	if name=="":
    		tkMessageBox.showwarning("Attention","please name your analysis") 
    		return 
    	if name in self.pca_map.keys():
    		tkMessageBox.showwarning("Attention","name already exists; please choose another one")
    		return
    	
		
    	
    	
    	p_data=self.analysis.pca(self.data,pca_headers,normalized,name)	
    	self.pca_map[name]=p_data
    	
    	
    
    '''
    save a PCA analysis file for later use 
    '''
    def handleSavePCA(self):
    	
    	keys=self.pca_map.keys()
    	if len(keys)==0:
			tkMessageBox.showwarning("ATTENTION","please do a PCA analysis FIRST")
			return 
    	
    	s_dialog=save_pca_dialog(self.root,keys)
    	pca_indexes=s_dialog.result 
    	
    	if len(pca_indexes)==0:
    		return 
    	else:
    		pca_index=pca_indexes[0]
    		key=keys[pca_index]
    		p_data=self.pca_map[key]
    		
    	
    	name=s_dialog.name
    	if name=="":
    		tkMessageBox.showwarning("ATTENTION","please select a name for output file")
    		return 
    	else:
    		name=name+".csv"
    		print name 
    		p_data.write(name)
    		
    	
    	 
    	
    	
    	
    	
    	
    '''
    delete a pca analysis 
    '''
    def delete_pca(self):
    		
    	if len(self.pca_map.keys())==0:
    		tkMessageBox.showwarning("Attention","NO PCA analysis now")
    		return 
    		
    	#process user's selection 
    	p_dialog=single_Dialog(self.root,self.pca_map.keys(),"delete PCA analysis")
    	if len(p_dialog.result)==0: #the user cancels selection 
    		return  
    	else:
    		key=self.pca_map.keys()[p_dialog.result[0]]
    	
    	del self.pca_map[key]
    	
    	
    	
    	
    	
    	
    	
    	
    '''
    enable the use to see the eigen vectors of the corresponding analysis 
    '''
    def show_pca_data(self):
    	
    	if len(self.pca_map.keys())==0:
    		tkMessageBox.showwarning("Attention","please do a PCA analysis first")
    		return 
    	
    	#process user's selection 	
    	p_dialog=single_Dialog(self.root,self.pca_map.keys(),"select a PCA analysis")
    	if len(p_dialog.result)==0: #the user cancels selection 
    		return  
    	else:
    		key=self.pca_map.keys()[p_dialog.result[0]]
    	
    	
    	#now show the selected PCA analysis 
    	pca_data=self.pca_map[key]
    	
    	pca_info=pca_info_dialog(self.root,pca_data)
    	
    	 
    	
    	
    
    '''
    plot the data projected onto PCA 
    enable the user to select which PCA axis to plot 
    '''
    def plotPCA(self):	
    	
    	#first check whether there are valid PCA objects 
    	if len(self.pca_map.keys())==0:
    		tkMessageBox.showwarning("Attention","please do a PCA analysis first")
    		return 
    	
    	#first enable the user to select analysis 
    	p_dialog=single_Dialog(self.root,self.pca_map.keys(),"Select PCA analysis")
    	if len(p_dialog.result)==0: #the user cancels selection 
    		return  
    	else:
    		key=self.pca_map.keys()[p_dialog.result[0]]
    		pca_data=self.pca_map[key]
    		
    		
    	
    	#now enable the user to select axes 
    	self.data_inuse=pca_data
    	self.handleChooseAxes(pca_data)
    	self.colorScheme="smooth"
    	self.buildPoints()
    	
    	
    	
    	
    #project 7 clustering method 	
    '''
    enable the user to perform clustering on specified headers 
    '''
    def handleCluster(self):
    	
    	if self.data==None:	
    		tkMessageBox.showwarning("Attention","please open a valid file FIRST")
    		return 
    		
    		
    	#now allow the user to choose whether to plot using eigens 
    	keys=self.pca_map.keys()
    	if len(keys)!=0:
    		sg=single_Dialog(self.root,keys,"Append a PCA analysis?")
    		result=sg.result
    		if len(result)!=0:
    			if result[0]!=None:
    				key=keys[result[0]]
    				self.data_inuse=self.data.merge(self.pca_map[key])
    	
    	
    	#create a dialog box to let the user select clustering parameters 
    	c_dialog=apply_cluster_dialog(self.root, self.data_inuse.get_headers())
    	headers=self.data_inuse.get_headers()
    	cluster_indexes=c_dialog.result 
    	
    	
    	#process user's selection 
    	#first deal with selection dimensions
    	if len(cluster_indexes)==0:
    		return 
    	elif len(cluster_indexes)<2:
    		tkMessageBox.showwarning("Attention","please select at least TWO dimensions")
    		return 
    	else:
    		cluster_headers=[]
    		for index in cluster_indexes:
    			cluster_headers.append(headers[index])
    	
    	#manipulate the name of the analysis 
    	name=c_dialog.name 
    	if name=="":
    		tkMessageBox.showwarning("Attention","please name your clustering") 
    		return 
    	if name in self.cluster_map.keys():
    		tkMessageBox.showwarning("Attention","name already exists; please choose another one")
    		return
    		
    		
    	#manipulate the number of cluster 
    	num=c_dialog.num
    	try:
    		num=int(num)
    	except ValueError:
    		tkMessageBox.showwarning("Attention:Number of Clusters", "please input a number between 2 and 15") 
    		return
    	if num>15 or num<2:
    		tkMessageBox.showwarning("Attention:Number of Clusters", "please input a number between 2 and 15") 
    		return 
    		
    		
    	#now deal with metrics 
    	metrics=["Euclidean","Manhattan","Cosine"]
       	if len(c_dialog.metric)==0:
       		tkMessageBox.showwarning("Attention:Metrics","please chooose at at least one metric")
       		return 
       	else:
       		metric=metrics[c_dialog.metric[0]]
       		
       	
       	 
    	#create a cluster object and put it to the cluster map
    	means,codes,error=self.analysis.kmeans(self.data_inuse,cluster_headers,num,metric)
    	cluster=Cluster(name,num,headers,metric,means,codes)
    	
    	self.cluster_map[name]=cluster 
    	
    	
    	
    
    '''
    display the info about a cluster object 
    '''
    def show_cluster_data(self):
    	if len(self.cluster_map.keys())==0:
    		tkMessageBox.showwarning("Attention","please do a cluster analysis first")
    		return 
    	
    	#process user's selection 	
    	c_dialog=single_Dialog(self.root,self.cluster_map.keys(),"Select cluster analysis")
    	if len(c_dialog.result)==0: #the user cancels selection 
    		return  
    	else:
    		key=self.cluster_map.keys()[c_dialog.result[0]]
    	
    	
    	#now show the selected PCA analysis 
    	cluster=self.cluster_map[key]
    	cluster_info=cluster_info_dialog(self.root,cluster)
    	

    	
    	
    	
    	
    	
    			
    	
    
    
    
    '''
    change vup, vpr, u so that we change our view to xz data 
    this means looking in negative y-direction 
    '''
    def viewXZ(self,event=None): 
    	self.view.vrp=np.matrix([0.5,-1.0,0.5])
    	self.view.vpn=np.matrix([0,-1.0,0])
    	self.view.u=np.matrix([1.0,0,0])
    	self.view.vup=np.matrix([0,0,1.0])
    	self.update_axes()
    	self.updatePoints()
    
    
    '''
    yz-data 
    this means looking in the negative x-direction 
    ''' 
    def viewYZ(self,event=None):
    	self.view.vrp=np.matrix([0.5,-1.0,0.5])
    	self.view.vpn=np.matrix([-1.0,0,0])
    	self.view.u=np.matrix([0,1.0,0])
    	self.view.vup=np.matrix([0,0,1.0])
    	self.update_axes()
    	self.updatePoints()
    	
    	
    '''	
    resize the data objects and axes according to the change of size of the canvas 
    '''
    def handleResize(self,event=None):
    	
    	width=self.canvas.winfo_width()
    	height=self.canvas.winfo_height()
    	
    	x_factor=float(width)/float(self.base_width)
    	y_factor=float(height)/float(self.base_height) 
    	
    	#change the view object according to the scaling of the canvas 
    	self.view.screen[0]=x_factor*self.base_screen[0]
    	self.view.screen[1]=y_factor*self.base_screen[0]
    	
    	self.update_axes()
    	self.updatePoints()
    	
    	

    def main(self):
        print 'Entering main loop'
        self.root.mainloop()	






#feel free to neglect the following code 
#they are used to create the dialog box to enable user to select 






		 
'''
design a dialog box to let the user decides which columns of data to plot on which axis 
also enable the user to set size and color, which is calculated based on the column the user selects
the initialization and button box part copied from effbot.org 
the parameter dat is a data object 
updated for project 6:enalbing choosing projected PCA values as dimensions 
'''
class Axes_dialog(Dialog):

	def __init__(self,parent,dat,clustered=False):
		self.dat=dat
		self.clustered=clustered #if already clustered, do not append color choice 
		Dialog.__init__(self,parent,title="Plot data")
	
	
	
	#using listbox to enable user selection 	
	def body(self,master):
		
		#first create labels 
		tk.Label(master,text="X").grid(row=0,column=0)
		self.e1=tk.Listbox(master,selectmode=tk.SINGLE,exportselection=0)
		
		tk.Label(master,text="Y").grid(row=0,column=1)
		self.e2=tk.Listbox(master,selectmode=tk.SINGLE,exportselection=0)
		
		tk.Label(master,text="Z").grid(row=0,column=2) 
		self.e3=tk.Listbox(master,selectmode=tk.SINGLE, exportselection=0)
		
		tk.Label(master,text="Size").grid(row=0,column=3)
		self.e4=tk.Listbox(master,selectmode=tk.SINGLE,exportselection=0)
	
		tk.Label(master,text="Shape").grid(row=0,column=4)
		self.e5=tk.Listbox(master,selectmode=tk.SINGLE,exportselection=0)
		
		if self.clustered==False:
			tk.Label(master,text="Color").grid(row=0,column=5)
			self.e6=tk.Listbox(master,selectmode=tk.SINGLE,exportselection=0) 
		
		
		 
		
		
		#insert all numeric headers as options and making grids 
		if self.clustered:#no color option
			lists=[self.e1,self.e2,self.e3,self.e4,self.e5]
		else:
			lists=[self.e1,self.e2,self.e3,self.e4,self.e5,self.e6]
		
		for i in range(len(lists)):
			for header in self.dat.get_headers(): 
				lists[i].insert(tk.END,header)
			lists[i].grid(row=1,column=i)
			
		


		
	'''
	modify the result field according to user's selection 
	'''
	def apply(self):
		if self.clustered:
			lists=[self.e1.curselection(),self.e2.curselection(),self.e3.curselection(),
				self.e4.curselection(),self.e5.curselection()]
		else:
			lists=[self.e1.curselection(),self.e2.curselection(),self.e3.curselection(),
				self.e4.curselection(),self.e5.curselection(),self.e6.curselection()]
		
				
		for list in lists:
			if len(list)<1:
				self.result.append(None) 
			else:
				self.result.append(list[0])
		




'''
design a dialog box that enables the user to select dependent 
variable and independent variables for linear regression 
'''
class regression_dialog(Dialog):
	
	def __init__(self,parent,headers):
		self.headers=headers
		Dialog.__init__(self,parent,title="Select dependent and independent variables")
		
	
	'''
	using list box to enable user selection 
	'''
	def body(self,master):
		
		#create labels 
		
		tk.Label(master,text="Independent Variable 1").grid(row=0,column=0)
		self.e1=tk.Listbox(master,selectmode=tk.SINGLE,exportselection=0)
		
		tk.Label(master,text="Independent Variable2").grid(row=0,column=1)
		self.e2=tk.Listbox(master,selectmode=tk.SINGLE,exportselection=0)
		
		tk.Label(master,text="Dependent Variable").grid(row=0,column=2)
		self.e3=tk.Listbox(master,selectmode=tk.SINGLE,exportselection=0)
		
		
		#insert all numeric headers as options and making grids 
		lists=[self.e1,self.e2,self.e3]
		for i in range(3):
			for header in self.headers:
				lists[i].insert(tk.END,header)
			lists[i].grid(row=1,column=i)


	'''
	modify the result field according to user's selection 
	'''
	def apply(self):
		lists=[self.e1.curselection(),self.e2.curselection(),self.e3.curselection()]
		for list in lists:
			if len(list)<1:
				self.result.append(None)
			else:
				self.result.append(list[0])





#dialog to deal with PCA 





'''
design a dialog box that enables the user to select columns 
to apply PCA analysis 
'''
class apply_pca_dialog(Dialog):
	
	def __init__(self,parent,headers):
		self.headers=headers
		self.metrics=[]
		Dialog.__init__(self,parent,title="Select columns for PCA")
		
		
		
	def body(self,master):
		
		tk.Label(master,text="Dimensions").grid(row=0,column=0)
		self.e1=tk.Listbox(master,selectmode=tk.MULTIPLE,exportselection=0)
		for header in self.headers:
			self.e1.insert(tk.END,header)
		self.e1.grid(row=1,column=0)
		
		
	
		#for convenience,give the user the freedom to select or deselect all items 
		self.all_select=tk.Button(master,text="select all", command=self.selectAll)
		self.all_select.grid(row=2, column=0)
		self.all_deselect=tk.Button(master,text="deselect all", command=self.deselectAll)
		self.all_deselect.grid(row=2, column=1)
		
		
		#let the user decide whether to normalize data 
		self.normalized=tk.BooleanVar()
		self.button=tk.Checkbutton(master,text="Normalize",variable=self.normalized)
		self.button.grid(row=3,column=0)
		
		#let the user select a name for PCA analysis 
		tk.Label(master, text="Analysis Name").grid(row=4, column=0)
		self.entry = tk.Entry(master)
		self.entry.grid(row=4, column=1)
	
	
	
	def selectAll(self):
		self.e1.select_set(0, tk.END)
		
		
	def deselectAll(self):
		self.e1.select_clear(0, tk.END)
	
	
	#modify the result field according to user's selection 	
	def apply(self):
		self.name=self.entry.get()
		selection = self.e1.curselection() 
		if len(selection)>=1:
			for select in selection:
				self.result.append(select)
	
	

		



'''
this class displays the info of the selected pca analysis 
'''
class pca_info_dialog(Dialog):

	
	def __init__(self,parent,pca):
		self.pca=pca 
		Dialog.__init__(self,parent,title="PCA info")

	
	def body(self,master):
		
		tk.Label(master,text="e-vec").grid(row=0,column=0)
		tk.Label(master,text="e-val").grid(row=0,column=1)
		tk.Label(master,text="cumulative").grid(row=0,column=2)
		headers=self.pca.get_data_headers()
		for i in range(len(headers)):
			tk.Label(master,text=headers[i]).grid(row=0,column=3+i)
			
		#now put eigen vector values into the display 
		e_vectors=self.pca.get_eigenvectors()
		e_vals=self.pca.get_eigenvalues()
		cumu=self.pca.get_cumulative()
		for i in range(len(e_vectors)):
			row_num=i+1
			name="pc"+str(i)
			tk.Label(master,text=name).grid(row=row_num,column=0)
			tk.Label(master,text=str(round(e_vals[i],4))).grid(row=row_num,column=1)
			tk.Label(master,text=str(round(cumu[i],4))).grid(row=row_num,column=2) 
			
			e_vector=e_vectors[i]
			for j in range (e_vector.shape[1]):
				tk.Label(master,text=str(round(e_vector[0,j],4))).grid(row=row_num,column=3+j)
		




'''
this class displays info of a user chosen cluster 
'''
class save_pca_dialog(Dialog):
	
	def __init__(self, parent,headers):
		self.headers=headers
		Dialog.__init__(self,parent,title="save PCA")

	
	def body(self,master):
		
		tk.Label(master,text="select PCA").grid(row=0,column=0)
		self.e1=tk.Listbox(master,selectmode=tk.SINGLE,exportselection=0)
		for header in self.headers:
			self.e1.insert(tk.END,header)
		self.e1.grid(row=1,column=0)
		
		#let the user select a name for PCA output file  
		tk.Label(master, text="Output Filename").grid(row=2, column=0)
		self.entry = tk.Entry(master)
		self.entry.grid(row=3, column=0)
		
		
	#modify the result field according to user's selection 	
	def apply(self):
		self.name=self.entry.get()
		selection = self.e1.curselection() 
		if len(selection)>=1:
			for select in selection:
				self.result.append(select)
	
		
		








#dialog to deal with clusters 



'''
a dialog that enables the user to select which headers to use for clustering,
the number of clusters and metric  
'''
class apply_cluster_dialog(Dialog):
	
	def __init__(self,parent,headers):
		self.headers=headers
		self.metric=[]
		Dialog.__init__(self,parent,title="Select Clustering parameters")
	
	def body(self,master):
		
		tk.Label(master,text="Dimensions").grid(row=0,column=0)
		self.e1=tk.Listbox(master,selectmode=tk.MULTIPLE,exportselection=0)
		for header in self.headers:
			self.e1.insert(tk.END,header)
		self.e1.grid(row=1,column=0)
		
		#set metric 
		tk.Label(master,text="Metric").grid(row=0,column=1)
		self.e2=tk.Listbox(master,selectmode=tk.SINGLE,exportselection=0)
		for metric in ["Euclidean","Manhattan","Cosine"]:
			self.e2.insert(tk.END,metric)
		self.e2.grid(row=1,column=1)
		
		#enable the user to select number of clusters 
		tk.Label(master,text="Num of Clusters").grid(row=3,column=0)
		self.num_entry=tk.Entry(master)
		self.num_entry.grid(row=3,column=1)
		
		
		#for convenience,give the user the freedom to select or deselect all items 
		self.all_select=tk.Button(master,text="select all dimensions", command=self.selectAll)
		self.all_select.grid(row=2, column=0)
		self.all_deselect=tk.Button(master,text="deselect all dimensions", command=self.deselectAll)
		self.all_deselect.grid(row=2, column=1)
		
	
		
		#let the user select a name for cluster analysis 
		tk.Label(master, text="Cluster Name").grid(row=4, column=0)
		self.entry = tk.Entry(master)
		self.entry.grid(row=4, column=1)
		
		
	def selectAll(self):
		self.e1.select_set(0, tk.END)
		
		
	def deselectAll(self):
		self.e1.select_clear(0, tk.END)
	
	
	#modify the result field according to user's selection 	
	def apply(self):
		self.num=self.num_entry.get()
		self.name=self.entry.get()
		selection = self.e1.curselection() 
		if len(selection)>=1:
			for select in selection:
				self.result.append(select)
		metric=self.e2.curselection()
		if len(metric)>0:
			self.metric.append(metric[0])
				





'''
this class displays info of a user chosen cluster 
'''
class cluster_info_dialog(Dialog):
	
	def __init__(self, parent,cluster):
		self.cluster=cluster 
		Dialog.__init__(self,parent,title="cluster info")

	
	def body(self,master):
		
		tk.Label(master,text="Name:").grid(row=0,column=0)
		tk.Label(master,text=self.cluster.name).grid(row=0,column=1)
		
		tk.Label(master,text="Metric:").grid(row=1,column=0)
		tk.Label(master,text=self.cluster.metric).grid(row=1,column=1) 
		
		tk.Label(master,text="Number of Clusters:").grid(row=2,column=0)
		tk.Label(master,text=self.cluster.num).grid(row=2,column=1) 
		
		tk.Label(master,text="Headers:").grid(row=3,column=0)
		for i in range(len(self.cluster.headers)):
			tk.Label(master,text=self.cluster.headers[i]).grid(row=3,column=i+1)
		



			
'''
this class allows the user to choose clusters and color scheme 
'''	
class cluster_plot_dialog(Dialog):
	
	def __init__(self,parent,headers):
		self.headers=headers
		self.scheme=[]
		Dialog.__init__(self,parent,title="Choose a Cluster Analysis?")
	
	
	def body(self,master):
		
		tk.Label(master,text="clusters").grid(row=0,column=0)
		self.e1=tk.Listbox(master,selectmode=tk.SINGLE,exportselection=0)
		for header in self.headers:
			self.e1.insert(tk.END,header)
		
		
		
		colorScheme=["pre-selected","smooth"]
		tk.Label(master,text="color scheme").grid(row=0,column=1)
		self.e2=tk.Listbox(master,selectmode=tk.SINGLE,exportselection=0)
		for scheme in colorScheme:
			self.e2.insert(tk.END,scheme)
		
		self.e1.grid(row=1,column=0)
		self.e2.grid(row=1,column=1)
			
	def apply(self):
		select=self.e1.curselection()
		if len(select)>0:
			self.result.append(select[0])
		color=self.e2.curselection()
		if len(color)>0:
			self.scheme.append(color[0])
		
	

'''
this class can be used for all single choice selection 
'''
class single_Dialog(Dialog):
	
	def __init__(self,parent,headers,label_name):
		self.headers=headers
		self.label_name=label_name
		Dialog.__init__(self,parent,title="Select a Column")

	
	#using listbox to enable user selection 	
	def body(self,master):
		
		#create a label 
		tk.Label(master,text=self.label_name).grid(row=0,column=0)
		self.e1=tk.Listbox(master,selectmode=tk.SINGLE,exportselection=0)
		
		
		#insert all numeric headers as options
		for header in self.headers:
			self.e1.insert(tk.END,header)

		
		#making grids 
		self.e1.grid(row=1,column=0)
	

	
	'''
	modify the result field according to user's selection 
	'''
	def apply(self):
		select=self.e1.curselection()
		if len(select)>=1:
			self.result.append(select[0])



		





	
	



'''	
an entry box for user to input filename 
'''
class fileEntry(Dialog):
	
	def __init__(self,parent):
		Dialog.__init__(self,parent,title="input filename to save")
	

	def body(self,master):
		self.entry=tk.Entry(master)
		self.entry.grid(row=2, column=1, sticky=tk.W)
	
	'''
	modify the result field according to user'selection
	'''
	def apply(self):
		result=self.entry.get()
		if result != "":
			self.result.append(result)
			












'''
this class holds the information about a clustering 
'''		
class Cluster:
	
	def __init__(self,name,num,headers,metric,means,clusterIDs):
		
		self.name=name #user selected name of the cluster 
		self.num=num #user selected num of clusters 
		self.headers=headers #user selected headers 
		self.metric=metric #user selected metric 
		self.means=means #calculated data center  
		self.clusterIDs=clusterIDs # a N*1 numpy matrix saving the cluster ID of each point
		
	
	
	

		
'''
multiply a matrix by a float 
'''
def multiply(f,matrix):
	
	row_num=matrix.shape[0]
	col_num=matrix.shape[1]
	newMatrix=np.zeros((row_num,col_num))
	
	for i in range(row_num):
		for j in range(col_num):
			newMatrix[i,j]=f*matrix[i,j]
	
	return newMatrix
	
	
'''
given a list of float numbers, return a list of string 
representation of the numbers rounded to three digits
'''
def roundL(list):
	newList=[]
	for num in list:
		new_num=round(num,3)
		newList.append(str(new_num))
	return newList
	
	
'''
given a matrix of float numbers,
round all numbers to 3 digits
'''
def roundF(matrix):
    
    row_num=matrix.shape[0]
    col_num=matrix.shape[1]
    newMatrix=np.zeros((row_num,col_num))
        
    for i in range(row_num):
        for j in range(col_num):
            newMatrix[i,j]=round(matrix[i,j],3)
        
    return newMatrix


	

'''
add a list of strings to a string 
'''
def concat_list(string,list):
	for ele in list:
		string=string+" "+ele
	return string+"\n"	
		
	
	
'''
given a list, count the number of non-NULL elements
''' 
def count(list): 
	num=0
	for item in list:
		if item!=None:
			num=num+1	
	return num 		
			
		
		
		
		


if __name__ == "__main__":
    dapp = DisplayApp(1200, 675)
    dapp.main()


