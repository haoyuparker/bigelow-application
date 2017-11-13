#a general dialog class 
#can be modified for a variety of purpose 

import Tkinter as tk
import tkFont as tkf
import os 




class Dialog(tk.Toplevel):

	def __init__(self,parent,title=None):
		
		tk.Toplevel.__init__(self,parent)
		self.transient(parent)
		
		if title:
			self.title(title)
		
		self.parent=parent 
		
		self.result=[]
		self.cancelled=False 
		
		body=tk.Frame(self)
		self.initial_focus=self.body(body)
		body.pack(padx=5,pady=5)
		
		self.buttonbox()
		
		self.grab_set()
		
		if not self.initial_focus:
			self.initial_focus=self
		
		self.protocol("WM_DELETE_WINDOW",self.cancel)
		
		self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
		                                  parent.winfo_rooty()+50))

		self.initial_focus.focus_set()
		
		self.wait_window(self)
		
	
	#to override 
	def body(self,master):
		return 
		
		
		
	def buttonbox(self):
		
		box=tk.Frame(self)
		
		w=tk.Button(box,text="OK",width=10, command=self.ok,default=tk.ACTIVE)
		w.pack(side=tk.LEFT, padx=5,pady=5)
		w=tk.Button(box,text="Cancel",width=10,command=self.cancel)
		w.pack(side=tk.LEFT,padx=5,pady=5)
		
		self.bind("<Return>",self.ok)
		self.bind("<Escape>",self.cancel)
		
		box.pack()
		
	def validate(self):
		return 1 
		
	def ok(self,event=None):
		
		if not self.validate():
			self.initial_focus.focus_set()
			return 
			
		self.withdraw()
		self.update_idletasks()
		
		self.apply()
		
		self.cancel()
		
	def cancel(self,event=None):
		
		self.cancelled=True 
		self.parent.focus_set()
		self.destroy()
		
	'''
	to override 
	'''
	def apply(self):
		return 
				
