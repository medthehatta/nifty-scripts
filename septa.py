#!/usr/bin/python
# -*- encoding: utf-8 -*-
#

import sys
import bs4
import urllib.request
import argparse


def get_next(loca,locz): 
  html  = urllib.request.urlopen("http://app.septa.org/nta/result.php?"+
                                 urllib.parse.urlencode({"loc_a":loca,
                                                         "loc_z":locz})).readall()
  nexts = [[ll.contents for ll in l.select("td")] for 
            l in bs4.BeautifulSoup(html).select("tr")]

  return [[line[0],leave[0],arrive[0],timing[0]] for
            (train,line,leave,arrive,dash,timing) in nexts[1:]]


def main(argv):

    # === Option Parsing ===
    p = argparse.ArgumentParser(description='Check the SEPTA train schedule.')	

    p.add_argument('-a','--from',dest='loc_a',default='TU',help='point of origin')
    p.add_argument('-z','--to',dest='loc_z',default='CHE',help='destination')

    args = p.parse_args(argv)
    # === End Option Parsing ===

    lookup = {'CHE':'Chestnut Hill East',
              'TU':'Temple U',
              'CHW':'Chestnut Hill West',
              'A':'Ambler',
              'CON':'Conshohocken',
              'M':'Main St',
              'NOR':'Norristown Transportation Center'
             }

    start = lookup.get(args.loc_a.upper()) or args.loc_a
    end = lookup.get(args.loc_z.upper()) or args.loc_z
    print('\n'.join(['  '.join([n for n in N]) for 
      N in get_next(start,end)]))

if __name__=='__main__':
	main(sys.argv[1:])





