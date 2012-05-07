import random as rnd
import numpy as np
import matplotlib as plt

def perturb_values(points,radius=1):
	perturbers = [-radius + 2*radius*rnd.random() for x in range(0,len(points))]
	return points+perturbers

def fuzzy(f,fuzz=1,xlo=-10,xhi=10,step=0.1):
	xs = np.arange(xlo,xhi,step)
	return zip(xs, perturb_values(f(xs),fuzz))

def transpose_list(lst):
	return np.array(lst).transpose().tolist()
	

	
	
