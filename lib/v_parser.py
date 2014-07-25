import argparse
from datetime import datetime
import sys
import os


try:
    import config
except ImportError:
    class config:
        SETTINGS = {'LOG_USER': 'logger'}


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
            result = vars(result)
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
        self.parser.add_argument('-t', '--type', default='rpc', help='The type of server to start: job, rpc, ast, ... Default: rpc')
        self.parser.add_argument('-a', '--address', default='0.0.0.0', help='IPv4 address to listen on. Default: 0.0.0.0')
        self.parser.add_argument('-p', '--port', default='4884', help='Port to listen on. Default: 4884')


class VoodoParser(BaseParser):
    def __init__(self):
        super(VoodoParser, self).__init__()
        self.parser.add_argument('-i', '--input', nargs='*', default='', help='Input file to replace stdin')
        self.parser.add_argument('-d', '--debug', default='INFO',
                                 help='Indicates debug level. CRITICAL, ERROR, WARNING (default), INFO, or DEBUG')

    def post_parse(self, dic):
        file_in = dic.get('input')
        if file_in:
            dic['input'] = self.sanitize_path(' '.join(file_in))
        return dic


class VBoxParser(BaseParser):
    def __init__(self):
        super(VBoxParser, self).__init__()
        self.parser.add_argument('-d', '--desc', default='none', help='TODO')
        self.parser.add_argument('--delete', action='store_true', default=False, help='TODO')
        self.parser.add_argument('-n', '--name', nargs=1, default='no_name', help='TODO')
        self.parser.add_argument('-r', '--restore', default=False, action='store_true', help='TODO')
        self.parser.add_argument('-v', '--machines', default=[], nargs='*', help='TODO')
        self.parser.add_argument('-i', '--input', nargs='*', help='TODO')

    def post_parse(self, dic):
        if isinstance(dic['input'], list):
            dic['input'] = ' '.join(dic['input'])
        if isinstance(dic['name'], list):
            dic['name'] = ' '.join(dic['name'])
        return dic


class JobParser(BaseParser):
    def __init__(self):
        super(JobParser, self).__init__()
        self.parser.add_argument('-a', '--analyzers', nargs='*', default=[],
                                 help='optional: specify analyzing tools to be run before and after launch. Options = '
                                      'autorunsc, registry')
        self.parser.add_argument('-b', '--before', action='store_true', default=False,
                                 help='optional: specify this job as creating a before analysis image used in diffs '
                                      'later')
        self.parser.add_argument('--date_stamp', default=datetime.today().strftime('%Y-%m-%d'))
        self.parser.add_argument('-d', '--diff', action='store_true', default=False,
                                 help='optional: specify this job should have a diff run on the logs')
        self.parser.add_argument('-f', '--flag', nargs='*', default=[],
                                 help='optional: flags for exe')
        self.parser.add_argument('--flag2', nargs='*', default=[],
                                 help='optional: flags for exe')
        self.parser.add_argument('--flag3', nargs='*', default=[],
                                 help='optional: flags for exe')
        self.parser.add_argument('-i', '--input', nargs='*', default=[],
                                 help='optional: use with a tool to specify an input file name')
        self.parser.add_argument('-j', '--job', default='no-name_' + datetime.today().strftime('%I-%M-%S'),
                                 help='optional: name for the job that will be run')
        self.parser.add_argument('-l', '--log', action='store_true', default=False,
                                 help='optional: name of log, or white space separated list of log names (from config'
                                      '.py). No entry = no logs')
        self.parser.add_argument('--lib', default='',
                                 help='optional: Specifies a library name (source of sample sets/catalogs)')
        self.parser.add_argument('-m', '--method', default='debug', help='RPC Method to run on guest')
        self.parser.add_argument('-o', '--output', nargs='*', default=[],
                                 help='optional: use with a tool to specify an output file name')
        self.parser.add_argument('--path', default='',
                                 help='optional: Set the path for a library or catalog, for example')
        self.parser.add_argument('-p', '--priority', type=int, default=2,
                                 help='optional: set the priority of the jobs being forked. High = 0, Med(Default) = '
                                      '1, Low = 2')
        self.parser.add_argument('--push_sample', default=False, action='store_true')
        self.parser.add_argument('-r', '--reset', action='store_true', default=False,
                                 help='optional: default is true, tells the driver to reset(kill, restore, '
                                      'start) the guests between forked procs')
        self.parser.add_argument('--results', default={})
        self.parser.add_argument('-s', '--set', default='',
                                 help='optional: Specify a sample set name. A set is a catalog, or sample set of '
                                      'artifacts')
        self.parser.add_argument('-t', '--pin_tool', nargs='*', default=[],
                                 help='optional: dll to be used with pin execution')
        self.parser.add_argument('--time_stamp', default=datetime.today().strftime('%I-%M'))
        self.parser.add_argument('--username', default=config.SETTINGS['LOG_USER'])
        self.parser.add_argument('-v', '--vms', nargs='*', default=[],
                                 help='list of virtual machine names to run job on')
        self.parser.add_argument('-w', '--wait', type=int, default=10,
                                 help='optional argument for a wait time. default is 10')
        self.parser.add_argument('-x', '--exe', nargs='*', default=[],
                                 help='required for launch command: path to file to load/run')

    def post_parse(self, dic):
        dic['exe'] = ' '.join(dic['exe'])
        dic['input'] = ' '.join(dic['input'])
        dic['output'] = ' '.join(dic['output'])
        dic['pin_tool'] = ' '.join(dic['pin_tool'])
        dic['flag'] = ' '.join(dic['flag']).replace('+', '-')
        dic['flag2'] = ' '.join(dic['flag2']).replace('+', '-')
        dic['flag3'] = ' '.join(dic['flag3']).replace('+', '-')
        if not dic['exe'] and dic['input']:
            dic['push_sample'] = True
        return dic


if __name__ == '__main__':
    parser = VBoxParser()
    while True:
        print 'Test VBoxParser input (q to quit):',
        args = raw_input().split(' ')
        if args[0] == 'q':
            break
        print 'VBOXPARSER:', parser.parse_args(args)

    parser2 = JobParser()
    while True:
        print 'Test JobParser input (q to quit):',
        args = raw_input().split(' ')
        if args[0] == 'q':
            break
        print 'JOBPARSER:', parser2.parse_args(args)
