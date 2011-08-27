import datetime
import hashlib
import sqlite3
import re
import sys
import os

DB="fuser.db"
SAVPATH=os.path.sep.join(["S:","Misc","Util"])

def init_db():
	db=get_standard_db()
	c=db.cursor()
	r=c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, user STRING, date STRING)")
	db.commit()
	db.close()

def get_standard_db():
	return sqlite3.connect(DB)

class String_Compute:
	def __init__(self,s=""):
		self.s = self.hash_it(s)
		self.asc_first = 0
		self.VARS = {"caps":False
			    ,"numtostr":True
			    ,"advance":True}
		self.COMPS = \
			{ '1':"caps"
			, '2':"caps"
			, '3':"caps"
			, '4':"caps"
			, '5':"caps"
			, '6':"advance"
			, '7':"advance"
			, '8':"advance"
			, '9':"advance"
			, '0':"advance"
			, 'a':"advance"
			, 'b':"numtostr"
			, 'c':"numtostr"
			, 'd':"numtostr"
			, 'e':"numtostr"
			, 'f':"numtostr"
			}

	def hash_it(self,s):
		return hashlib.sha224(s.lower()).hexdigest()


	def compute(self):
		r=""
		for n in range(0,len(self.s)):
			c=self.s[n]
			w=c

			if self.VARS["caps"]:
				if self.asc_first in range(60,92):
					self.asc_first = 97
				else:
					self.asc_first = 60

			if self.VARS["advance"]:
				if self.asc_first <= 80:
					self.asc_first = self.asc_first + 10
			else:
				if self.asc_first >= 64:
					self.asc_first = self.asc_first - 4 

			if self.VARS["numtostr"]:
				w = chr( 60 + (self.asc_first+int("0x"+c,16))%67 )

			if w not in ['{','}','`','\\','/','%','[',']','\"',"|","\'"] and len(r)<9:
				r = r+w

			self.VARS[self.COMPS[c.lower()]] = (not self.VARS[self.COMPS[c.lower()]])
		return r





def today_mmddyyyy():
	return datetime.datetime.today().strftime("%m/%d/%Y")

def log_user(s,d):
	try:
		date_rex=re.compile(r'[0-9]{2}\/[0-9]{2}\/[0-9]{4}')
		if not date_rex.match(d.strip()):
			raise DateFormatError
		db = get_standard_db()
		r=db.cursor().execute("INSERT INTO users VALUES (NULL,?,?)",(s.lower(),d))
		db.commit()
		db.close()

	except DateFormatError:
		print ">>> ERROR: Invalid date.  Please enter the date in mm/dd/yyyy format and try again."


def mkpass(s):
	if not s: return ""
	pwd = check_pass(s,today_mmddyyyy())
	if pwd: log_user(s,today_mmddyyyy())
	return pwd

class DateFormatError(Exception): pass
def check_pass(s,d=None):
	if not d: d = today_mmddyyyy()
	try:
		date_rex=re.compile(r'[0-9]{2}\/[0-9]{2}\/[0-9]{4}')
		d = d.strip()
		if date_rex.match(d):
			sd = s+d.replace("/","")
			return String_Compute(sd).compute()
		else:
			raise DateFormatError
	except DateFormatError:
		print ">>> ERROR: Invalid date.  Please enter the date in mm/dd/yyyy format and try again."

def users_list():
	r = get_standard_db().cursor().execute("SELECT * FROM users").fetchall()
	if r:
		t = ["\t".join(map(str,x)) for x in r]
		return "\n".join(sorted(t))
	else:
		return None

def users_list_save(f=None):
	if not f: f = "ftp-users_"+today_mmddyyyy().replace("/","-")+".csv"
	r = get_standard_db().cursor().execute("SELECT * FROM users").fetchall()
	if r:
		t = [",".join(map(str,x)) for x in r]
		listing = "\n".join(sorted(t))
		file = open(SAVPATH+os.path.sep+f,'w')
		file.write(listing)
		file.close()
		return "Written to: "+SAVPATH+os.path.sep+f
	else:
		return None




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
CMD = { \
        "ckpass":(check_pass,["user"],["date"],"Given a user (and optionally a date), display the password that would be assigned")
      , "mkpass":(mkpass,["user"],[],"Make a new password for the user, and save it to the database")
      , "list":(users_list,[],[],"Lists all the users that have been added to the database, as well as the dates they were added")
      , "list-save":(users_list_save,[],["filename"],"Saves the user list from the \'list\' command to a file at "+SAVPATH+".  The filename is automatically generated unless overridden with the optional [filename] argument")
      , "commands":(command_list,[],[],"List the commands available")
      , "init":(init_db,[],[],"Initializes the database")
      , "zzzz_  \n\nNOTICE: This password management system has been deprecated in favor of ftp-dropbox.py.  Please update your shortcuts as necessary.":(None,[],[],"")
      }


def main():
    if len(sys.argv) == 1:
    	print("### Enter any of the following commands:")
	print(command_list())
	print("")
    	craw=raw_input("### Command: ")
	if craw:
		c=craw.split()
		run_command(c[0],c[1:])
    if len(sys.argv) > 1:
        if len(sys.argv) > 2:
            run_command(sys.argv[1],sys.argv[2:])
        else:
            run_command(sys.argv[1])
    

if __name__=="__main__":
    main()



