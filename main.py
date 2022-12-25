#!/usr/bin/env python
import argparse
import pathlib
import string
import sys


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-v', '--verbose', action='store_true')
    return parser.parse_args()


def next_token(code, position, line):
    if code[position] == '\n':
        line += 1
        position+=1

    while code[position] in string.whitespace:
        position += 1

    if code[position] == ';':
        position+= 1
        print(';')
        return position, line

    if(code[position] in (string.ascii_letters + '_' + '$')):
        token_start = position
        position += 1
        while(code[position] in (string.ascii_letters + string.digits + '_')):
            position += 1
        print(code[token_start: position])
        return position, line


def main(args):
    keywords = ['begin',
                'end',
                'module',
                'endmodule',
                'initial',]
    built_in = ['$display']
    sv_code = ''
    position = 0
    line = 1
    with open(args.filename) as sv_file:
        sv_code = sv_file.read()
    while position < len(sv_code):
        position, line = next_token(sv_code, position, line)
    return 0


if __name__ == '__main__':
    sys.exit(main(parse_args()))
