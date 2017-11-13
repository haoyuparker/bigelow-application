#Filename:view.py 
#CS251, Project 3
#Haoyu Song 


import numpy as np 
import math 
import copy 



'''
a class that manages viewing parameters and builds transformation matrix 
'''

class View:
	
	'''
	initialize viewing fields and screen fields 
	all saved as numpy matrix 
	'''
	def __init__(self):
		
		self.vrp=np.matrix([0.5,0.5,1.0])
		self.vpn=np.matrix([0.0,0.0,-1.0])
		self.vup=np.matrix([0.0,1.0,0.0])
		self.u=np.matrix([-1.0,0.0,0.0])
		self.extent=np.matrix([1.0,1.0,1.0])
		self.screen=[400.0,400.0]
		self.offset=[20.0,20.0]
		
	'''
	builds the transformation matrix
	'''
	def build(self):
		
		vtm = np.identity( 4, float ) #dimension:4*4
		
		#first generate a transformation matrix moving VRP to the origin
		tr=np.matrix([[1,0,0,-self.vrp[0,0]],
					 [0,1,0,-self.vrp[0,1]],
					 [0,0,1,-self.vrp[0,2]],
					 [0,0,0,1]])
		
		vtm=tr*vtm
		
		#set the view reference frame
		tu=np.cross(self.vup,self.vpn) #use cross product to ensure orthogonality 
		tvup=np.cross(self.vpn,tu)
		tvpn=self.vpn.copy()
		
		#normalization 
		self.u=normalize(tu)
		self.vup=normalize(tvup)
		self.vpn=normalize(tvpn)
	
		
		
		#align the axis using rotational matrix 
		r1 = np.matrix( [[ tu[0, 0], tu[0, 1], tu[0, 2], 0.0 ],
		                    [ tvup[0, 0], tvup[0, 1], tvup[0, 2], 0.0 ],
		                    [ tvpn[0, 0], tvpn[0, 1], tvpn[0, 2], 0.0 ],
		                    [ 0.0, 0.0, 0.0, 1.0 ] ] )
		
		vtm = r1 * vtm
		
		
		#translate the lower left corner to the origin
		tr=np.matrix([[1,0,0,0.5*self.extent[0,0]],
						[0,1,0,0.5*self.extent[0,1]],
						[0,0,1,0],
						[0,0,0,1]])
		vtm=tr*vtm 
		
		
		#scale to the screen size 
		sc=np.matrix([[-self.screen[0]/self.extent[0,0],0,0,0],
					[0,-self.screen[1]/self.extent[0,1],0,0],
					 [0,0,1.0/self.extent[0,1],0],
					 [0,0,0,1]])
		vtm=sc*vtm 
		
		# translate the lower left corner to the origin and add the view offset		
		# gives a little buffer around the top and left edges of the window
		tr=np.matrix([[1,0,0,self.screen[0]+self.offset[0]],
						[0,1,0,self.screen[1]+self.offset[1]],
						[0,0,1,0],
						[0,0,0,1]])
		vtm=tr*vtm 
		
		return vtm 
		
	
	
	'''
	create another view object with the same fields 
	'''	
	def clone(self):
		
		#use deep copy so that we copy the exact value
		#rather than a reference  
		v=View()
		v.vrp=self.vrp.copy()
		v.vpn=self.vpn.copy()
		v.vup=self.vup.copy()
		v.u=self.u.copy()
		v.extent=copy.deepcopy(self.extent)
		v.screen=copy.deepcopy(self.screen)
		v.offset=copy.deepcopy(self.offset)
		return v 
		
		
	'''
	rotation about the center of the volume 
	angle 1 specifies how much to rotate about u axis 
	angle 2 specifies how much to rotate about vup
	'''
	def rotateVRC(self,angle_up,angle_u):
		
		#first translation 
		point=self.vrp+self.vpn*self.extent[0,2]*0.5
		t1=np.matrix([[1,0,0,-point[0,0]],
					[0,1,0,-point[0,1]],
					[0,0,1,-point[0,2]],
					[0,0,0,1]])
		
		#align Rxyz using u,vup and vpn
		Rxyz=np.matrix([[self.u[0,0],self.u[0,1],self.u[0,2],0.0],
					[self.vup[0,0],self.vup[0,1],self.vup[0,2],0.0],
					[self.vpn[0,0],self.vpn[0,1],self.vpn[0,2],0.0],
					[0,0,0,1]])
		 
		
		#rotation matrix about y with angle_up
		r1 = np.matrix( [[math.cos(angle_up), 0, math.sin(angle_up), 0],
						[0, 1, 0, 0],
						[-math.sin(angle_up), 0, math.cos(angle_up), 0],
						[0, 0, 0, 1] ] )
		
		#rotation matrix about x with angle_u
		r2=np.matrix([[1,0,0,0],
					[0,math.cos(angle_u),-math.sin(angle_u),0],
					[0,math.sin(angle_u),math.cos(angle_u),0],
					[0,0,0,1]])
					
		#undo translate 
		t2=np.matrix([[1,0,0,point[0,0]],
					[0,1,0,point[0,1]],
					[0,0,1,point[0,2]],
					[0,0,0,1]])
		
		
		tvrc=np.matrix([[self.vrp[0,0],self.vrp[0,1],self.vrp[0,2],1],
						[self.u[0,0],self.u[0,1],self.u[0,2],0],
						[self.vup[0,0],self.vup[0,1],self.vup[0,2],0],
						[self.vpn[0,0],self.vpn[0,1],self.vpn[0,2],0]])	

		tvrc=(t2*Rxyz.T*r2*r1*Rxyz*t1*tvrc.T).T

		
		#now reset vrp,u,vup,vpn
		self.vrp=tvrc[0][0,:3]
		self.u=tvrc[1][0,:3]
		self.vup=tvrc[2][0,:3]
		self.vpn=tvrc[3][0,:3]
		
		#normalization 
		self.u=normalize(self.u)
		self.vup=normalize(self.vup)
		self.vpn=normalize(self.vpn) 
		

'''
normalize a 3d vector to be a matrix 
'''
def normalize(vector):
	
	length=math.sqrt(vector[0,0]*vector[0,0]+vector[0,1]*vector[0,1]+vector[0,2]*vector[0,2])
	normalized=np.zeros((1,3))
	for i in range(3):
		normalized[0,i]=vector[0,i]/length
	return np.matrix(normalized)
	

if __name__=="__main__":
	view=View()

