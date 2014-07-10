import argparse, os, sys, xml_creator, re
from JSAnalysis import analyse as analyse
from JSAnalysis import unescapeHTMLEntities as unescapeHTML

if __name__ == '__main__':
    pdf = {
        'xml': '',
        'javascript': '',
        'deobfuscated': ''
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
            pdf['xml'], js = xml_creator.create(args.pdf)
            if args.x:
                print pdf['xml']
            #print "JS: " + str(js)
            if len(js) > 0:
                for item in js:
                    item = unescapeHTML(item)
                    item = re.sub("^(<)", "//", item, flags=re.M)
                    pdf['javascript'] += item + "\n\n"
                    pdf['deobfuscated'] += analyse(item, pdf['xml'])
                    
        else:
            print 'Unable to find PDF file/directory:', args.pdf_in
            sys.exit(1)
