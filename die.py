"""
Rolls fudge dice with bonuses or penalties
"""

import random 
import re

def base_roll(): return [random.choice([-1,0,1]) for a in [1,2,3,4]]	

def get_embellishments(s): return map(int, re.findall(r'[+-][0-9]+',s))
	
def signed_display(i):
	if i>0: 
		return "+"+str(i)
	else:
		return str(i)

def displayable(f,e):
	f_part = str(f).replace(",","").replace("-1","-").replace("1","+").replace("0","0")
	f_part += " (%d)" % (sum(f),)
	e_part = " ".join( [signed_display(a) for a in e] )
	total  = sum(f) + sum(e)
	if e_part:
		return f_part + "  (" + e_part + ") = {" + signed_display(total) + "}"
	else:
		return f_part

def rollem(s):
	fudge = base_roll()
	embellishments = get_embellishments(s)
	return displayable(fudge,embellishments)

def roll_embellished(phenny,input):
	try:
		if input.group(2):
			result = rollem(input.group(2))
		else:
			result = rollem("")
		phenny.say( input.nick + " rolled: " + result ) 
	except Exception as e:
		phenny.say( str(e) )
roll_embellished.commands=['roll']


