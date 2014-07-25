import os
import sys
import argparse


class BaseParser(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser()

    def pre_parse(self, line):
        if not isinstance(line, list):
            line = line.split(' ')
        return line

    def post_parse(self, dic):
        return dic

    def parse_args(self, line):
        line = self.pre_parse(line)
        try:
            result = self.parser.parse_args(line)
        except SystemExit:
            if '-h' in line or '--help' in line:
                return ''
            print 'Parsing failed:', line
            sys.exit(1)
        else:
            result = self.post_parse(result)
            return result

    def sanitize_path(self, path_str):
        try:
            path_str = os.path.expanduser(path_str)
            path_str = os.path.expandvars(path_str)
            path_str = os.path.normpath(path_str)
            path_str = os.path.abspath(path_str)
        except (AttributeError, TypeError):
            print 'Err sanitizing "--input" path'
            path_str = None
        finally:
            return path_str


class ServerParser(BaseParser):

    def __init__(self):
        super(ServerParser, self).__init__()
        self.parser.add_argument('-m', '--mode', default='rpc', help='The mode of the server to start: job, rpc, ast, ... Default: rpc')
        self.parser.add_argument('-a', '--address', default='0.0.0.0', help='IPv4 address to listen on. Default: 0.0.0.0')
        self.parser.add_argument('-p', '--port', default='4884', help='Port to listen on. Default: 4884')
        self.parser.add_argument('-d', '--debug', default=False, action='store_true')
        self.parser.add_argument('-v', '--verbose', default=False, action='store_true')
