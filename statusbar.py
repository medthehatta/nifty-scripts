import re
import os
from math import *
import subprocess
import time
import datetime
import shutil
from functools import *
import septa

home_dir="/home/med"
mail_dir=home_dir+"/mail"
icon_dir=home_dir+"/scripts/icons"

def cmd(c):
	return subprocess.Popen(c,shell=False,stdout=subprocess.PIPE).communicate()[0].decode()

def volume_level():
	raw = cmd(["amixer","sget","Master"])
	rex = re.compile(r'\[([^\[\]\s]+)%\].*\[[^\[\]\s]+\].*\[([^\[\]\s]+)\]')
	(v,m) = rex.search(raw).groups()
	return (int(v),m=='on')


def date():
	return cmd(["date","+%d %b (%a) %I:%M %p"])


def battery_remaining():
  raw = cmd(["acpitool","-B"])

  percent_p = re.search(r'Remaining.*, ([0-9\.]+)%',raw)
  time_p = re.search(r'Remaining.*([0-9]+:[0-9]+):[0-9]+',raw)
  state_p = re.search(r'Charging state.*(Full|Discharging|Unknown|Charging)',raw)

  if time_p:
    time = time_p.groups()[0]
  else:
    time = None

  if percent_p:
    percent = float(percent_p.groups()[0])
  else:
    percent = None

  if state_p:
    state = state_p.groups()[0]
  else:
    state = None

  return (state,percent,time)


def irssi_notifications():
	raw = open("/tmp/med_irssi_pipe").readlines()
	return [r.split("\t") for r in raw]


def instances(rex,mailbox): 
	return cmd(["grep",rex,mail_dir+"/"+mailbox])
def count_instances(rex,mailbox):
	return len( instances(rex,mailbox).split("\n") )

def new_mail():
	mailboxes={}
	for mailbox in [f for f in os.listdir(mail_dir) if "IN-" in f]:
		mailboxes[mailbox] = \
		count_instances("^From:",mailbox) \
		- count_instances("^Status:",mailbox)
	
	return mailboxes


def wifi_online():
	nic="enp1s0"
	wifi="wlp2s0"
	tether="enp0s"
	rex = re.compile(r'inet ([^\ ]*)')
	raw_nic = cmd(["ip","addr","show","dev",nic])
	raw_wifi = cmd(["ip","addr","show","dev",wifi])
	raw_et = cmd(["ip","addr","show","dev",tether])
	m_nic = rex.search(raw_nic)
	m_wifi = rex.search(raw_wifi)
	m_et = rex.search(raw_et)
	if m_nic: return (0,m_nic.groups()[0])
	if m_wifi: return (1,m_wifi.groups()[0])
	if m_et: return (2,m_et.groups()[0])
	if not (m_nic or m_wifi or m_et): return None

def time_to_minutes(s):
	sp = [int(a) for a in reversed( s.split(":") )]
	return sp[0] + sum( [60*a for a in sp[1:]] )

def xmms2_status():
	rex = re.compile(r'([A-Za-z]+): (.+): ([0-9]+:[0-9]+) of ([0-9]+:[0-9]+)')
	raw = cmd(["nyxmms2","current"])
	m = rex.search(raw)
	if m: 
		(status,song,current,final) = m.groups()
		duration = time_to_minutes(final)
		progress = time_to_minutes(current)
		return (status,song,progress,duration)
	return None

def time_diff(t1,t2):
	ts1 = [int(t) for t in t1.split(":")]
	ts2 = [int(t) for t in t2.split(":")]
	tsp1 = 60*ts1[0]+ts1[1] 
	tsp2 = 60*ts2[0]+ts2[1] 
	return tsp1-tsp2

def next_prayer():
	prayers = ["Fajr","Shorooq","Zuhr","Asr","Maghrib","Isha"]
	times_line = cmd(["ipraytime","-b"]).strip().split("\n")[-1]
	times = re.sub(r'\ +',r' ',times_line).split(" ")
	now = datetime.datetime.today().strftime("%H:%M")
	deltas = [time_diff(a,now) for a in times[2:]]
	data = zip(prayers,times[2:],deltas)
	next = [d for d in data if d[2]>0]

	if next:
		return next[0]
	else:
		return None

def usb_present():
  mounts = cmd(["mount"]).strip().split("\n")
  usbs   = [a for a in mounts if 'usb' in a]
  return len(usbs)


##################################
# FUNCTIONS FOR PRINTING TO DZEN #
##################################

def pbar(pct,color="green"):
	filled = floor(pct/2.)	
	unfilled = 50-filled
	return "^fg({0})^r({1}x6)^fg(white)^r({2}x6)".format(color,str(filled),str(unfilled))


def statusbar_item(num,data):
	return str(num)+" ^p(+5)^fg()| "+data.strip()+"\n"
def clear_item(num):
	return str(num)+" "

def i(icon,color=""):
	if color:
		return "^fg({0})^i({1}/{2})^fg()".format(color,icon_dir,icon+".xbm")
	else:
		return "^i({0}/{1})".format(icon_dir,icon+".xbm")


def dzen_write(data):
	f=open("/tmp/med-status",'w')
	f.writelines(data)
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
		dzen_write(statusbar_item(ordering[a],names[a]()))

	# Run at specified intervals
	while 1==1:
		time.sleep(1)
		counter = (counter+1) % maxcounter
		update_keys = [k for k in interval if counter%interval[k] == 0]
		for i in update_keys:
			dzen_write(statusbar_item(ordering[i],names[i]()))


def dzen_stop():
	for a in range(0,20):
		dzen_write(clear_item(str(a)))


def dz_battery():
	(state,percent,time) = battery_remaining()
	if state == "Discharging":
		if percent >= 0: color = "red"
		if percent > 25: color = "yellow"
		if percent > 50: color = "green"
		return i("bat_empty_01","white")+" "+pbar(percent,color)+" {0}% ({1})".format(int(percent),time)
	if state == "Unknown" or state == "Charging":	
		if percent > 95:
			return i("ac","")+" {0}%".format(int(percent),)
		else:
			return i("ac","")+" "+pbar(percent,"black")+" {0}% (--:--)".format(int(percent))
	if state == "Full":
		return i("ac","")+" {0}%".format(int(percent))


def dz_wifi():
	r = wifi_online()
	if r: 
		if r[0]==0: return i("net_wired","green")+"^fg(white) "+r[1]
		if r[0]==1: return i("wifi_02","green")+"^fg(white) "+r[1]
		if r[0]==2: return i("usb_02","green")+"^fg(white) "+r[1]
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


def dz_usb():
  count = usb_present()
  if count:
    return i("usb","green")+" {0}".format(count)
  else:
    return i("usb","")

def dz_mail():
	mb = new_mail()
	abbrevs={"IN-facebook":"fb","IN-inbox":"in","IN-testing":"x","IN-monster":"jb","IN-temple":"tu"}
	boxes = ["^fg("+((not not mb[k])*"white")+")"+abbrevs[k]+"-"+str(mb[k]) for k in sorted(mb) if k in abbrevs and mb[k]]
	nonzero = [b for b in mb.keys() if mb[b]>0]
	if [b for b in mb.keys() if mb[b]>0]:

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
		return i("note","")
	else:
		color = "white"
		color2 = ""

	percent = int(r[2]/float(r[3])*100)
	progress = 4 - int(percent / 25)

	return i("note",color) +" ^fg("+color2+")"+ r[1] + " " + progress*"." + (4-progress)*" "

def dz_prayer():
	raw = next_prayer()
	if not raw: return i("clock","")
	#else
	if len(raw) != 3: return i("clock","")
	#else again
	(prayer,time,delta) = raw
	if delta < 15:
		icolor="green"
		color="green"
	elif delta < 30:
		icolor = "white"
		color = "white"
	elif delta  < 60:
		icolor = "white"
		color = ""
	else:
		icolor = ""
		color = ""

	return i("clock",icolor) + "^fg({0}) {1} - {2} ({3}m)".format(color,prayer.strip(),time.strip(),delta)

def dz_suspend_lock():
        if is_suspend_locked():
                return i("stop","green")
        else:
                return i("stop","")

def dz_septa():
  #lines = ["Chestnut Hill East", "Chestnut Hill West", "Ambler", "Conshohocken", "Main St"]
  #lines = ["Chestnut Hill East"]
  lines = [l.strip() for l in open("/home/med/scripts/septastop").readlines() if l.strip()]
  out = ""
  for l in lines:
    (line,leave,arrive,timing) = septa.get_next("Temple U",l)[0]
    now = datetime.datetime.today().strftime("%H:%M")
    then = datetime.datetime.strptime(leave,"%I:%M%p").strftime("%H:%M")
    dt = time_diff(then,now)
    if dt < 15:
      color = "green"
    elif dt < 30:
      color = "white"
    else:
      color = ""
    if timing=="On time":
      out+="^fg({0})[{6}]  {1}  {2}  {3}  ({5} mins)\n".format(color,line,leave,arrive,timing,dt,l)
    else:
      out+="^fg({0})[{6}]  {1}  {2}  {3}  ({5}+{4})\n".format(color,line,leave,arrive,timing,dt,l)
  return out

if __name__ == "__main__":
	ITEMS=[("usb",dz_usb,60),("prayer",dz_prayer,120),("vol",dz_volume,5),("wifi",dz_wifi,60),("batt",dz_battery,60),("date",dz_date,50)]
	dzen_go(ITEMS)



