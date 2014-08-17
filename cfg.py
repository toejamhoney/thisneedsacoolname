import os
import sys
from ConfigParser import SafeConfigParser


DEFAULT_CFG = 'frankenstein.cfg'


class Config(object):

    def __init__(self, path='', name=''):
        if name:
            cfg_file = os.path.join(path, name)
        else:
            cfg_file = os.path.join(path, DEFAULT_CFG)
        self.parser = SafeConfigParser()
        if not self.parser.read(cfg_file):
            print 'No configuration file found:', cfg_file
            self.new_cfg()

    def new_cfg(self):
        self.section_gen()
        self.section_db()
        self.section_net()
        with open(DEFAULT_CFG, 'w') as new_cfg:
            print 'Creating new config file in CWD:', DEFAULT_CFG
            print 'Please double check the default values before running again:'
            print self
            self.parser.write(new_cfg)
        sys.exit(0)

    def section_gen(self):
        sec = 'general'
        self.parser.add_section(sec)
        self.parser.set(sec, 'output', 'sqlite3 #default')
        self.parser.set(sec, '#output', 'stdout')

    def section_db(self):
        sec = 'database'
        self.parser.add_section(sec)
        self.parser.set(sec, 'path', os.getcwd())
        self.parser.set(sec, 'user', 'frankenstein')
        self.parser.set(sec, 'pw', 'PuttinOnTheRitz')
        self.parser.set(sec, 'db', 'frankenstein.sqlite')

    def section_net(self):
        sec = 'network'
        names = set()
        self.parser.add_section('network')
        self.parser.set(sec, 'port', '4884')
        try:
            fin = open('virtual-machines.txt', 'r')
        except IOError:
            sys.stderr.write("cfg could not open 'virtual-machines.txt'\tNo guests networked...\n")
        else:
            for line in fin:
                try:
                    name, ip4addr, desc = line.split(',')
                except ValueError:
                    name, ip4addr = line.split(',')
                else:
                    self.parser.set(sec, '%s-%s' % (name, 'description'), desc)
                finally:
                    self.parser.set(sec, '%s-%s' % (name, 'address'), ip4addr)
                    names.add(name)
            fin.close()
        self.parser.set(sec, 'guests', ','.join(['%s' % n for n in names]))


    def setting(self, section='', option=''):
        if not section:
            for s in self.parser.sections():
                if self.parser.has_option(s, option):
                    return self.parser.get(s, option)
        elif self.parser.has_option(section, option):
            return self.parser.get(section, option)
        else:
            return None

    def __str__(self):
        rv = ''
        for sect in self.parser.sections():
            rv += 'Section: %s\n' % sect
            for opt in self.parser.options(sect):
                rv += '\t%s\t=\t%s\n' % (opt, self.parser.get(sect, opt))
        return rv


if __name__ == '__main__':
    cfg = Config()
    print cfg
