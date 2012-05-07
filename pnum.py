import os
import os.path
import sys
import subprocess
import re

CAD="R:\\"
EXPLORE="C:\\Windows\\explorer.exe"

# Parts of the project number (7501-002  75=head  01=major 002=minor)
def process_pnum(pnum):
	pn=str(pnum)
	rx=re.compile(r'([0-9]{2,3})([0-9]{2})(-[A-Z0-9]+)?')
	m=rx.match(pnum)
	if m: return m.groups()
	return []

# Decides what the best selections are from a <lst>, if the project number is <pnum>
def best_selections(lst,pnum):
        (head,major,minor)=pnum
        #kludge to avoid selecting a "major-only" revision over the ones with minor revisions
        if not minor: minor=r'$'
	#arbitrary design decision: disallow leading characters before the project number
	head = "^"+head
        formats=[head+major+minor,head+major,head+"xx"]
        tries=[fuzzy_filter(lst,selection) for selection in formats]
        t=[a for a in tries if len(a)>0]
        if t: return t[0]
        return []

# Filters a list for a relatively close match to <s>
def fuzzy_filter(lst,s):
        return [a for a in lst if re.findall(s,a,re.IGNORECASE)]

# Allows the user to select from a list of options in order to disambiguate
def choose_interactively(r):
        if len(r) == 0:
                print("No match")
                return None
        if len(r) > 0:
                for (a,i) in zip(r,range(1,len(r)+1)):
                    print("%d   %s" % (i,a))
                c = raw_input("Choice: ")
                if c==" ": c="1"
                if c in map(str,range(1,len(r)+1)):
                    print(str(r[int(c)-1])+"\n")
                    return r[int(c)-1]
        else:
            return None
        
# Runs through the directory tree, starting from <path>, picking the best_selections()
#  at each node
def traverse(path,search):
	os.chdir(path)
	dirs=[f for f in os.listdir(path) if os.path.isdir(os.path.join(path,f))]
	pp=process_pnum(search)
	if pp:
		b=best_selections(dirs,pp)
	else:
		b=fuzzy_filter(dirs,search)
	if len(b) == 0: return path
	if len(b) == 1: return traverse(os.path.join(path,b[0]),search)
	if len(b) > 1:
		c=choose_interactively(b)
		if c:
			return traverse(os.path.join(path,c),search)
		else:
			return path

# For more info than simply a project number (e.g. 7501 TIF)
def multi_traverse(p,l):
	if len(l) == 1:
		return traverse(p,l[0])
	else:
		return multi_traverse(traverse(p,l[0]),l[1:])


def explore_dir(e,dir):
	return subprocess.call([e,dir])
	
if __name__=="__main__":
	print sys.argv[1:]
	if len(sys.argv)>1:
		explore_dir(EXPLORE,multi_traverse(CAD,sys.argv[1:]))
	else:
		explore_dir(EXPLORE,CAD)

