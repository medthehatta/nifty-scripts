import re
import os
from math import *
import subprocess
import time
import shutil

home_dir="/home/med"
icon_dir=home_dir+"/scripts/icons"

#shameless hack to try and get the battery to work more accurately
#(basically going to track all the rate measurements in a global variable
# and average them)
rate=[]



def cmd(cmdlist):
	if not cmdlist: return None

	pipeline = reduce( \
		lambda last, command: subprocess.Popen(command ,\
			stdin=last.stdout,stdout=subprocess.PIPE) ,\
		cmdlist ,\
		subprocess.Popen("echo"))

	return pipeline.communicate()[0]


def volume_level():
	raw = cmd([["amixer","sget","Master"]])
	rex = re.compile(r'\[([^\[\]\s]+)%\].*\[[^\[\]\s]+\].*\[([^\[\]\s]+)\]')
	(v,m) = rex.search(raw).groups()
	return (int(v),m=='on')


def date():
	return cmd([["date","+%d %b (%a) %I:%M %p"]]).strip()


def battery_remaining():
	raw = open("/proc/acpi/battery/BAT0/state").readlines()

	rex = re.compile(r'\s+(.*)\n')
	(P,C,S,R,L,V) =\
		[rex.search(a).groups()[0] for a in raw if a]

	rate.append(float(re.search(r'([0-9]+)',R).groups()[0]))
	leftH = float(re.search(r'([0-9]+)',L).groups()[0])

	state = re.search(r'(charged|discharging|charging)',S).groups()[0]

	rateA = sum(rate)/float(len(rate))

	if rateA == 0: 
		timeleft = 0
	else:
		timeleft = leftH / rateA
	
	return (state,100*leftH/5053.,floor(timeleft),floor(60*(timeleft-floor(timeleft))))


def irssi_notifications():
	raw = open("/tmp/med_irssi_pipe").readlines()
	return [r.split("\t") for r in raw]


def new_mail():
	mail_dir=home_dir+"/mail"
	def count_instances(rex,mailbox): 
		return int(cmd([["grep",rex,mail_dir+"/"+mailbox],["wc","-l"]]).strip())
	
	mailboxes={}
	for mailbox in [f for f in os.listdir(mail_dir) if "IN-" in f]:
		mailboxes[mailbox] = \
		count_instances("^From:",mailbox) \
		- count_instances("^Status:",mailbox)
	
	return mailboxes


def wifi_online():
	nic="eth0"
	wifi="wlan0"
	rex = re.compile(r'inet addr:([^\ ]*)')
	raw_nic = cmd([["ifconfig",nic]]).strip()
	raw_wifi = cmd([["ifconfig",wifi]]).strip()
	m_nic = rex.search(raw_nic)
	m_wifi = rex.search(raw_wifi)
	if m_nic: return (0,m_nic.groups()[0])
	if m_wifi: return (1,m_wifi.groups()[0])
	if not (m_nic or m_wifi): return None

def time_to_minutes(s):
	sp = map(int, reversed( s.split(":") ))
	return sp[0] + sum( [60*a for a in sp[1:]] )

def xmms2_status():
	rex = re.compile(r'([A-Za-z]+): (.+): ([0-9]+:[0-9]+) of ([0-9]+:[0-9]+)')
	raw = cmd([["nyxmms2","status"]]).strip()
	m = rex.search(raw)
	if m: 
		(status,song,current,final) = m.groups()
		duration = time_to_minutes(final)
		progress = time_to_minutes(current)
		return (status,song,progress,duration)
	return None

##################################
# FUNCTIONS FOR PRINTING TO DZEN #
##################################

def pbar(pct,color="green"):
	filled = floor(pct/2.)	
	unfilled = 50-filled
	return "^fg(%s)^r(%sx6)^fg(white)^r(%sx6)" % (color,str(filled),str(unfilled))


def statusbar_item(num,data):
	return str(num)+" ^p(+5)^fg()| "+data
def clear_item(num):
	return str(num)+" "

def i(icon,color=""):
	if color:
		return "^fg(%s)^i(%s/%s)^fg()" % (color,icon_dir,icon+".xbm")
	else:
		return "^i(%s/%s)" % (icon_dir,icon+".xbm")


def dzen_write(data):
	f=open("/tmp/med-status",'w')
	print >> f, data
	f.close()
	return data
	

def dzen_go(items):
	names={}
	interval={}
	ordering={}
	counter=0
	ord = [a[0] for a in items]
	for a in items:	names[a[0]]=a[1]
	for a in items: interval[a[0]]=a[2]
	maxcounter=1+max(interval.values())
	for k in zip(range(0,len(ord)),ord): ordering[k[1]]=k[0]

	# First run
	for a in names:
		dzen_write(statusbar_item(ordering[a],apply(names[a])))

	# Run at specified intervals
	while 1==1:
		time.sleep(1)
		counter = (counter+1) % maxcounter
		update_keys = [k for k in interval if counter%interval[k] == 0]
		for i in update_keys:
			dzen_write(statusbar_item(ordering[i],apply(names[i])))


def dzen_stop():
	for a in range(0,20):
		dzen_write(clear_item(str(a)))


def dz_battery():
	(state,percent,hours,minutes) = battery_remaining()
	if state == "discharging":
		if percent >= 0: color = "red"
		if percent > 25: color = "yellow"
		if percent > 50: color = "green"
		
		return i("bat_empty_01","white")+" "+pbar(percent,color)+" %02d%% (%02d:%02d)"%(int(percent),int(hours),int(minutes))
	if state == "charging":	
		return i("ac","")+" "+pbar(percent,"black")+" %02d%% (--:--)" % (int(percent),)
	if state == "charged":
		return i("ac","green")+" "+pbar(percent,"green")+" %02d%% (--:--)" % (int(percent),)

def dz_wifi():
	r = wifi_online()
	if r: 
		if r[0]==0: return i("net_wired","green")+"^fg(white) "+r[1]
		if r[0]==1: return i("wifi_02","green")+"^fg(white) "+r[1]
	else:
		return "offline"


def dz_volume():
	(percent,on) = volume_level() 
	if on:
		if percent >= 0: color = "green"
		if percent > 42: color = "blue"
		if percent > 80: color = "red"
		
		return i("spkr_01","green")+" "+pbar(percent,color)
	else:
		return i("spkr_01","")+" "+pbar(percent,"") 


def dz_date():
	return "     "+date()


def dz_mail():
	mb = new_mail()
	abbrevs={"IN-facebook":"fb","IN-inbox":"in","IN-testing":"x","IN-monster":"jb"}
	boxes = ["^fg("+((not not mb[k])*"white")+")"+abbrevs[k]+"-"+str(mb[k]) for k in sorted(mb) if k in abbrevs and mb[k]]
	if filter(lambda x: x>0, mb.values()):
		color="green"
		if boxes:
			boxdisp=" "+"^p(+2)".join(boxes)
		else:
			boxdisp=""
	else:
		color=""
		boxdisp=""
	return i("mail",color)+boxdisp

def dz_downloaded():
	numfiles = len(os.listdir(home_dir+"/downloaded"))
	movedfiles = len([f for f in os.listdir(home_dir+"/downloaded") if re.match(r'.*\.moved$',f)])
	if numfiles > 0:
		if numfiles < 10: 
			color = "blue"
		else:
			color = "red"
		
		return i("diskette",color)+" "+str(numfiles-movedfiles)+"/"+str(numfiles)
	else:
		if movedfiles == 0:
			return i("diskette","")
		else:
			return i("diskette","white")

def dz_xmms2():
	r = xmms2_status()
	if not r: return i("note","")

	if r[0] == "Playing":
		color = "green"
		color2 = "white"
	elif r[0] == "Stopped":
		color = ""
		color2 = ""
	else:
		color = "white"
		color2 = ""

	percent = int(r[2]/float(r[3])*100)
	progress = 4 - int(percent / 25)

	return i("note",color) +" ^fg("+color2+")"+ r[1] + " " + progress*"." + (4-progress)*" "



ITEMS=[("xmms2",dz_xmms2,3),("mail",dz_mail,60), ("vol",dz_volume,3), ("wifi",dz_wifi,30), ("batt",dz_battery,30), ("date",dz_date,30)]

dzen_go(ITEMS)
