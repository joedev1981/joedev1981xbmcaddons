# -*- coding: latin-1 -*-
import sys, os

import xbmc, xbmcplugin

from lib.common import inheritInfos
from lib.localparser import localParser
localParser = localParser()
from lib.remoteparser import remoteParser
remoteParser = remoteParser()

from lib.utils.fileUtils import clean_filename, saveList
from lib.utils.xbmcUtils import addListItem, addListItems
from lib.entities.CItemTypes import CItemTypes

mode = sys.modules["__main__"].mode
addon = sys.modules["__main__"].addon
__language__ = sys.modules["__main__"].__language__
rootDir = sys.modules["__main__"].rootDir
settingsDir = sys.modules["__main__"].settingsDir
cacheDir = sys.modules["__main__"].cacheDir
allsitesDir = sys.modules["__main__"].allsitesDir
resDir = sys.modules["__main__"].resDir
imgDir = sys.modules["__main__"].imgDir
catDir = sys.modules["__main__"].catDir

sort_dict = {
    u'label' : xbmcplugin.SORT_METHOD_LABEL, 
    u'size' : xbmcplugin.SORT_METHOD_SIZE, 
    u'duration' : xbmcplugin.SORT_METHOD_DURATION, 
    u'genre' : xbmcplugin.SORT_METHOD_GENRE, 
    u'rating' : xbmcplugin.SORT_METHOD_VIDEO_RATING, 
    u'date' : xbmcplugin.SORT_METHOD_DATE
}

def create_listItem(directory, type, items, infos, lItem, totalItems = 50):
    filename = type + u'.list'
    infos[u'url'] = os.path.join(directory, filename)
    addListItem(mode.selectLinkMode(infos), totalItems)
    return infos

def create_lists_and_listItems(directory, items_list, lItem, totalItems = 50):
    tmp_items = []
    for title, infos, items in items_list.files():
        tmp_items.append(create_list_and_listItem(directory, title, items, infos, lItem, totalItems))
    return tmp_items

def create_list_and_listItem(directory, type, items, infos, lItem, totalItems = 50):
    filename = type + u'.list'
    saveList(directory, filename, type, items)
    return create_listItem(directory, type, items, infos, lItem, totalItems = 50)

class parseView:
    def __init__(self, handle, lItem):
        self.handle = handle
        self.sort = [u'label', u'genre']
        self.links = CItemTypes()
        self.result = self.run(lItem)

    def createDirs(self, List):
        keys = [item[u'title'] for item in List]
        Dict = {}
        for i in range(len(keys)):
            key = keys.pop().lower().strip()
            value = List.pop()
            if key in Dict:
                Dict[key].append(value)
            else:
                Dict[key] = [value]
        keys1 = sorted(Dict.keys())
        keys1.reverse()
        keys2 = sorted(Dict.keys())
        keys2.reverse()
        while len(keys1)> 0:
            key1 = keys1.pop()
            for key2 in keys2:
                if key1 != key2:
                    if key2.startswith(key1):
                        if key1 not in self.links:
                            for item in Dict[key1]:
                                if not item[u'icon'].startswith(imgDir):
                                    tmp_infos = item
                                    break
                            else:
                                tmp_infos = Dict[key1][0]
                            self.links[key1] = (tmp_infos, Dict[key1])
                        self.links[key1] = (Dict[key2][0], Dict[key2])
                        keys1.remove(key2)
        return None

    def run(self, lItem):
        #loadLocal
        if mode == u'START':
            localParser.load_links(lItem)
            totalItems = len(localParser.links)
            tmp = {
                u'title': u' All Sites',
                u'type': u'rss',
                u'genre': u' Directory',
                u'director': u'VideoDevil',
                u'icon': os.path.join(imgDir, u'face_devil_grin.png'),
                u'url': u'sites.list'
            }
            addListItem(mode.selectLinkMode(inheritInfos(tmp, lItem)), totalItems)
            for link in localParser.links:
                addListItem(mode.selectLinkMode(link), totalItems)
        elif mode == u'VIEW_RSS' or mode == u'VIEW_SEARCH' or mode == u'VIEW_RSS_DIRECTORY':
            localParser.load_site(lItem)
            self.sort.extend(localParser.site.sort)
            remoteParser.main(((localParser.site, lItem),))
            type_dict = {}
            for type, infos, items in remoteParser.items.files():
                if type == u'next' or (mode == u'VIEW_RSS_DIRECTORY' and type == lItem[u'type']):
                    addListItems(items)
                else:
                    create_list_and_listItem(cacheDir, type, items, infos, lItem)
            for type, infos, items in localParser.site.links.files():
                if type not in remoteParser.items:
                    for item in items:
                        addListItem(mode.selectLinkMode(item), 0)
        elif mode == u'VIEW_DIRECTORY':
            localParser.load_links(lItem)
            totalItems = len(localParser.links)
            for link in localParser.links:
                addListItem(mode.selectLinkMode(link), totalItems)
        elif mode == u'VIEWALL_RSS' or mode == u'VIEWALL_SEARCH':
            localParser.load_links_and_sites_in_list(lItem)
            remoteParser.main(localParser.sites)
            for type, infos, items in remoteParser.items.files():
                if u'cfg' in infos:
                    del infos[u'cfg']
                if type == u'next':
                    create_list_and_listItem(cacheDir, type, items, infos, lItem)
                elif not os.path.isfile(os.path.join(allsitesDir, type + u'.list')):
                    create_list_and_listItem(allsitesDir, type, items, infos, lItem)
                else:
                    create_listItem(allsitesDir, type, items, infos, lItem)
            if not os.path.isfile(os.path.join(allsitesDir, u'search.list')):
                tmp_items = []
                for site, item in localParser.sites:
                    for type, infos, items in site.links.files():
                        if type == u'search':
                            tmp_items.extend(items)
                tmp_infos = tmp_items[0].copy()
                if u'cfg' in tmp_infos:
                    del tmp_infos[u'cfg']
                create_list_and_listItem(allsitesDir, u'search', tmp_items, tmp_infos, lItem)
        elif mode == u'VIEWALL_DIRECTORY':
            fileDir = os.path.join(allsitesDir, lItem[u'type'])
            if not os.path.exists(fileDir):
                os.mkdir(fileDir)
                localParser.load_links_and_sites_not_in_list(lItem)
                remoteParser.main(localParser.sites)
                for type, infos, items in remoteParser.items.files():
                    if u'cfg' in infos:
                        del infos[u'cfg']
                    if type == lItem[u'type']:
                        self.createDirs(items + localParser.links)
                        dir_items = create_lists_and_listItems(fileDir, self.links, lItem) 
                        if dir_items:
                            saveList(allsitesDir, lItem[u'type'] + u'.list', lItem[u'title'], dir_items)
            else:
                localParser.load_links(lItem)
                totalItems = len(localParser.links)
                for link in localParser.links:
                    addListItem(mode.selectLinkMode(link), totalItems)
        for sort_method in self.sort:
            xbmcplugin.addSortMethod(handle = self.handle, sortMethod = sort_dict[sort_method])
        return 0