# -*- coding: latin-1 -*-

import sys, traceback
import re
import htmlentitydefs

from lib.common import smart_unicode

enable_debug = sys.modules["__main__"].enable_debug

name2unicode = dict((unicode(key), unichr(htmlentitydefs.name2codepoint[key])) for key in htmlentitydefs.name2codepoint.keys())
name2unicode[u'apos'] = u"'"

decode_pattern = re.compile(r'&(#?[a-zA-Z0-9]+);') # more specific(\w is shorter but contains "_"), avoids matching "& jane; and won't skip "& jane&#039;s"

def decode(s):
    if not s:
        return u''
    def sub(m):
        if m.group(1).startswith(u'#'):
            if m.group(1)[1] == u'x':
                return unichr(int(text[3:-1], 16))
            return unichr(int(m.group(1)[1:]))
        elif name2unicode.has_key(m.group(1)):
            return name2unicode[m.group(1)]
        else:
            return u'' # false match(i.e. "&jane;") or unsupported named entity consider returning m.group(0)
    return decode_pattern.sub(sub, s)

def clean_safe(s):
    if not s:
        return ''
    try:
        o = smart_unicode(s)
        # remove any number of "amp;"
        #&amp;/&amp;amp; --> &
        #&amp;#XXX/&amp;amp;#XXX --> &#XXX
        #&amp;XXX/&amp;amp;XXX --> &XXX
        #&amp; jane&amp;&#039;s  -->  & jane&#039;s
        o = o.replace(u'amp;', u'')
        # remove &#XXX; &#xXXX; &XXX;
        o = decode(o)
        # remove \uXXX
        o = re.sub(r'\\u(....)', lambda m: unichr(int(m.group(1), 16)), o)
    except:
        if enable_debug:
            traceback.print_exc(file = sys.stdout)
        o = s
    return o

def unquote(s): # unquote
    if not s:
        return u''
    try:
        for key, value in entitydefs2.iteritems():
            s = s.replace(value, key)
    except:
        if enable_debug:
            traceback.print_exc(file = sys.stdout)
    return s

def quote(s): # quote
    if not s:
        return u''
    try:
        for key, value in entitydefs2.iteritems():
            s = s.replace(key, value)
    except:
        if enable_debug:
            traceback.print_exc(file = sys.stdout)
    return s2