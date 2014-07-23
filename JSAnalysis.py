import build_pdf_objects, re, lxml.etree as ET
from util import unescapeHTMLEntities
'''try:
    import PyV8
    
    JS_MODULE = True
    
    class Global(PyV8.JSClass):
        evalCode = ''
        
        def evalOverride(self, expression):
            if self.evalCode.find(expression) == -1:
                self.evalCode += expression +'\n'
            return

        """def evalOverride2(self, expression):
            if self.evalCode.find(expression) == -1:
                self.evalCode += expression +'\n'
            return PyV8.JSContext.current.eval(expression)"""
        
except:
    JS_MODULE = False'''
from subprocess import check_output

reJSscript = '<script[^>]*?contentType\s*?=\s*?[\'"]application/x-javascript[\'"][^>]*?>(.*?)</script>'

#Mimic native Adove objects and add them to the context
def create_objs(tree):
    obj_string = ''
    try: 
        app = build_pdf_objects.create_app_obj(tree)
        obj_string += "app = " + str(app) + ";"
        obj_string +="app.doc.syncAnnotScan = function () {};\n"
        obj_string +="app.doc.getAnnots = function () { return app.doc.annots;};\n"
        obj_string +="app.eval = function (string) { eval(string);};\n"
        obj_string +="app.newDoc = function () { return '';};\n"
        obj_string +="app.getString = function () { ret = \"\"; for(var prop in app){ ret += app[prop]; } return ret;};\n"
        #return obj_string
        #print app
    except Exception as e:
        print "App: " + e.message
        pass
    try:
        info = build_pdf_objects.create_info_obj(tree)
        obj_string +="this.info = " + str(info) + ";\n"
        obj_string +="this.eval = eval;\n"
        #print info
    except Exception as e:
        print "Info: " + e.message
        pass
    try:
        event = build_pdf_objects.create_event_obj(tree)
        obj_string +="event = " + str(event) + ";\n"
        obj_string +="event.target.info = this.info;\n"
        #print event
    except Exception as e:
        print "Event: " + e.message
        pass
    return obj_string


def eval_loop (code, context, old_msg = ""):
    try:
        context.eval(code)
        return context.eval("evalCode")
    except ReferenceError as e:
        #print e.message

        #do something to fix  
        if e.message == old_msg:
            #return e.message
            return context.eval("evalCode")
        elif e.message.find('$') > -1:
            context.eval("$ = this;")
        else:
            #try commenting out line
            line_num = re.findall("@\s(\d*?)\s", e.message)
            line_num = int(line_num[0])
            i = 0

            for item in code.split("\n"):
                i += 1
                if i == line_num:
                    code = re.sub(item, "//" + item, code)
                    break
        return eval_loop(code, context, e.message)
    except TypeError as te:
        #print te.message
        if te.message == old_msg:
            #return te.message
            return context.eval("evalCode")
        elif te.message.find("called on null or undefined") > -1:
            #in Adobe undefined objects become app object
            line = re.findall("->\s(.*)", te.message)
            sub, count = re.subn("=\s?.\(.*?\)", "=app", line[0])
            if count < 1:
               sub = re.sub("=.*", "=app", line[0])
            line = re.escape(line[0])
            code = re.sub(line, sub, code)
        elif te.message.find("undefined is not a function") > -1:
            #sub in eval as a guess
            line = re.findall("->\s(.*)", te.message)
            match = re.findall("[\s=]?(.*?)\(", line[0])
            if len(match) > 0:
                sub = re.sub(match[0], "eval", line[0])
                line = re.escape(line[0])
                code = re.sub(line, sub, code)
            else:
                #return te.message
                return context.eval("evalCode")
        elif te.message.find("Cannot read property") > -1:
            #undefined becomes app
            line = re.findall("->\s(.*)", te.message)
            match = re.findall("[=\s](.*?)\[", line[0])
            if len(match) > 0:
                sub = re.sub(match[0], "app", line[0])
                line = re.escape(line[0])
                code = re.sub(line, sub, code)
            else:
                #return te.message
                return context.eval("evalCode")
        else:
            #return te.message
            return context.eval("evalCode")
        return eval_loop(code, context, te.message)
    except SyntaxError as se:
        #print se.message
        if se.message == old_msg:
            #return se.message
            return context.eval("evalCode")
        line_num = re.findall("@\s(\d*?)\s", se.message)
        if len(line_num) > 0:
            line_num = int(line_num[0])
            i = 0
            #try commenting out the line number with the error
            for item in code.split("\n"):
                i += 1
                if i == line_num:
                    esc_item = re.escape(item)
                    code, n = re.subn(esc_item, "//" + item, code)
                    break
        else:
            #return se.message
            return context.eval('evalCode')
        eval_loop(code, context, se.message)
    except Exception as e1:
        #print e1.message
        #return e1.message
        return context.eval("evalCode")

def analyse (js, tree):
        try:
            eval_string = '_eval = eval; eval = function (expression) { console.log(expression); return;};\n'
            if tree is not None:
                eval_string += create_objs(tree)
            eval_string += js
            #ret = check_output(["nodejs", "sandbox.js", eval_string])
            ret = check_output(["docker", "run", "-i", "node-base", "/bin/bash","nodejs", "docker.js", eval_string])
            #print 'ret: ' + ret
            if ret == None:
                return ''
            else:
                return ret
        except Exception as e:
            #return 'Error with analyzing JS: ' + e.message
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


