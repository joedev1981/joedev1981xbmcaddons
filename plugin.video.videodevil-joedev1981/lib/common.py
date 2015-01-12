import sys, traceback
def smart_unicode(s):
    if not s:
        return ''
    try:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), 'UTF-8')
        elif not isinstance(s, unicode):
            s = unicode(s, 'UTF-8')
    except UnicodeDecodeError:
        traceback.print_exc(file = sys.stdout)
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), 'ISO-8859-1')
        elif not isinstance(s, unicode):
            s = unicode(s, 'ISO-8859-1')
    return s

def inheritInfos(item, lItem): #consider replacing function with dict.copy()
    for k in lItem.keys():
        if k not in item:
            item[k] = lItem[k]
    return item