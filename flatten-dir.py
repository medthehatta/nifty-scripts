import os
import os.path
import shutil
import sys

def flatten(top,path):
	for file in os.listdir(path):
		if os.path.isfile(path+"\\"+file):
			print("   " + file)
			shutil.copy(path+"\\"+file,top)
		else:
			print(">> " + file)
			flatten(top,path+"\\"+file)

if not len(sys.argv) > 1: 
	default_top = os.getcwd()
	top = input("What directory to flatten? <%s>" % default_top)
	if not top: top=default_top
else:
	top = sys.argv[1]

flatten(top,top)

