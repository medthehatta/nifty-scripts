#!/usr/bin/python
import re
import sys
import os
import subprocess
from optparse import OptionParser

multi_image_rex = re.compile(r'(.*)/([^\/]*)[0-9]+([a-zA-Z\-]*\.(jpg|jpeg|png))')

def match_string(rex,string):
	m = rex.search(string)	
	if m:
		return m.groups()
	else:
		return None

def fetch_command(cmd,args,url):
	return [cmd] + args + [url]

def wget_fetch(url,dir="."):
	return fetch_command("wget",["-q","-P",dir],url)

def assemble_image_rex_template(matchgroups):
	if not matchgroups: return ""
	(path,first,end,ext) = matchgroups
	return path.replace("%","\\%")+"/"+first+"%s"+end

def make_template_from_url(url):
	return assemble_image_rex_template( match_string(multi_image_rex,url) )

def populate_template(template,num,padlen):
	return template % (str(num).zfill(padlen),)

def main(argv):
	p = OptionParser()	

	p.add_option("-p","--pad-zeros","--pad-zeroes",type="int",dest="padLen",default=1,help="pad numbers with this many zeros")
	p.add_option("-P","--pad-upper",action="store_true",dest="padUpper",help="pad numbers using the upper bound size (use in conjunction with -u or --upper-bound")
	p.add_option("-l","--lower-bound","--lowerbound",type="int",dest="lBound",default=0,help="start counting from this number")
	p.add_option("-u","--upper-bound","--upperbound",type="int",dest="uBound",default=10,help="stop counting at this number")
	p.add_option("-0","--no-break-on-fail","--no-break",action="store_true",dest="noBreakOnFail",help="do not break when the download fails")
	p.add_option("-d","--output-dir","--prefix",dest="prefix",default=os.getcwd(),help="sets the default save directory")

	opts, args = p.parse_args(argv)
	rest = " ".join(args)

	template = make_template_from_url(rest)
	print("Using template: %s" % (template,))
	print("Looping from: %d to %d..." % (opts.lBound,opts.uBound))
	for i in range(opts.lBound,opts.uBound+1):
		if opts.padUpper:
			fillLen = len(str(opts.uBound))
		else:
			fillLen = opts.padLen
		this_url = template % (str(i).zfill(fillLen),)
		print(this_url)
		r = subprocess.call( wget_fetch(this_url,opts.prefix) )
		if (not opts.noBreakOnFail) and r!=0: break


if __name__=="__main__":
	main(sys.argv[1:])


