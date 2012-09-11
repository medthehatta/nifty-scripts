#!/usr/bin/python

import os, os.path, sys
from subprocess import Popen,PIPE

PREFIX = '/home/med'
BOXEN  = {'.dropbox1':'academic', '.dropbox2':'personal'}

def read_dropbox(boxhome,cmd):
  p = Popen(['dropbox']+cmd,
            env={'HOME':boxhome},shell=False,stdout=PIPE)
  ret = p.communicate()[0].decode('utf-8')
  if ret:
    return ret
  else:
    return None

def direxpand(rpth):
  return os.path.join(PREFIX,rpth)

def histogram(pairs):
  d={}
  for (k,v) in pairs:
    if d.get(v):
      d[v].append(k)
    else:
      d[v]=[k]
  return d

def print_rethist(histo):
  if histo:
    for k in histo:
      vs = ", ".join(histo[k])
      if k and k.count("\n")>1:
        print(vs+":\n"+k.strip())
      else:
        try:
          print("{0}: {1}".format(vs,k.strip()))
        except AttributeError:
          print("{0}: {1}".format(vs,"-- no output --"))
          
  
def dropbox_call(cmds):
  outputs = [(BOXEN[k],read_dropbox(direxpand(k),cmds)) for k in BOXEN]
  print_rethist(histogram(outputs))
  return 0



if __name__ == '__main__':
  dropbox_call(sys.argv[1:])

