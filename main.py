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
# along with this code to see where these methods and their names come
# from
#
# TODO: I think this would all be more clear to me if the token that's
# being looked at was passed to each function.
class Parser:
    def __init__(self, filename):
        self.filename = filename
        with open(self.filename) as sv_file:
            self.code = sv_file.read()
        self.tokenizer = Tokenizer(self.code) 

    def next_token(self):
        return self.tokenizer.next()

    def error(self, message):
        print(f'{self.filename}:{self.tokenizer.line}:{self.tokenizer.position}: error: {message}')

    def go(self):
        self.source_text()

    def source_text(self):
        token = self.next_token()
        while token != '':
            self.description(token)
            token = self.next_token()

    def description(self, token):
        self.module_declaration(token)

    def module_declaration(self, token):
        self.module_ansi_header(token)
        token = self.next_token()
        self.non_port_module_item(token)
        token = self.next_token()
        if token != 'endmodule':
            self.error("expected 'endmodule' at end of module")

    def module_ansi_header(self, token):
        if self.token != 'module':
            self.error("expected 'module' at start of module header")
        token = self.next_token()
        self.module_identifer(token)
        token = self.next_token()
        if self.token != ';':
            self.error("expected ';' after module identifier")

    def module_identifer(self, token):
        self.identifier(token)

    def non_port_module_item(self, token):
        self.module_or_generate_item(token)

    def module_or_generate_item(self, token):
        self.module_common_item()

    def module_common_item(self):
        self.next_token()
        self.initial_construct()

    def initial_construct(self):
        if self.token != 'initial':
            self.error("expected 'initial' at start of initial construct")
        self.next_token()
        self.statement_or_null()

    def statement_or_null(self):
        self.statement()
        self.next_token()
        if self.token != ';':
            self.error("expected ';' at end of statement")
        self.next_token()

    def statement(self):
        self.statement_item()

    def statement_item(self):
        self.subroutine_call_statement()

    def subroutine_call_statement(self):
        self.subroutine_call()
        self.next_token()
        if self.token != ';':
            self.error("expected ';' at end of subroutine call statement")
        print(self.token)
        self.next_token()

    def subroutine_call(self):
        self.system_tf_call()

    def system_tf_call(self):
        self.next_token()
        self.system_tf_identifier()
        self.next_token()
        if self.token == '(':
            print(self.token)
            self.next_token()
            self.list_of_arguments()
            self.next_token()
            if self.token != ')':
                self.error("expecting ')' at end of function/task argument list")
            print(self.token)

    def identifier(self):
        print(self.token)

    def system_tf_identifier(self):
        # I don't know, I guess this double checks the tokenizer?
        if self.token[0] != '$':
            self.error("expected '$' at start of system task/function identifier")
        # TODO: more of these for debugging
        print(self.token)

    def list_of_arguments(self):
        self.expression()
        self.next_token()
        while self.token != ',':
            print(',')
            self.next_token()
            self.expression()
            self.next_token()
    
    def expression(self):
        self.primary()

    def primary(self):
        self.primary_literal()

    def primary_literal(self):
        self.string_literal()

    def string_literal(self):
        if self.token != '"':
            self.error("expected '\"' because string literals are the only literals supported right now")
        print(self.token)
        self.next_token()
        while self.token != '"':
            print(self.token)
            self.next_token()


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
