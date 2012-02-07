#!/usr/bin/python

import os, os.path
import stat
import shutil
import subprocess
import sys
from optparse import OptionParser

def doit(pdfname,semid,hwnum,title,abbrev,hwdesc,base):
	base = os.path.expanduser(base)

	# Make the directory and change in
	path = os.path.join(base,abbrev,'homework','{:02d}'.format(hwnum))
	os.makedirs(path)
	os.chdir(path)

	# Make hwdef.tex
	template = r'\newcommand{\hwAssignment}{CLASSTITLE: Homework \#NUM}' + "\n"
	template = template + r'\newcommand{\hwAuthor}{Med Mahmoud}' + "\n"
	hwdef = template.replace('CLASSTITLE',title).replace('NUM',str(hwnum))
	with open("hwdef.tex",'w') as f: f.writelines(hwdef)

	# Make empty rst
	template = "\n".join( [r'.. default-role:: math',r'.. role:: bib',r'.. role:: references'] )
	with open(abbrev.lower()+str(hwnum)+".rst",'w') as f: f.write(template)

	# Make scp upload script
	template = "#!/bin/bash\nscp {} $tussh:$tuwork/{}\n"
	upload = template.format(pdfname,semid)
	with open("upload",'w') as f: f.writelines(upload)
	os.chmod("upload",504)

	# Make view script
	template = "#!/bin/bash\n{} {} && {} {}\n\n"
	view = template.format('/home/med/scripts/hw-builder.sh'
				,os.path.join(path,abbrev.lower()+str(hwnum)+".rst")
				,'mupdf'
				,os.path.join(path,pdfname))
	with open("view",'w') as f: f.writelines(view)
	os.chmod("view",504)

	# Add link to coursework
	tussh = "tud48344@astro.temple.edu"
	tuhome = "/usr/home/c/141/tud48344"
	#  download
	subprocess.call(['scp',tussh+":"+tuhome+"/public_html/coursework.htm",'.'])
	contents = "".join(open("coursework.htm").readlines())
	placeholder = "<!-- {}.{} --!>".format(semid,abbrev.upper())
	template = '<li> <a href="work/{}/{}">Homework {}</a> - {} </li>'.format(semid,pdfname,str(hwnum),hwdesc)
	#  modify
	contents = contents.replace(placeholder,template+"\n"+placeholder)
	with open("coursework.htm",'w') as f: f.write(contents)
	#  upload
	subprocess.call(['scp','coursework.htm',tussh+":"+tuhome+"/public_html"])
	#  remove local copy
	os.remove("coursework.htm")
	# Output the directory
	print(path)


def main(argv):

	# === Option Parsing ===
	p = OptionParser()	

	#def doit(pdfname,semid,hwnum,title,abbrev,hwdesc,base):
	p.add_option("-c","--course",dest="abbrev",default="",help="course abbreviation")
	p.add_option("-d","--description","--desc",dest="hwdesc",default="",help="brief description of the assignment")
	p.add_option("--pdf-name",dest="pdfname",default="",help="what to name the pdf.  (default: med-xx#.pdf)")
	p.add_option("-n","--hw-number",dest="hwnum",type="int",default=0,help="ovveride the homework number")
	p.add_option("--course-title",dest="title",default="",help="alternate course title")
	p.add_option("-s","--semester",dest="semid",default="02-spring2012",help="semester id.  (default: 02-spring2012)")
	p.add_option("-p","--prefix",dest="base",default="/home/med/class/grad/",help="base directory for course data.  (default: ~/class/grad)")

	(opts,args) = p.parse_args(argv)
	rest = " ".join(args)
	# === End Option Parsing ===

	if not opts.abbrev:
		print("You need to give me something to work with, here")
		return -1

	if opts.hwnum < 1:
		if os.path.isdir(os.path.join(opts.base,opts.abbrev,"homework")):
			hwnum = 1 + max( map(int,os.listdir(os.path.join(opts.base,opts.abbrev,"homework"))) )
		else:
			hwnum = 1
	else:
		hwnum = opts.hwnum

	if not opts.pdfname: 
		pdfname = "med-{}{}.pdf".format(opts.abbrev,hwnum)
	else:
		pdfname = opts.pdfname

	if not opts.title:
		title = {'tb':"Tissue Biomechanics", 'afd':"Fluid Dynamics", 'fe':"FEA"}[opts.abbrev.lower()]
	else:
		title = opts.title

	if not opts.hwdesc:
		if rest.count(" ")==len(rest):
			hwdesc = "(No description)"
		else:
			hwdesc = rest
	else:
		hwdesc = opts.hwdesc

	#DOIT
	doit(pdfname,opts.semid,hwnum,title,opts.abbrev,hwdesc,opts.base)	

if __name__=="__main__":
	main(sys.argv[1:])

