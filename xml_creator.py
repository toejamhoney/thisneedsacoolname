import re
from  pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import PDFStream, PDFObjRef
from pdfminer.psparser import PSKeyword, PSLiteral
from pdfminer.utils import isnumber
from JSAnalysis import isJavascript


ESC_PAT = re.compile(r'[\000-\037&<>()"\042\047\134\177-\377]')
def e(s):
    return ESC_PAT.sub(lambda m:'&#%d;' % ord(m.group(0)), s)

def dump(obj, js):
    res = ""
    if obj is None:
        res += '<null />'
        return res, js

    if isinstance(obj, dict):
        res += '<dict size="%' + str(len(obj)) + '">\n'
        for (k,v) in obj.iteritems():
            res += '<' + k + '>'
            tmp, js = dump(v, js)
            res += tmp
            res += '</' + k + '>\n'
        res += '</dict>'
        return res, js

    if isinstance(obj, list):
        res += '<list size="' + str(len(obj)) + '">\n'
        for v in obj:
            tmp, js = dump(v, js)
            res += tmp
            res += '\n'
        res += '</list>'
        return res, js

    if isinstance(obj, str):
        if isJavascript(obj):
            js.append(e(obj))
        res += e(obj)
        return res, js

    if isinstance(obj, PDFStream):
        res += '<stream>\n<props>\n'
        tmp, js = dump(obj.attrs, js)
        res += tmp
        res += '\n</props>\n'
        data = obj.get_data()
        if isJavascript(str(data)):
            js.append(str(data))
        res += '<data size="' + str(len(data)) + '">' + e(data) + '</data>\n'
        res += '</stream>'
        return res, js

    if isinstance(obj, PDFObjRef):
        res += '<ref id="' + str(obj.objid) + '" />'
        return res, js

    if isinstance(obj, PSKeyword):
        if isJavascript(obj.name):
            js.append(obj.name)
        res += '<keyword>' + obj.name + '</keyword>'
        return res, js

    if isinstance(obj, PSLiteral):
        if isJavascript(obj.name):
            js.append(obj.name)
        res += '<literal>' + obj.name + '</literal>'
        return res, js

    if isnumber(obj):
        if isJavascript(str(obj)):
            js.append(str(obj))
        res += '<number>' + str(obj) + '</number>'
        return res, js

    raise TypeError(obj)

# dumptrailers
def dumptrailers(doc, js):
    res = ""
    for xref in doc.xrefs:
        res += '<trailer>\n'
        tmp, js = dump(xref.trailer, js)
        res += tmp
        res += '\n</trailer>\n\n'
    return res, js

def create (fname):
    fp = file(fname, 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument(parser)
    res = '<pdf>'
    visited = set()
    js = []
    for xref in doc.xrefs:
        for objid in xref.get_objids():
            if objid in visited: continue
            visited.add(objid)
            try:
                obj = doc.getobj(objid)
                if obj is None: continue
                res += '<object id="' + str(objid) + '">\n'
                tmp, js = dump(obj, js)
                res += tmp
                res += '\n</object>\n\n'
            except Exception as e:
                print 'not found: ' + e.message
    fp.close()
    tmp, js = dumptrailers(doc, js)
    res += tmp + '</pdf>'
    #print js
    return res, js
