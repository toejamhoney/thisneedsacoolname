import os
import re
import sys
import argparse

import xml_creator
from JSAnalysis import analyse as analyse
from util.str_utils import unescapeHTMLEntities as unescapeHTML

reJSscript = '<script[^>]*?contentType\s*?=\s*?[\'"]application/x-javascript[\'"][^>]*?>(.*?)</script>'

if __name__ == '__main__':
    pdf = {
        'xml': '',
        'javascript': '',
        'deobfuscated': '',
        'swf': '',
    }
    parser = argparse.ArgumentParser()
    parser.add_argument('pdf', help='The PDF to be analyzed')
    parser.add_argument('-x', action='store_true', default=False, help='Print xml produced from PDF')

    try:
        args = parser.parse_args()
    except Exception:
        parser.exit(status=0, message='USAGE GOES HERE SOMEDAY')
    else:
        if os.path.exists(args.pdf):
            pdf['xml'], js, swf = xml_creator.create(args.pdf)
            if args.x:
                print pdf['xml']
            #print "JS: " + str(js)
            if len(js) > 0:
                for item in js:
                    item = unescapeHTML(item)
                    scriptElements = re.findall(reJSscript, item, re.DOTALL | re.IGNORECASE)
                    if scriptElements != []:
                        item = ''
                        for scriptElement in scriptElements:
                            item += scriptElement + '\n\n'
                    #item = re.sub("(\s*<.*?>)", "", item, flags=re.M)
                    item = re.sub("^(\s*<)", "//", item, flags=re.M)
                    pdf['javascript'] += item + "\n\n"
                    pdf['deobfuscated'] += analyse(item, pdf['xml'])
            #print pdf['deobfuscated']
            f = open ('deob_js/' + os.path.basename(args.pdf), 'w')
            f.write(pdf['deobfuscated'])
            f.close()
            if len(swf) > 0:
                for item in swf:
                    item = unescapeHTML(item)
                    pdf['swf'] += item + " \n\n"
                    #TODO: retrieve actionscript
            #print pdf['swf']
        else:
            print 'Unable to find PDF file/directory:', args.pdf
            sys.exit(1)
