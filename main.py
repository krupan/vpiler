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
    try:
        # handle newline
        if code[position] == '\n':
            line += 1
            position+=1

        # handle whitespace
        while code[position] in string.whitespace:
            position += 1

        # handle punctuation
        if code[position] in ';()':
            position+= 1
            print(f'>{code[position-1]}<')
            return position, line

        # handle string constants
        if code[position] == '"':
            string_start = position
            position += 1
            # look for quotes to end string, but not if they are preceded by a \
            while code[position] != '"':
                if code[position] == '\\':
                    position += 2
                else:
                    position += 1
            position += 1
            print(f'>{code[string_start:position]}<')
            return position, line

        # handle identifiers
        if(code[position] in (string.ascii_letters + '_' + '$')):
            token_start = position
            position += 1
            while(code[position] in (string.ascii_letters + string.digits + '_')):
                position += 1
            print(f'>{code[token_start:position]}<')
            return position, line
    # If any of the above position += 1 take us past the end of code,
    # this will save us.  Some would argue this is an improper use of
    # exceptions.
    except IndexError as err:
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
