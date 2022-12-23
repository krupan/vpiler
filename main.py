#!/usr/bin/env python
import pathlib
import sys
import argparse

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('filename')
  parser.add_argument('-v', '--verbose', action='store_true')
  return parser.parse_args()

def main(args):
  with open(args.filename) as sv_file:
    for line in sv_file:
      print(line.rstrip())
  return 0
  
if __name__ == '__main__':
  sys.exit(main(parse_args()))