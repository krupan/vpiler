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
  if args.verbose:
    print (sys.argv[0])
  else:
    print('nothing to say')
  return 0
  
if __name__ == '__main__':
  sys.exit(main(parse_args()))