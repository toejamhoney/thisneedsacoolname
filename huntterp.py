import sys
import os

'''
For testing run the module without arguments. (Can also be run on arbitrary files.)

'''
class Test(object):
    tests = [ 'ftp', 'http' ]
    ftp = "6674703a2f2f676f6f676c652e636f6d"
    http = "6674703a2f2f676f6f676c652e636f6d687474703a2f2f676f6f676c652e636f6df1"

'''
This function makes no assumptions on the validity of the string values
'''
def ascii2hex(string):
    if isinstance(string, str):
        return ''.join( [hex(ord(c))[2:] for c in string] )
    else:
        return ''
'''
Convert a string from hex to ascii. Starting from the first position, and
stopping on the first invalid (not-printable) character or invalid input,
whichever comes first.
'''
def hex2ascii(string):
    letters = ''
    for idx in range(0, len(string), 2):
        try:
            c1 = string[idx]
            c2 = string[idx+1]
            i = int(c1+c2, 16)
            if i < 32 or i > 127:
                break 
            ch = chr(i)
        except (ValueError, TypeError, IndexError):
            break
        else:
            letters += ch
    return letters

'''
Return a list of strings found in the hexstring. Should not return overlapping
results. Needle is converted from ASCII to HEX on the first line.
'''
def find_in_hex(needle, hexstack):
    needle = ascii2hex(needle)
    results = []
    total = 0
    while True:
        idx = hexstack.find(needle)
        if idx < 0:
            break
        total += idx
        results.append((total, hex2ascii(hexstack[idx:])))
        hexstack = hexstack[idx + 1:]
        total += 1
    return results

def verify(vals, string):
    for val in vals:
        sys.stdout.write('Verifying [%s] @ [%d]...' % (val[1], val[0]))
        if string[val[0]:len(val[1])].startswith(hex2ascii(val[1])):
            sys.stdout.write('pass\n')
        else:
            sys.stdout.write('fail. string[%d]==[%s]...\n' % (val[0], val[1][val[0]:val[0]+32]))

'''
Find h1 in h2 | h1 == ASCII && h2 == HEX
'''
def main(h1, h2):
    if not isinstance(h2, str):
        print 'Invalid input:',type(h2)
        print str(h2)
        return

    print 'Searching for "%s" in "%s"...' % (h1, h2[:32])

    urls = find_in_hex(h1, h2)
    
    print 'Found: %d occurrences' % len(urls)
    if len(urls):
        verify(urls, h2)
    
if __name__ == "__main__":
    try:
        needle = sys.argv[1]
        fin = open(sys.argv[2], 'r')
    except IndexError:
        print 'Invalid or no arguments. Usage: huntterp.py needle haystack.txt'
        print 'Beginning tests'
        t = Test()
        for needle in t.tests:
            haystack = getattr(t, needle)
            main(needle, haystack)
    except IOError as e:
        print e
    else:
        main(needle, fin.read())
