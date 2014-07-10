import build_pdf_objects, re, htmlentitydefs, lxml.etree as ET
try:
    import PyV8
    
    JS_MODULE = True
    
    class Global(PyV8.JSClass):
        evalCode = ''
        
        def evalOverride(self, expression):
            if self.evalCode.find(expression) == -1:
                self.evalCode += expression +'\n'
            return

        def evalOverride2(self, expression):
            if self.evalCode.find(expression) == -1:
                self.evalCode += expression +'\n'
            return PyV8.JSContext.current.eval(expression)
        
except:
    JS_MODULE = False

reJSscript = '<script[^>]*?contentType\s*?=\s*?[\'"]application/x-javascript[\'"][^>]*?>(.*?)</script>'

def create_objs(context, xml):
    try:
        tree = ET.fromstring(xml)
    except Exception as e:
        print "Tree: " + e.message
        #pass
    if tree is not None:
        try: 
            app = build_pdf_objects.create_app_obj(tree)
            context.eval("app = " + str(app) + ";")
            context.eval("app.doc.syncAnnotScan = function () {}")
            context.eval("app.doc.getAnnots = function () { return app.doc.annots;}")
            context.eval("app.eval = function (string) { eval(string);}")
            context.eval("app.newDoc = function () { return '';}")
            context.eval("app.getString = function () { ret = \"\"; for(var prop in app){ ret += app[prop]; } return ret;}")
            print app
        except Exception as e:
            print "App: " + e.message
            #pass
        try:
            event = build_pdf_objects.create_event_obj(tree)
            context.eval("event = " + str(event) + ";")
            print event
        except Exception as e:
            print "Event: " + e.message
            #pass
        try:
            info = build_pdf_objects.create_info_obj(tree)
            context.eval("this.info = " + str(info['info']) + ";")
            context.eval("event.target.info = this.info")
            context.eval("this.eval = eval")
            print info
        except Exception as e:
            print "Info: " + e.message
            #pass

def analyse (js, xml):
    context = PyV8.JSContext(Global())
    context.enter()
    context.eval('eval=evalOverride')
    if JS_MODULE:
        try:
            create_objs(context, xml)
            #evalCode = eval_loop(code, context)
            #return evalCode
            return ""
        except Exception as e:
            print 'Error with analyzing JS: ' + e.message
            return ''
    else:
        print 'Error with PyV8 context'
        return ''
    



def isJavascript(content):
    '''
        Given an string this method looks for typical Javscript strings and try to identify if the string contains Javascript code or not.
        
        @param content: A string
        @return: A boolean, True if it seems to contain Javascript code or False in the other case
    '''
    JSStrings = ['var ',';',')','(','function ','=','{','}','if ','else','return','while ','for ',',','eval']
    keyStrings = [';','(',')']
    stringsFound = []
    limit = 15
    minDistinctStringsFound = 5
    results = 0
    content = unescapeHTMLEntities(content)
    if re.findall(reJSscript, content, re.DOTALL | re.IGNORECASE) != []:
        return True
    for char in content:
        if (ord(char) < 32 and char not in ['\n','\r','\t','\f','\x00']) or ord(char) >= 127:
            return False

    for string in JSStrings:
        cont = content.count(string)
        results += cont
        if cont > 0 and string not in stringsFound:
            stringsFound.append(string)
        elif cont == 0 and string in keyStrings:
            return False

    if results > limit and len(stringsFound) >= minDistinctStringsFound:
        return True
    else:
        return False

def unescapeHTMLEntities(text):
    '''
        Removes HTML or XML character references and entities from a text string.
        
        @param text The HTML (or XML) source text.
        @return The plain text, as a Unicode string, if necessary.
        
        Author: Fredrik Lundh
        Source: http://effbot.org/zone/re-sub.htm#unescape-html
    '''
    def fixup(m):
        text = m.group(0)
        if text[:2] == '&#':
            # character reference
            try:
                if text[:3] == '&#x':
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub('&#?\w+;', fixup, text)
