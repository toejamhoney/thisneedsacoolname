import re, lxml.etree as ET
from  pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import PDFStream, PDFObjRef, PDFNotImplementedError
from pdfminer.psparser import PSKeyword, PSLiteral
from pdfminer.utils import isnumber
from JSAnalysis import isJavascript
from SWFAnalysis import isFlash


'''
    Parse a pdf and build an xml tree based on the object structure
'''
class FrankenParser(object):
    def __init__(self, pdf, debug=False):
        self.errors = ''
        self.debug = debug
        self.pdf = pdf
        self.xml = ''
        self.javascript = []
        self.deobfuscated = []
        self.swf = []
        self.found_eof = False
        self.bin_blob = ''
        self.parse()
        self.tree = self.tree_from_xml(self.xml)

    def e(self, s):
        ESC_PAT = re.compile(r'[\000-\037&<>()"\042\047\134\177-\377]')
        return ESC_PAT.sub(lambda m:'&#%d;' % ord(m.group(0)), s)

    '''
        Convert a pdf object into xml
    '''
    def dump(self, obj):
        res = ""
        if obj is None:
            res += '<null />'
            return res

        if isinstance(obj, dict):
            res += '<dict size="%' + str(len(obj)) + '">\n'
            for (k,v) in obj.iteritems():
                res += '<' + k + '>'
                res += self.dump(v)
                res += '</' + k + '>\n'
            res += '</dict>'
            return res

        if isinstance(obj, list):
            res += '<list size="' + str(len(obj)) + '">\n'
            for v in obj:
                res += self.dump(v)
                res += '\n'
            res += '</list>'
            return res

        if isinstance(obj, str):
            self.check_js(obj)
            #encode base64 to avoid illegal xml characters
            res += '<string>' + self.e(obj).encode('base64') + '</string>'
            return res

        if isinstance(obj, PDFStream):
            res += '<stream>\n'
            try:
                res += '<props>\n'
                res += self.dump(obj.attrs)
                res += '\n</props>\n'
                data = obj.get_data()
                self.check_js(str(data))
                self.check_swf(str(data))
                res += '<data size="' + str(len(data)) + '">' + self.e(data).encode('base64') + '</data>\n'
            #Throws an exception if the filter is unsupported, etc
            except Exception as e:
                print e.message
            #make sure the tag is closed appropriately
            res += '</stream>'
            return res

        if isinstance(obj, PDFObjRef):
            res += '<ref id="' + str(obj.objid) + '" />'
            return res

        if isinstance(obj, PSKeyword):
            self.check_js(obj.name)
            res += '<keyword>' + obj.name + '</keyword>'
            return res

        if isinstance(obj, PSLiteral):
            self.check_js(obj.name)
            res += '<literal>' + obj.name + '</literal>'
            return res

        if isnumber(obj):
            self.check_js(str(obj))
            res += '<number>' + str(obj) + '</number>'
            return res

        raise TypeError(obj)

    '''
        Add the PDF trailers to the xml
    '''
    def dumptrailers(self, doc):
        res = ""
        for xref in doc.xrefs:
            res += '<trailer>\n'
            res += self.dump(xref.trailer)
            res += '\n</trailer>\n\n'
        return res

    '''
        Parse the pdf and build the xml
    '''
    def parse (self):
        fp = file(self.pdf, 'rb')
        parser = PDFParser(fp, dbg=self.debug)
        doc = PDFDocument(parser, dbg=self.debug)
        #extract blob of data after EOF (if it exists)
        if doc.found_eof and doc.eof_distance > 3:
            self.bin_blob = parser.read_from_end(doc.eof_distance)
        res = '<pdf>'
        visited = set() #keep track of the objects already visited
        for xref in doc.xrefs:
            for objid in xref.get_objids():
                if objid in visited: continue
                visited.add(objid)
                try:
                    obj = doc.getobj(objid)
                    if obj is None: continue
                    res += '<object id="' + str(objid) + '">\n'
                    res += self.dump(obj)
                    res += '\n</object>\n\n'
                except Exception as e:
                    #usually means the object cannot be found
                    print e.message
        fp.close()
        res += self.dumptrailers(doc)
        res += '</pdf>'
        self.xml=res
        self.errors = doc.errors
        self.bytes_read = parser.BYTES
        return

    '''
        Check string for javascript content
    '''
    def check_js (self, content):
        if isJavascript(content):
            #pull out js between script tags
            reJSscript = '<script[^>]*?contentType\s*?=\s*?[\'"]application/x-javascript[\'"][^>]*?>(.*?)</script>'
            res = re.findall(reJSscript, content, re.DOTALL | re.IGNORECASE)
            if res != []:
                self.javascript.append('\n'.join(res))
            else:
                self.javascript.append(content)
        return

    '''
        Check string for flash content
    '''
    def check_swf(self, content):
        if isFlash(content):
            self.swf.append(content)
        return

    '''
        Create an lxml tree from the xml string
    '''
    def tree_from_xml (self, xml):
        try:
            tree = ET.fromstring(xml)
            return tree
        except Exception as e:
            print "Tree Error"
            print e.message
            return None

    '''
        Calls edges to recursively create the graph string
    '''
    def make_graph(self, tree):
        res = []
        if tree is not None:
            self.edges(tree, res, 0)
        return res
        
    '''
       creates string showing connections between objects
    '''
    def edges(self, parent, output, id):
      for child in list(parent):
        if child.get("id") != None:
            cid = child.get("id")
            output.append(str(id) + ' ' + cid +  '\n')
            self.edges(child, output, cid)
        else:
            res = self.edges(child, output, id)
      return
