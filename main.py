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
    ## interesting errors to consider:
    ##
    ## identifier starts with a number
    ## stray semi-colons
    ## 
    def __init__(self, sv_code):
        self.code = sv_code
        self.position = 0
        self.line = 1
        self.position_in_line = 0
        self.current_token = ''

    def next(self):
        try:
            # handle newline
            if self.code[self.position] == '\n':
                self.line += 1
                self.position+=1
                self.position_in_line = 0

            # handle whitespace
            while self.code[self.position] in string.whitespace:
                self.position += 1
                self.position_in_line += 1

            # handle punctuation
            if self.code[self.position] in ';()':
                self.position += 1
                self.position_in_line += 1
                self.current_token = self.code[self.position-1]
                return self.current_token

            # handle string constants
            if self.code[self.position] == '"':
                string_start = self.position
                self.position += 1
                self.position_in_line += 1
                # look for quotes to end string, but not if they are preceded by a \
                while self.code[self.position] != '"':
                    if self.code[self.position] == '\\':
                        self.position += 2
                        self.position_in_line += 2
                    else:
                        self.position += 1
                        self.position_in_line += 1
                self.position += 1
                self.position_in_line += 1
                self.current_token = self.code[string_start:self.position]
                return self.current_token

            # handle identifiers
            if(self.code[self.position] in (string.ascii_letters + '_' + '$')):
                token_start = self.position
                self.position += 1
                self.position_in_line += 1
                while(self.code[self.position] in (string.ascii_letters + string.digits + '_')):
                    self.position += 1
                    self.position_in_line += 1
                self.current_token = self.code[token_start:self.position]
                return self.current_token
        # If any of the above position += 1 take us past the end of code,
        # this will save us.  Some would argue this is an improper use of
        # exceptions.
        except IndexError as err:
            self.current_token = ''
            return self.current_token


# parser functions, see systemverilog-1800-2018.bnf that is included
# along with this code to see where these methods and their names come
# from
class Parser:
    def __init__(self, filename):
        self.filename = filename
        with open(self.filename) as sv_file:
            self.code = sv_file.read()
        self.tokenizer = Tokenizer(self.code) 

    def next_token(self):
        token = self.tokenizer.next()
        print(f'>{token}<')
        return token

    def current_token(self):
        return self.tokenizer.current_token

    def error(self, message):
        print(f'{self.filename}:{self.tokenizer.line}:{self.tokenizer.position_in_line}: error: {message}')
        # uncomment when you need to debug (TODO: make --debug-parser
        # a command-line argument)
        #
        # raise
        
        # I'm seeing how it would be useful sometimes to keep looking
        # for errors, and sometimes not.  Not sure how to decide that
        # in this code.

    def go(self):
        self.source_text()

    def source_text(self):
        token = self.next_token()
        while token != '':
            self.description(token)
            token = self.next_token()
        print('parsed source_text')

    def description(self, token):
        self.module_declaration(token)
        print('parsed description')

    def module_declaration(self, token):
        self.module_ansi_header(token)
        self.non_port_module_item(self.next_token())
        if self.next_token() != 'endmodule':
            self.error("expected 'endmodule' at end of module")
        print('parsed module_declaration')

    def module_ansi_header(self, token):
        if token != 'module':
            self.error("expected 'module' at start of module header")
        self.module_identifer(self.next_token())
        if self.next_token() != ';':
            self.error("expected ';' after module identifier")
        print('parsed module_ansi_header')

    def module_identifer(self, token):
        self.identifier(token)
        print('parsed module_identifer')


    def non_port_module_item(self, token):
        self.module_or_generate_item(token)
        print('parsed non_port_module_item')

    def module_or_generate_item(self, token):
        self.module_common_item(token)
        print('parsed module_or_generate_item')

    def module_common_item(self, token):
        self.initial_construct(token)
        print('parsed module_common_item')

    def initial_construct(self, token):
        if token != 'initial':
            self.error("expected 'initial' at start of initial construct")
        self.statement_or_null(self.next_token())
        print('parsed initial_construct')

    def statement_or_null(self, token):
        self.statement(token)
        print('parsed statement_or_null')

    def statement(self, token):
        self.statement_item(token)
        print('parsed statement')

    def statement_item(self, token):
        if token == 'begin':
            self.seq_block(token)
        else:
            self.subroutine_call_statement(token)
        print('parsed statement_item')

    def seq_block(self, token):
        token = self.next_token()
        while token != 'end':
            self.statement_or_null(token)
            token = self.next_token()
        print('parsed seq_block')

    def subroutine_call_statement(self, token):
        self.subroutine_call(token)
        if self.next_token() != ';':
            self.error("expected ';' at end of subroutine call statement")
        print('parsed subroutine_call_statement')

    def subroutine_call(self, token):
        self.system_tf_call(token)
        print('parsed subroutine_call')

    def system_tf_call(self, token):
        self.system_tf_identifier(token)
        if self.next_token() == '(':
            self.list_of_arguments(self.next_token())
            if self.current_token() != ')':
                self.error("expecting ')' at end of function/task argument list")
        print('parsed subroutine_tf_call')

    def identifier(self, token):
        if token[0] == '\\':
            self.escaped_identifier(token)
        else:
            self.simple_identifier(token)
        print('parsed identifier')

    def simple_identifier(self, token):
        print('parsed simple_identifier')

    def escaped_identifier(self, token):
        print('parsed escaped_identifier')

    def system_tf_identifier(self, token):
        # I don't know, I guess this double checks the tokenizer?
        if token[0] != '$':
            self.error("expected '$' at start of system task/function identifier")
        print('parsed system_tf_identifier')

    def list_of_arguments(self, token):
        self.expression(token)
        while self.next_token() == ',':
            self.expression(self.next_token())
        print('parsed list_of_arguments')
    
    def expression(self, token):
        self.primary(token)
        print('parsed expression')

    def primary(self, token):
        self.primary_literal(token)
        print('parsed primary')

    def primary_literal(self, token):
        self.string_literal(token)
        print('parsed primary_literal')

    def string_literal(self, token):
        if token[0] != '"':
            self.error("expected string literal because string literals are the only literals supported right now")
        print('parsed string_literal')


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
