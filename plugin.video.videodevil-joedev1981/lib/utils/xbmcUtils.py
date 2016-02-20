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

exclusions = [u'url', u'title', u'icon', u'type', u'extension', u'duration']
base_url = unicode(sys.argv[0]) + u'?'

def addListItems(items, rule_type = None, lItem = None, totalItems = 50):
    #need to run time tests
    if rule_type != None and lItem != None:
        if rule_type != u'once':
            base_url = unicode(sys.argv[0]) + u'?mode=' + unicode(mode.selectItemMode({u'type': rule_type})[u'mode']) + u'&'
            inherited = [(info_name, lItem[info_name]) for info_name in lItem.keys() if info_name not in items[0].keys()]
            if inherited:
                base_url += codeUrl(dict(inherited)) + u'&'
            lizs = [(base_url + codeUrl(item), xbmcgui.ListItem(item[u'title'], item[u'title'], item[u'icon'], item[u'icon']), True) for item in items]
            if rule_type == u'video':
                name = __language__(30007)
                context_menus = [[(name, u'XBMC.RunPlugin(%s&mode=%d)' % (liz[0], mode[u'DOWNLOAD']))] for liz in lizs]
            else:
                context_menus = [[] for liz in lizs]
            for info_name in items[0].keys():
                if info_name not in exclusions:
                    if info_name.startswith(u'context.'):
                        name = info_name[8:]
                        for i, item in enumerate(items):
                            cItem = item.copy()
                            cItem[u'url'] = item[info_name]
                            context_menus[i].append((name, u'XBMC.RunPlugin(%s)' % (base_url + codeUrl(cItem))))
                    else:
                        if info_name.endswith(u'.int'):
                            name = info_name[:-4]
                            for i, item in enumerate(items):
                                lizs[i][1].setInfo(u'Video', infoLabels = {name: int(item[info_name])})
                        elif info_name.endswith(u'.once'):
                            name = info_name[:-4]
                            for i, item in enumerate(items):
                                lizs[i][1].setInfo(u'Video', infoLabels = {name: item[info_name]})
                        else:
                            for i, item in enumerate(items):
                                lizs[i][1].setInfo(u'Video', infoLabels = {info_name: item[info_name]})
            for i, item in enumerate(items):
                lizs[i][1].addContextMenuItems(context_menus[i])
            xbmcplugin.addDirectoryItems(int(sys.argv[1]), lizs, totalItems)
    else:
#       map(addListItem, map(mode.selectItemMode, items))
        for item in items:
            addListItem(mode.selectItemMode(item), len(items))
    return None

def addListLinks(items):
    map(addListItem, map(mode.selectLinkMode, items))
    return None

def addListItem(item, totalItems = 50):
    if item[u'type'] != u'once':
        url = base_url + codeUrl(item)
        liz = xbmcgui.ListItem(item[u'title'], item[u'title'], item[u'icon'], item[u'icon'])
        if item[u'type'] == u'video':
            context_menu = [(__language__(30007), u'XBMC.RunPlugin(%s&mode=%d)' % (url, mode[u'DOWNLOAD']))]
        else:
            context_menu = []
        for info_name, info_value in item.iteritems():
            if info_name.startswith(u'context.'):
                cItem = item.copy()
                cItem[u'url'] = info_value
                context_menu.append((info_name[8:], u'XBMC.RunPlugin(%s)' % (base_url + codeUrl(cItem))))
            elif info_name not in exclusions:
                if info_name.endswith(u'.int'):
                    liz.setInfo(u'Video', infoLabels = {info_name[:-4]: int(info_value)})
                elif info_name.endswith(u'.once'):
                    liz.setInfo(u'Video', infoLabels = {info_name[:-5]: info_value})
                else:
                    liz.setInfo(u'Video', infoLabels = {info_name: info_value})
        liz.addContextMenuItems(context_menu)
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, liz, True, totalItems)
    return None

def codeUrl(item):
    return u'&'.join((info_name + u'=' + info_value.replace(u'&', u'%26') for info_name, info_value in item.iteritems() if not info_name.endswith(u'.once')))