import re
import readline
import sys
from sqlite3 import connect, OperationalError
from hashlib import sha224
from datetime import datetime
from shutil import copytree
from subprocess import call
from urllib import quote
from os.path import sep

DB="fuser.db"
SAVPATH=sep.join(["S:","Misc","Util"])

### For dropbox automation ###
DROPBOX_DIR = sep.join(["S:","Misc","dropbox"])
FTP_DIR = sep.join(["C:","Files for FTP Transfer"])

def mkuser(user,passwd):
	USERMOD = sep.join(["C:","iFtpSvc","iFtpAddU.exe"])
	return call([USERMOD,"-h","ppc-sftp01.ucsc.edu","-u",user,"-p",passwd,"-n","Dropbox","-chgpass"])

def init_db():
	db=get_standard_db()
	c=db.cursor()
	r=c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, user STRING, date STRING)")
	db.commit()
	db.close()

def get_standard_db():
	return connect(DB)

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
		return sha224(s.lower()).hexdigest()


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
	return datetime.today().strftime("%m/%d/%Y")

def log_user(s,d):
	try:
		date_rex=re.compile(r'[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{4}')
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
	users_list_save("most-recent-ftp-users.csv")
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
	try:
		r = get_standard_db().cursor().execute("SELECT * FROM users").fetchall()
	except OperationalError:
		print(">>> ERROR: Failure listing the users.  Is "+DB+" accessible?  (For a new database, you need to run INIT).")
		return None
	if r:
		t = [",".join(map(str,x)) for x in r]
		return "\n".join(t)
	else:
		return None

def users_list_save(f=None):
	if not f: f = "ftp-users_"+today_mmddyyyy().replace("/","-")+".csv"
	listing = users_list()
	if listing:
		with open(SAVPATH+sep+f,'w') as file: file.write(listing)
		return "Written to: "+SAVPATH+sep+f
	else:
		return None

def user_and_date_by_id(id):
	try:
		r = get_standard_db().cursor().execute("SELECT user,date FROM users WHERE id=?",(id,)).fetchone()
	except OperationalError:
		print(">>> ERROR: Failure to fetch the user!  Is "+DB+" accessible?  (For a new database, you need to run INIT).")
		return None
	if r:
		return " ".join(r)
	else:
		return None

def dropbox():
	# The username will be based on the date and time.
	#  Compute it
	print(" > Computing login credentials...")
	now_day = today_mmddyyyy().replace("/","")[:-4] #mmddyyyy -> mmdd
	now = datetime.today()
	now_minute = 60*now.hour + now.minute

	# Set the username and path
	id = str(now_day) + "-" + str(now_minute)
 	user = "d" + id	
	path = "$" + id

	# Create the user on the FTP site.  If this fails (returns a value that is not zero), don't do anything more
	print(" > Attempting to add user to FTP server...")
	try:
		if mkuser(user,check_pass(user)):
			print(">>> ERROR: Failed to make the new dropbox user.  Remember that the dropbox command must be run on the FTP server.  Aborting.")
			return "failed"
	except WindowsError:
			print(">>> ERROR: Failed to make the new dropbox user.  Remember that the dropbox command must be run on the FTP server.  Aborting.")
			return "failed"
	# If it doesn't fail, commit the user to the database
	print(" > Committing user to the database...")
	mkpass(user)

	# Perform the file copy
	print(" > Copying files from dropbox (" +DROPBOX_DIR+ ").  If there are a lot of files, this could take a few minutes...")
	copytree(DROPBOX_DIR, FTP_DIR + sep + path)

	# Generate the email text
	email_save = DROPBOX_DIR + sep + "_" + user + "-ftp.txt"
	print(" > Generating email text... (will be written to: " + email_save + ")")
	email = email_text(user, None, None, email_save)

	print(" > DONE!\n\n\n")
	return email


def email_text(user,date=None,path=None,save=None,template="dropbox-email.txt"):
	t_dict = {}
	dropbox_rex = re.compile(r'd[0-9]{4}-[0-9]{1,4}')

	t_dict["host"] = "ppc-sftp01.ucsc.edu"
	t_dict["user"] = user
	t_dict["pass"] = check_pass(user,date)
	t_dict["password"] = t_dict["pass"]

	if not path: 
		if dropbox_rex.match(user):
			t_dict["path"] = user.replace("d","$")
		else:
			t_dict["path"] = ""
	else:
		t_dict["path"] = path
	
	t_dict["url"] = quote("ftp://%(user)s@%(host)s/%(path)s" % t_dict,  "$:/?=-@_&")

	with open(template) as f:  t = "".join(f.readlines())
	template_substitute_rex = r'\[\[([A-Za-z0-9]+)\]\]'
	email = re.sub(template_substitute_rex, r'%(\1)s', t) % t_dict

	if save:
		with open(save,'w') as f: f.writelines(email)
	
	return email
		









def command_list(brief=False):
	ctxt = []
	cmds = [(v,CMD[v]) for v in CMD.keys() if v[0] != "_"]
	cmds = sorted(cmds, lambda y,x: cmp(x[1][4],y[1][4]))
	for (name,(f,args,optargs,desc,priority)) in cmds:
		args = " ".join(["<"+a+">" for a in args])
		optargs = " ".join(["["+a+"]" for a in optargs])
		if brief:
			txt = "%s %s %s" % (name,args,optargs)
		else:
			txt = "%s %s %s\n  - %s\n\n" % (name,args,optargs,desc)
		ctxt.append(txt)
	return "\n".join(ctxt)

def exitp():
	return sys.exit(0)

def reset():
	db=get_standard_db()
	c=db.cursor()
	r=c.execute("DROP TABLE users")
	db.commit()
	db.close()
	init_db()

CMD = { \
        "ckpass":(check_pass,["user"],["date"],"Given a user (and optionally a date), display the password that would be assigned",5)
      , "mkpass":(mkpass,["user"],[],"Make a new password for the user, and save it to the database",5)
      , "list":(users_list,[],[],"Lists all the users that have been added to the database, as well as the dates they were added",4)
      , "list-save":(users_list_save,[],["filename"],"Saves the user list from the \'list\' command to a file at "+SAVPATH+".  The filename is automatically generated unless overridden with the optional [filename] argument",3)
      , "commands":(command_list,[],[],"List the commands available",1)
      , "init":(init_db,[],[],"Initializes the database",0)
      , "exit":(exitp,[],[],"Exits the command prompt",0)
      , "dropbox":(dropbox,[],[],"Processes files that have been placed in the dropbox (at "+DROPBOX_DIR+").  This command must be run on the FTP server",3)
      , "email":(email_text,["user"],["user-date","path","save-path","template"],"Generates the email text for a particular user.  Optionally set the date the user was created, the path on the FTP server, where to save a hardcopy (if desired - None for no hardcopy), and the template used to generate the email.",3)
      , "_reset":(reset,[],[],"")
      }



def run_command(cmd,args=[]):
	print("---")
	c = cmd.lower()
	if not c: run_command("exit")
	if c in CMD.keys() and len(args) >= len(CMD[c][1]):
		print(apply( CMD[cmd.lower()][0], args ))
		print("")
		r=raw_input("")
	else:
		print(">>> ERROR: Invalid command, or incorrect usage.  Valid commands are:")
		run_command("commands")

def interpolate_users(st):
	sub_rex = re.compile(r'##([0-9]+)')
	interpolations = sub_rex.findall(st)
	transfer = zip(interpolations,[user_and_date_by_id(i) for i in interpolations])
	modified_st = reduce(lambda s,t: s.replace("##"+str(t[0]),str(t[1])), transfer, st)
	return modified_st

def run_prompt():
	print("### Enter any of the following commands:")
	print(command_list(brief=True))
	print("")
    	craw1=raw_input("### Command: ")
	craw2=interpolate_users(craw1)
	if craw1 != craw2:
		print(" > " + craw2)
	c=craw2.split()
	if len(c) < 1:
		run_command("exit")
	else:
		run_command(c[0],c[1:])


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
