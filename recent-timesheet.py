import os
import subprocess
import sys

EXCELPATH = "C:\\Program Files\\Microsoft Office\\OFFICE11\\EXCEL.EXE"

def newest_file(path):
	return sorted([path + "\\" + a for a in filter(lambda x: str(x).count("xls") > 0, os.listdir(path))])[0]

def main():
	if len(sys.argv) < 2:
	    pathsearch_default = "P:\\Timesheets"
	    pathsearch = input("Which path to open? <%s> " % pathsearch_default)
	    if not pathsearch: pathsearch=pathsearch_default
	else:
	    pathsearch = sys.argv[1]
	    
	tspath = newest_file(pathsearch)
	print("%s %s" % (EXCELPATH,tspath))
	return subprocess.call([EXCELPATH, tspath])

if __name__=="__main__":
	main()
