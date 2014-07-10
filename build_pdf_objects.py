import lxml.etree

#search tree for specified tag with specified value
def search_tree (root, tag):
    for key in root.iterfind(tag):
           return key
    else: 
        return None

def get_annots(app, root):
  for annot in root.iterfind(".//Annots"):
    objs = []
    parent = annot.getparent()
    ref_list = parent[parent.index(annot)+1][0]
    for ref in ref_list:
      id = ref.get("id")
      for obj in root.iterfind(".//object"):
          if obj.get("id") == id:
              size = obj[0].get("size")
              size = re.sub("%", "", size)
              new = {}
              childs =  obj[0].getchildren()
              for i in range(int(size)):
                  if childs[2*i+1][0].tag == "literal":
                      new[childs[2*i].text] = unescapeHTMLEntities(childs[2*i+1][0].text)
                  elif childs[2*i+1][0].tag == "ref":
                      for ob in root.iterfind(".//object"):
                          if ob.get("id") == childs[2*i+1][0].get("id"):
                              for child in ob.iterdescendants(tag="data"):
                                 new[childs[2*i].text] = unescapeHTMLEntities(child.text)
                  else:
                       new[childs[2*i].text] = "Unknown tag: " + childs[2*i+1][0].tag
              new["subject"] = new.pop("Subj")
              app['doc']['annots'].append(new)

def create_event_obj(tree):
    event_attrs = ["author", "calculate", "creator", "creationDate", "delay", "dirty", "external", "filesize", "keywords", "modDate", "numFields", "numPages", "numTemplates", "path", "pageNum", "producer", "subject", "title", "zoom", "zoomType"]
    event = {}
    event["target"] ={}
    for item in event_attrs:
        elem = search_tree(tree, item[0].upper() + item[1:])
        if elem != None:
            parent = elem.getparent()
            sibling = parent[parent.index(elem)+1][0]
            if sibling.tag == "string" and sibling.text != None:
                event["target"][item] = unescapeHTMLEntities(sibling.text)
            elif sibling.tag == "ref":
                for ob in tree.iterfind(".//object"):
                    if ob.get("id") == sibling.get("id"):
                        for child in ob.iterdescendants(tag="data"):
                            if child.text != None:
                                event["target"][item] = unescapeHTMLEntities(child.text)
            else:
                event["target"][item] = "Unknown tag: " + sibling.tag
    #print event
    return event

def create_app_obj(tree):
    app= {}
    app_attrs = ["calculate", "formsVersion", "fullscreen", "language", "numPlugins", "openInPlace", "platform", "toolbar", "toolbarHorizontal", "toolbarVertical"]
    doc = {}
    for item in app_attrs:
        elem = search_tree(tree, item[0].upper() + item[1:])
        if elem != None:
            parent = elem.getparent()
            doc[item] = unescapeHTMLEntities(parent[parent.index(elem)+1][0].text)
    app['doc'] = doc;
    app['doc']['annots'] = []
    app['doc']['viewerType'] = 'Reader'
    app['viewerType'] = 'Reader'
    app['viewerVersion'] = 5.0
    app['plugIns'] = [{ 'version': 6.0}, {'version': 7.5}, {'version': 8.7},{'version': 9.1}]
    if not 'language' in app.keys():
        app['language'] = "ENU"
    if not 'platform' in app.keys():
        app['platform'] = "WIN"
    get_annots(app, tree)
    return app

def create_info_obj(tree):
    info_attrs = ["author", "creator", "creationDate", "Date", "keywords", "modDate", "producer", "subject", "title", "trapped"]
    this = {}
    this["info"] ={}
    for item in info_attrs:
        elem = search_tree(tree, item[0].upper() + item[1:])
        if elem != None:
            parent = elem.getparent()
            sibling = parent[parent.index(elem)+1][0]
            if sibling.tag == "string" and sibling.text != None:
                this["info"][item] = unescapeHTMLEntities(sibling.text)
            elif sibling.tag == "ref":
                for ob in tree.iterfind(".//object"):
                    if ob.get("id") == sibling.get("id"):
                        for child in ob.iterdescendants(tag="data"):
                            this["info"][item] = unescapeHTMLEntities(child.text)
            else:
                this["info"][item] = "Unknown tag: " + sibling.tag
    #print this
    return this

