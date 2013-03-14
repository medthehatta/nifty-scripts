#!/usr/bin/python
# -*- encoding: utf-8 -*-
"""
hw_builder.py

Python script for producing nicely LaTeXed file from RST.
Replaces hw-builder.sh.

Dunno why I bothered to write this.  Guess it will be easier to extend than a
bash script?
"""

import os, os.path, shutil
import argparse
import subprocess
import yaml
from docutils.core import publish_file


# Setting defaults
DEFAULT_CONFIG = '/home/med/academic/Public/tex/hw-builder.conf'

def rewrite(basename,rule,ext='pdf'):
  """Rewrite the base name.  Need more options someday."""
  return rule.format(**{'basename':basename, 'ext':ext})

def main():
  # Reads in file to process
  parser = argparse.ArgumentParser(description="Produces PDFs from RST.")
  parser.add_argument('rstfile', nargs='?', default=None, 
                      help="File to process.")
  parser.add_argument('--config','-c', default=DEFAULT_CONFIG, 
                      help="Path to alternate config file.")
  args = parser.parse_args()
  rstfile = args.rstfile
  config = args.config

  # If no file passed in, try to use the rst file in the directory
  if rstfile is None:
    candidates = [f for f in os.listdir('.') if '.rst' in f]
    if len(candidates)==1:
      rstfile = candidates[0]
    else:
      print("RST file ambiguous.  Need to specify RST file to process.")
      print(parser.print_usage())
      sys.exit(1)

  # Process the file
  if produce_file(rstfile,config):
    sys.exit()
  else:
    sys.exit(1)

def produce_file(sourcefile,CONFIG):
  # Read in config
  C = yaml.load(open(CONFIG))
  RST_WRITER_NAME = C['rst-writer']
  RST_OPTIONS = C['rst-options']
  TEX_WRITE = C['tex-writer'].split(' ')
  RENAME_RULE = C['rename-rule']

  SOURCE=os.path.expanduser(sourcefile)
  # Compute path and base name
  SRC_PATH = os.path.dirname(SOURCE)
  SRC_BASE = os.path.basename(SOURCE).replace('.rst','')

  TEX = os.path.join(SRC_PATH,SRC_BASE+'.tex')

  # Produce the LaTeX file
  publish_file(source_path=SOURCE, destination_path=TEX,
               writer_name=RST_WRITER_NAME,
               settings_overrides=RST_OPTIONS)

  # Produce the PDF file
  if subprocess.call(TEX_WRITE+[TEX])==0:
    # Rename it per the rewrite rule
    rewritten = rewrite(SRC_BASE,RENAME_RULE)
    os.rename(os.path.join(SRC_PATH,'out',SRC_BASE+'.pdf'),
              os.path.join(SRC_PATH,rewritten))
    # Move tex to out
    shutil.move(TEX, os.path.join(SRC_PATH,'out',SRC_BASE+'.tex'))
    return rewritten

  
if __name__=="__main__":
  main()


