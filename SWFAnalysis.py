import re
from util import unescapeHTMLEntities

def isFlash (content):
    content = unescapeHTMLEntities(content)
    content = content[:3]
    compare = ["CWS", "FWS"]
    if content in compare:
        return True
    else:
        return False





