import sqlite3
import sys
import datetime
from math import *
from os import listdir
from os.path import sep
from shutil import move

#TODO When spreading hours across multiple days, avoid the weekends!
#TODO Split by week?


SAVPATH=sep.join(["S:","Misc","Util"])
DB = 'bill-db.db'
def get_standard_db():
	return sqlite3.connect(DB)

def init_db():
	today = datetime.datetime.today()
	if (DB in listdir(SAVPATH)):
		move(SAVPATH + sep + DB,SAVPATH + sep + "bill-db_" + str(today.toordinal()) + "-" + str(today.microsecond))
	db = get_standard_db()
	c = db.cursor()
	r = c.execute("CREATE TABLE IF NOT EXISTS billing (id INTEGER PRIMARY KEY AUTOINCREMENT, recharge STRING, date DATE, time FLOAT)")
	db.commit()
	db.close()



################### BEGIN

def round_hours(hours):
	return 0.25 * ceil(hours * 4.)

def run_sql(sql,args=[],loadDB=None):
	if not loadDB:
		db = get_standard_db()
	else:
		db = loadDB

	c = db.cursor()
	r = c.execute(sql,args)
	m = r.fetchall()

	if not loadDB:
		db.commit()
		db.close()

	return m


def billing_insert(values,loadDB=None):
	ss =  "INSERT INTO billing VALUES (NULL," + ",".join(["?"]*len(values)) + ")"
	return run_sql(ss,values,loadDB)

def add_hours(recharge,date,hours=0.5,loadDB=None): 
	return billing_insert( (recharge, date, round_hours(hours)), loadDB)
	
def add_hours_range(recharge,start_date,end_date,hours=0.5):
	start = datetime.datetime.strptime(start_date,"%m/%d/%Y")
	end = datetime.datetime.strptime(end_date,"%m/%d/%Y")
	hrs_per_day = ceil(float(hours)*60 / float((end-start).days+1))/60.
	db = get_standard_db()
	for d in range(0,(end-start).days+1):
		add_hours(recharge, (start + datetime.timedelta(d)).strftime("%m/%d/%Y"), round_hours(hrs_per_day), db)
	db.commit()
	db.close()
	return hrs_per_day

def add_hours_fuzzy(recharge,start,hours=0.5,end=None):
	today = datetime.datetime.today()
	(year,month,day) = map(str,(today.year,today.month,today.day))

	s = start.split("/")
	if len(s) == 3:
		start_date = s
	elif len(s) == 2:
		start_date = (s[0],s[1],year)
	elif len(s) == 1:
		start_date = (month,s[0],year)
	else:
		return None
	
	if not end:
		end_date = start_date
	else:
		e = end.split("/")
		if len(e) == 3:
			end_date = e
		elif len(e) == 2:
			end_date = (e[0],e[1],start_date[2])
		elif len(e) == 1:
			end_date = (start_date[0],e[0],start_date[2])
		else:
			return None
	
	return add_hours_range(recharge,"/".join(start_date),"/".join(end_date),hours)
		



def print_all_entries():
	m = run_sql("SELECT * FROM billing")
	if m:
		return "\n".join(map(str,m))
	else:
		return None

def work_by_day():
	m = run_sql("SELECT recharge, date, SUM(time) FROM billing GROUP BY recharge, date")
	if m:
		t = ["\t".join(map(str,x)) for x in m]
		listing = "\n".join(t)
		return listing
	else:
		return None

def work_by_day_to_file(f=None):
	if not f: f = SAVPATH+sep+"timesheet-helper.tab"
	file = open(f,'w')
	listing = work_by_day()
	if file and listing:
		file.write(listing)
		file.close()
		return "Written to: "+f
	else:
		return None

def from_file_add(f,d="\t"):
	try:
		file = open(f)
	except IOError:
		print("Error opening %s" % f)
		file = None
	if not file: return None
	lines = file.readlines()
	for l in lines:
		print(l)
		l = l.strip()
		tks = l.split(d)
		if (not l) or (len(tks) < 2): 
			print("Unable to process line: %s" % l)
		add_hours_fuzzy(*tks)
	print ("Done reading %d lines" % len(lines))
		


################### END






def run_prompt():
	print("### Enter any of the following commands:")
	print(command_list())
	print("")
    	craw=raw_input("### Command: ")
	if craw:
		c=craw.split()
		run_command(c[0],c[1:])


def command_list():
	ctxt = []
	cmds = [(v,CMD[v]) for v in sorted(CMD.keys())]
	for (name,(f,args,optargs,desc)) in cmds:
		args = " ".join(["<"+a+">" for a in args])
		optargs = " ".join(["["+a+"]" for a in optargs])
		txt = "%s %s %s\n%s" % (name,args,optargs,desc)
		ctxt.append(txt)
	return "\n\n".join(ctxt)

def run_command(cmd,args=[]):
	print("---")
	c = cmd.lower()
	if c in CMD.keys() and len(args) >= len(CMD[c][1]):
		print(apply( CMD[cmd.lower()][0], args ))
		print("")
		r=raw_input("")
	else:
		print(">>> ERROR: Invalid command, or incorrect usage.  Valid commands are:")
		run_command("commands")

def exit():
	return sys.exit(0)


CMD = { \
        "commands":(command_list,[],[],"List the commands available")
      , "init":(init_db,[],[],"Initializes the database")
      , "add-range":(add_hours_range,["recharge","start_date","end_date"],["hours=0.5"],"Add total hours evenly divided over a date range")
      , "add":(add_hours,["recharge","date","hours"],[],"Add hours to a specific date")
      , "quit":(exit,[],[],"Exit the command line") 
      , "list":(print_all_entries,[],[],"Prints all the entries in the database")
      , "a":(add_hours_fuzzy,["recharge","start_date"],["hours=0.5","end_date=start_date"],"Quickest way to add to the database")
      , "list-daily":(work_by_day,[],[],"Print how much work was done each day")
      , "list-daily-save":(work_by_day_to_file,[],["filename"],"Print how much work was done each day to a file")
      , "fuzzy-add-from-file":(from_file_add,["filename"],["delimiter=(tab)"],"Read in things to add (in the style of \'a\') from a file.")
      }


def main():
    if len(sys.argv) == 1:
    	while (1==1):
		run_prompt()
    if len(sys.argv) > 1:
        if len(sys.argv) > 2:
	    run_command(sys.argv[1],sys.argv[2:])
        else:
            run_command(sys.argv[1])
    

if __name__=="__main__":
    main()



