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


class Tokenizer:
    def __init__(self, sv_code):
        self.code = sv_code
        self.position = 0
        self.line = 1

    def next(self):
        try:
            # handle newline
            if self.code[self.position] == '\n':
                self.line += 1
                self.position+=1

            # handle whitespace
            while self.code[self.position] in string.whitespace:
                self.position += 1

            # handle punctuation
            if self.code[self.position] in ';()':
                self.position+= 1
                return self.code[self.position-1]

            # handle string constants
            if self.code[self.position] == '"':
                string_start = self.position
                self.position += 1
                # look for quotes to end string, but not if they are preceded by a \
                while self.code[self.position] != '"':
                    if self.code[self.position] == '\\':
                        self.position += 2
                    else:
                        self.position += 1
                self.position += 1
                return self.code[string_start:self.position]

            # handle identifiers
            if(self.code[self.position] in (string.ascii_letters + '_' + '$')):
                token_start = self.position
                self.position += 1
                while(self.code[self.position] in (string.ascii_letters + string.digits + '_')):
                    self.position += 1
                return self.code[token_start:self.position]
        # If any of the above position += 1 take us past the end of code,
        # this will save us.  Some would argue this is an improper use of
        # exceptions.
        except IndexError as err:
            return ''


# parser functions, see systemverilog-1800-2018.bnf that is included
# along with this code
class Parser:
    def __init__(self, filename):
        self.filename = filename
        with open(self.filename) as sv_file:
            self.code = sv_file.read()
        self.tokenizer = Tokenizer(self.code)
        self.token = ''

    def error(self, message):
        print(f'{self.filename}:{self.tokenizer.line}:{self.tokenizer.position}: error: {message}')

    def go(self):
        self.source_text()

    def source_text(self):
        self.token = self.tokenizer.next()
        while self.token != '':
            self.description():

    def description(self):
        self.module_declaration()

    def module_declaration(self):
        self.token = self.tokenizer.next()
        self.module_ansi_header()
        self.token = self.tokenizer.next()
        self.non_port_module_item()
        self.token = self.tokenizer.next()
        if self.token != 'endmodule':
            self.error("expected 'endmodule'")

    def module_ansi_header(self):
        self.token = self.tokenizer.next()
        if self.token != 'module':
            self.error("expected 'module'")
        self.token = self.tokenizer.next()
        self.module_identifer()
        self.token = self.tokenizer.next()
        if self.token != ';':
            self.error("expected ';'")

    def non_port_module_item(self):
        # WIP TODO
        pass
        


def main(args):
    keywords = ['begin',
                'end',
                'module',
                'endmodule',
                'initial',]
    built_in = ['$display']
    parser = Parser(args.filename)
    parser.go()
    return 0


if __name__ == '__main__':
    sys.exit(main(parse_args()))
