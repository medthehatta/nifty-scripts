#!/usr/bin/python

import os
import os.path
import re
import shutil

DOWNLOAD_DIR='/home/med/downloaded'

def has_ext(e):	return r'.*\.%s$' % e

def move_downloaded(dl,mapping):
	for f in os.listdir(dl):
		matchexps = [x for x in mapping.keys() if re.match(x,f)]
		if matchexps:
			print("Moving %s to %s" % (f,mapping[matchexps[0]]))
			try:
				shutil.copyfile(dl+os.path.sep+f,mapping[matchexps[0]]+os.path.sep+f)
				shutil.move(dl+os.path.sep+f,dl+os.path.sep+f+".moved")
			except IOError:
				print("Copy failed for %s" % f)	

def main():
	move_downloaded(DOWNLOAD_DIR,FILEMAP)



FILEMAP = {has_ext("torrent"):"/mnt/smb-seed/torrents"
	  ,has_ext("(jpg|jpeg|tif|tiff|png|bmp)"):"/home/med/pics"
	  ,has_ext("gif"):"/home/med/pics/gifs"
	  }

if __name__ == "__main__":
	main()
