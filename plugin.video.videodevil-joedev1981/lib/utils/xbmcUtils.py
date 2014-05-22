# -*- coding: latin-1 -*-

import sys, os, traceback
import xbmc, xbmcgui, xbmcplugin

from lib.common import inheritInfos
from lib.utils.encodingUtils import clean_safe, smart_unicode

mode = sys.modules["__main__"].mode
addon = sys.modules["__main__"].addon
__language__ = sys.modules["__main__"].__language__
imgDir = sys.modules["__main__"].imgDir

def getKeyboard(default = u'', heading = u'', hidden = False):
    kboard = xbmc.Keyboard(default, heading, hidden)
    kboard.doModal()
    if kboard.isConfirmed():
        return kboard.getText()
    return u''

def getSearchPhrase():
    try:
        curr_phrase = addon.getSetting(u'curr_search')
    except:
        addon.setSetting(u'curr_search', u'')
        curr_phrase = u''
    search_phrase = getKeyboard(default = curr_phrase, heading = __language__(30102))
    addon.setSetting(u'curr_search', search_phrase)
    return search_phrase.replace(u' ', u'+')

def addListItems(items):
#    map(addListItem, map(mode.selectItemMode, items))
    for item in items:
        addListItem(mode.selectItemMode(item), len(items))
    return None

def addListLinks(items):
    map(addListItem, map(mode.selectLinkMode, items))
    return None

exclusions = [u'url', u'title', u'icon', u'type', u'extension', u'duration']
base_url = unicode(sys.argv[0]) + u'?' 
def addListItem(item, totalItems = 0):
    if item[u'type'] != u'once':
        url = base_url + codeUrl(item)
        liz = xbmcgui.ListItem(item[u'title'], item[u'title'], item[u'icon'], item[u'icon'])
        context_menu_items = []
        if item[u'type'] == u'video':
            action = u'XBMC.RunPlugin(%s&mode=%d)' % (url, mode[u'DOWNLOAD'])
            context_menu_items.append((__language__(30007), action))
        for info_name, info_value in item.iteritems():
            if info_name.startswith(u'context.'):
                cItem = {}
                cItem[u'url'] = info_value
                cItem = inheritInfos(cItem, item)
                action = u'XBMC.RunPlugin(%s)' % (sys.argv[0] + u'?' + codeUrl(cItem))
                context_menu_items.append((info_name[8:], action))
            elif info_name not in exclusions:
                if info_name.endswith(u'.int'):
                    liz.setInfo(u'Video', infoLabels = {info_name[:-4]: int(info_value)})
                elif info_name.endswith(u'.once'):
                    liz.setInfo(u'Video', infoLabels = {info_name[:-5]: info_value})
                else:
                    liz.setInfo(u'Video', infoLabels = {info_name: info_value})
        liz.addContextMenuItems(context_menu_items)
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, liz, True, totalItems)
    return None

def codeUrl(item):
    # in Frodo url parameters need to be encoded
    # ignore characters that can't be converted to ascii
    params = [info_name + u'=' + info_value.replace(u'&', u'%26') for info_name, info_value in item.iteritems() if not info_name.endswith(u'.once')]
    params = u'&'.join(params)
    return params