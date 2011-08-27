#!/usr/bin/python2

import shutil,os
import re
from subprocess import call


#############################
## CONFIGURATION VARIABLES ##
#############################
GSHARKDOWN_CONFIG="~/.gsharkdown/gsharkdown.ini"
MUSIC_DIRECTORY="~/music"
GSHARKDOWN="gsharkdown"
PLAYER_QUEUE_CMD="nyxmms2 add"




##########################
## CODE PAST THIS POINT ##
##########################

# Translate configuration variables
gsharkdown_cmd=GSHARKDOWN.split(" ")
GSHARKDOWN_CONFIG_FILE = os.path.expanduser(GSHARKDOWN_CONFIG)
MUSIC_DIR=os.path.expanduser(MUSIC_DIRECTORY)

def copy_and_add(TMP_MUSIC_DIR,MUSIC_DIR,queuecmd):
	"""Copy files to the actual music directory and then add them"""

	# Copy files to the actual music directory, and then add them
	for f in os.listdir(TMP_MUSIC_DIR):
		shutil.copy( os.path.join(TMP_MUSIC_DIR,f),os.path.join(MUSIC_DIR,f) )
		if not call(queuecmd.split(" ")+[os.path.join(MUSIC_DIR,f)]):
			print "Added %s" % f

	# Check to make sure the files made it, and then remove the temps
	for f in os.listdir(TMP_MUSIC_DIR):
		if os.path.isfile( os.path.join(MUSIC_DIR,f) ):
			os.remove( os.path.join(TMP_MUSIC_DIR,f) )
		else:
			print "$s did not copy correctly!" % f

def gsharkdown_dl_dir(GSHARKDOWN_CONFIG_FILE):
	""" Fetch the temporary music dir from the gsharkdown config"""
	gsharkdown_cfg = {}
	with open(GSHARKDOWN_CONFIG_FILE) as f:
		for l in f:
			(k,v) = re.split(r'\s*=\s*',l.strip())
			gsharkdown_cfg[k]=v
	return gsharkdown_cfg["down_path"]


def main():
	TMP_MUSIC_DIR = gsharkdown_dl_dir(GSHARKDOWN_CONFIG_FILE)
	print "gsharkdown download directory is: %s" % TMP_MUSIC_DIR
	# Open gsharkdown, and wait for me to finish using it
	#  Downloaded files will be saved to TMP_MUSIC_DIR
	call(gsharkdown_cmd)
	# Copy the downloaded files to the actual music dir
	#  and enqueue them in xmms2
	copy_and_add(TMP_MUSIC_DIR,MUSIC_DIR,PLAYER_QUEUE_CMD)

# Entry point
main()

