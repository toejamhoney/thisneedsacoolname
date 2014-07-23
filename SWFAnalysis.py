import re
from util import unescapeHTMLEntities

'''
    Check for swf content in a string by searching for CWS or FWS 
    in the first three characters
'''
def isFlash (content):
    content = unescapeHTMLEntities(content)
    content = content[:3]
    compare = ["CWS", "FWS"]
    if content in compare:
        return True
    else:
        return False





