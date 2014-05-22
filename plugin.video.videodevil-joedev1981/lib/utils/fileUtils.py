# -*- coding: latin-1 -*-

import sys, traceback
import os.path

from lib.common import smart_unicode

addon = sys.modules["__main__"].addon
__language__ = sys.modules["__main__"].__language__
rootDir = sys.modules["__main__"].rootDir
settingsDir = sys.modules["__main__"].settingsDir
cacheDir = sys.modules["__main__"].cacheDir
allsitesDir = sys.modules["__main__"].allsitesDir
resDir = sys.modules["__main__"].resDir
imgDir = sys.modules["__main__"].imgDir
catDir = sys.modules["__main__"].catDir
log = sys.modules["__main__"].log

def clean_filename(s):
    if not s:
        return u''
    badchars = u'\\/:*?\"<>|'
    for c in badchars:
        s = s.replace(c, u'_')
    return s;

def getFileExtension(filename):
    ext_pos = filename.rfind(u'.')
    if ext_pos != -1:
        return filename[ext_pos+1:]
    return None

def saveList(directory, filename, Listname, items = None, List_dict = None, file_mode = 'w'):
    f = open(str(os.path.join(directory, filename)), file_mode)
    Listname = (u'#' + Listname.center(54) + u'#\n').encode('utf-8')
    pound_signs = (u'########################################################\n').encode('utf-8')
    f.write(pound_signs)
    f.write(Listname)
    f.write(pound_signs)
    if List_dict != None:
        for info_name, info_value in List_dict.iteritems():
            f.write((u'site_' + info_name + u'=' + info_value + u'\n').encode('utf-8'))
        f.write(pound_signs)
    if items != None:
        for item in items:
            try:
                f.write((u'link_title=' + item[u'title'] + u'\n').encode('utf-8'))
            except KeyError:
                f.write(u'link_title=...\n'.encode('utf-8'))
            for info_name, info_value in item.iteritems():
                if info_name != u'url' and info_name != u'title':
                    f.write((u'link_' + info_name + u'=' + info_value + u'\n').encode('utf-8'))
            f.write((u'link_url=' + item[u'url'] + u'\n').encode('utf-8'))
            f.write(pound_signs)
    f.close()
    return

def smart_read_file(filename, shortcuts = True):
    for directory in [catDir, resDir, cacheDir, allsitesDir, '']:
        try:
            filepath = os.path.join(directory, filename)
            f = open(filepath, 'r')
            break
        except:
            if directory == '':
                traceback.print_exc(file = sys.stdout)
                log(u'File Not Found: "%s"' % filename)
                return None, None
    log(u'File Opened: "%s"' % filepath)
    key = []
    value = []
    for line in f:
        if line and line.startswith(u'#'):
            continue
        try:
            line = line.replace(u'\r\n', u'').replace(u'\n', u'')
        except:
            continue
        try:
            k, v = line.split(u'=', 1)
        except:
            continue
        if shortcuts and v.startswith(u'video.devil.'):
            idx = v.find(u'|')
            if v[:idx] == u'video.devil.locale':
                v = u'  ' + __language__(int(v[idx+1:])) + '  '
            elif v[:idx] == u'video.devil.image':
                v = os.path.join(imgDir, v[idx+1:])
            elif v[:idx] == u'video.devil.context':
                v = u'context.' + __language__(int(v[idx+1:]))
        key.append(k)
        value.append(v)
    key.reverse()
    value.reverse()
    f.close()
    log(u'File Closed: "%s"' % filepath)
    return key, value
