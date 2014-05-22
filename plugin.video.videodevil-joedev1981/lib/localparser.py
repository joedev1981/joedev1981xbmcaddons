# -*- coding: latin-1 -*-

import sys, traceback
import os.path
import re

from lib.common import smart_unicode, inheritInfos

from lib.entities.CItemTypes import CItemTypes

from lib.utils.fileUtils import smart_read_file, getFileExtension
from lib.utils.xbmcUtils import getSearchPhrase

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
enable_debug = sys.modules["__main__"].enable_debug
log = sys.modules["__main__"].log

class CItemInfo:
    def __init__(self):
        self.name = u''
        self.src = u'url'
        self.rule = u''
        self.default = u''
        self.build = u''

    def __str__(self):
        txt = [u'item_info_name=%s' % self.name]
        if self.src != u'url':
            txt.append(u'item_info_from=%s' % self.src)
        if self.rule != u'':
            txt.append(u'item_info=%s' % self.rule)
        if self.default != u'':
            txt.append(u'item_info_default=%s' % self.default)
        txt.append(u'item_info_build=%s' % self.build)
        return u'\n'.join(txt)


class CRuleItem:
    def __init__(self):
        self.infos = u''
        self.infosRE = u''
        self.order = []
        self.skill = u''
        self.curr = u''
        self.currRE = u''
        self.type = u''
        self.info_list = []
        self.actions = []
        self.url_build = u''

    def __str__(self):
        txt = [u'item_infos=%s' % self.infos]
        txt.append(u'item_order=%s' %  u'|'.join([k for k in self.order]))
        if self.skill != u'':
            txt.append(u'item_skill=%s' % self.skill)
        if self.curr != u'':
            txt.append(u'item_curr=%s' % self.curr)
        txt.append(u'item_type=%s' % self.type)
        if len(self.info_list) != 0:
            for info in self.info_list:
                txt.append(str(info))
        if len(self.actions) != 0:
            txt.append(u'item_infos_actions=%s' % u'|'.join([k for k in self.actions]))
        txt.append(u'item_url_build=%s' % self.url_build)
        return u'\n'.join(txt)


class CRuleSite:
    def __init__(self):
        self.start = u''
        self.txheaders = {
            u'User-Agent': u'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-GB; rv:1.8.1.18) Gecko/20081029 Firefox/2.0.0.18',
            u'Accept-Charset':u'ISO-8859-1,utf-8;q=0.7,*;q=0.7'
        }
        self.skill = u''
        self.sort = []
        self.startRE = u''
        self.cfg = None
        self.rules = []
        self.links = CItemTypes()

    def __str__(self):
        txt = [u'site_start=%s' % self.start]
        if len(self.txheaders) != 0: #needs to be fixed
            txt.append(u'site_header=%s' % u'|'.join([k for k in self.txheaders]))
        if self.skill != u'':
            txt.append(u'site_skill=%s' % self.skill)
        if len(self.sort) != 0:
            txt.append(u'site_sort=%s' % u'|'.join([k for k in self.sort]))
        if self.startRE != u'':
            txt.append(u'site_startRE=%s' % self.startRE)
        if self.cfg != None:
            txt.append(u'site_cfg=%s' % self.cfg)
        if len(self.rules) != 0:
            for rule in self.rules:
                txt.append(str(rule))
        if len(self.links) != 0:
            txt.append(str(self.links))
        if len(self.items) != 0:
            txt.append(str(self.items))
        return u'\n'.join(txt)



def loadLocal(lItem, search_phrase = None):
    def loadKey(txt):
        return keys[-1] == txt and keys.pop()
    site = None
    links = []
    keys, values = loadFile(lItem)
    ext = getFileExtension(lItem[u'url'])
    if ext == u'cfg' or ext == u'list':
        filename = lItem[u'url']
        if ext == u'cfg' and u'cfg' not in lItem:
            lItem[u'cfg'] = filename
    else:
        filename = lItem[u'cfg']
    if u'type' in lItem and lItem[u'type'] == u'search' and search_phrase == None:
        search_phrase = getSearchPhrase()
    while keys:
        old_line = len(keys)
        while keys and keys[-1].startswith(u'site_'):
            old_line = len(keys)
            if loadKey(u'site_start'):
                site = CRuleSite()
                if ext == u'cfg':
                    site.start = values.pop()
                else:
                    if lItem[u'type'] == u'search':
                        lItem[u'url'] = lItem[u'url'] % search_phrase
                    site.start = lItem[u'url']
                    del values[-1]
                if site.cfg == None and ext == u'cfg':
                    site.cfg = filename
                elif u'cfg' in lItem:
                    site.cfg = lItem[u'cfg']
            if loadKey(u'site_header'):
                headers = values.pop().split(u'|')
                site.txheaders[headers[0]] = headers[1]
            if loadKey(u'site_skill'):
                site.skill = values.pop()
                skill_file = filename[:filename.find(u'.')] + u'.lnk'
                if site.skill.find(u'redirect') != -1:
                    try:
                        f = open(str(os.path.join(resDir, skill_file)), 'r')
                    except IOError:
                        pass
                    else:
                        forward_cfg = f.read()
                        f.close()
                        if forward_cfg != filename:
                            lItem[u'url'] = forward_cfg
                            lItem[u'cfg'] = forward_cfg
                            return loadLocal(lItem)
                elif site.skill.find(u'store') != -1:
                    f = open(str(os.path.join(resDir, skill_file)), 'w')
                    f.write(filename)
                    f.close()
            if loadKey(u'site_sort'):
                if values[-1].find(u'|') != -1:
                    site.sort.extend(values.pop().split(u'|'))
                else:
                    site.sort.append(values.pop())
            if loadKey(u'site_startRE'):
                site.startRE = values.pop()
            if loadKey(u'site_cfg'):
                site.cfg = values.pop()
            if len(keys) == old_line:
                log(u'Syntax Error: "%s" is invalid.' % filename)
                del keys[-1]
        while keys and keys[-1].startswith(u'item_'):
            old_line = len(keys)
            if loadKey(u'item_infos'):
                rule_tmp = CRuleItem()
                rule_tmp.infos = values.pop()
            if loadKey(u'item_order'):
                if values[-1].find(u'|') != -1:
                    rule_tmp.order.extend(values.pop().split(u'|'))
                else:
                    rule_tmp.order.append(values.pop())
            if loadKey(u'item_skill'):
                rule_tmp.skill = values.pop()
            if loadKey(u'item_curr'):
                rule_tmp.curr = values.pop()
            if loadKey(u'item_type'):
                rule_tmp.type = values.pop()
            while keys and keys[-1].startswith(u'item_info_'):
                old_line = len(keys)
                if loadKey(u'item_info_name'):
                    info_tmp = CItemInfo()
                    if values[-1].startswith(u'video.devil.context'):
                        values[-1] = u'context.' + __language__(int(values[-1][20:]))
                    info_tmp.name = values.pop()
                if loadKey(u'item_info_from'):
                    info_tmp.src = values.pop()
                if loadKey(u'item_info'):
                    info_tmp.rule = values.pop()
                if loadKey(u'item_info_default'):
                    info_tmp.default = values.pop()
                if loadKey(u'item_info_build'):
                    if values[-1].startswith(u'video.devil.'):
                        if values[-1].startswith(u'video.devil.locale'):
                            values[-1] = u'  ' + __language__(int(values[-1][19:])) + u'  '
                        elif values[-1].startswith(u'video.devil.image'):
                            values[-1] = os.path.join(imgDir, values[-1][18:])
                    info_tmp.build = values.pop()
                    rule_tmp.info_list.append(info_tmp)
                    info_tmp = None
                if len(keys) == old_line:
                    log(u'Syntax Error: "%s" is invalid.' % filename)
                    del keys[-1]
            if loadKey(u'item_infos_actions'):
                if values[-1].find(u'|') != -1:
                    rule_tmp.actions.extend(values.pop().split(u'|'))
                else:
                    rule_tmp.actions.append(values.pop())
            if loadKey(u'item_url_build'):
                rule_tmp.url_build = values.pop()
                if mode == u'VIEWALL_RSS' or mode == u'VIEWALL_SEARCH':
                    if rule_tmp.type.startswith(u'video') or rule_tmp.type == u'next':
                        site.rules.append(rule_tmp)
                    elif rule_tmp.type == u'category' and not os.path.isfile(os.path.join(allsitesDir, rule_tmp.type + u'.list')):
                        site.rules.append(rule_tmp)
                elif mode == u'VIEW_DIRECTORY':
                    if rule_tmp.type == u'category' and not os.listdir(os.path.join(allsitesDir, rule_tmp.type)):
                        site.rules.append(rule_tmp)
                else:
                    site.rules.append(rule_tmp)
                rule_tmp = None
            if len(keys) == old_line:
                log(u'Syntax Error: "%s" is invalid.' % filename)
                del keys[-1]
        while keys and keys[-1].startswith(u'link_'):
            old_line = len(keys)
            if loadKey(u'link_title'):
                tmp = {}
                if values[-1].startswith(u'video.devil.locale'):
                    values[-1] = u'  ' + __language__(int(values[-1][19:])) + u'  '
                tmp[u'title'] = values.pop()
            while tmp != None and keys[-1] != u'link_url':
                if values[-1].startswith(u'video.devil.image'):
                    values[-1] = os.path.join(imgDir, values[-1][18:])
                tmp[keys[-1][5:]] = values.pop()
                del keys[-1]
            if loadKey(u'link_url'):
                tmp[u'url'] = values.pop()
                if filename == u'sites.list':
                    if addon.getSetting(tmp[u'title']) == u'true':
                        tmp[u'cfg'] = tmp[u'url']
                        links.append(tmp)
                else:
                    tmp = inheritInfos(tmp, lItem)
                    if site != None:
                        if ext == u'cfg' and tmp[u'type'] == u'once':
                            tmp[u'type'] = u'links'
                        site.links[tmp[u'type']] = (tmp, [tmp])
                    else:
                        links.append(tmp)
                tmp = None
                break
            if len(keys) == old_line:
                log(u'Syntax Error: "%s" is invalid.' % filename)
                del keys[-1]
        if len(keys) == old_line:
            log(u'Syntax Error: "%s" is invalid.' % filename)
            del keys[-1]
    if site != None:
        return site
    return links

def loadFile(lItem):
    ext = getFileExtension(lItem[u'url'])
    if ext == u'cfg' or ext == u'list':
        filename = lItem[u'url']
    else:
        filename = lItem[u'cfg']
    for directory in [resDir, cacheDir, allsitesDir, catDir, '']:
        try:
            f = open(os.path.join(directory, filename), 'r')
        except IOError:
            pass
        else:
            data = smart_unicode(f.read())
            f.close()
            data = data.splitlines()
            keys = []
            values = []
            for line in reversed(data):
                if line and not line.startswith(u'#'):
                    key, value = line.split(u'=', 1)
                    keys.append(key)
                    values.append(value)
            return keys, values
    else:
        traceback.print_exc(file = sys.stdout)
        log(u'File Not Found: "%s"' % filename)
        raise


class localParser:
    def __init__(self):
        self.all_cfg_items = None
        self.cfg_items_in_list = []
        self.cfg_items_not_in_list = []
        self.search_phrase = None
        self.site = None
        self.sites = []
        self.links = []

    def resetLinks(self):
        tmp = []
        tmp, self.links = self.links, tmp
        return tmp

    def resetSites(self):
        tmp = []
        tmp, self.sites = self.sites, tmp
        return tmp

    def reset(self):
        self.resetLinks()
        self.resetSites()
        return None

    def load_site(self, lItem = {u'url': u'sites.list'}):
        self.site = loadLocal(lItem)
        return self.site

    def load_links(self, lItem = {u'url': u'sites.list'}):
        self.links = loadLocal(lItem)
        return self.links

    def load_all_sites_links(self, lItem = {u'url': u'sites.list'}):
        self.all_sites_links = loadLocal(lItem)
        return None

    def load_links_and_all_sites_links(self, lItem):
        self.load_all_sites_links()
        self.load_links(lItem)
        return None

    def load_links_and_sites_in_list(self, lItem):
        self.load_links(lItem)
        if u'type' in lItem and lItem[u'type'] == u'category':
            sites_in_list = set([link[u'cfg'] for link in self.links])
            search_links = loadLocal({u'url': u'search.list'})
            search_as_category_links = [link for link in search_links if link[u'cfg'] not in sites_in_list]
            search_phrase = lItem[u'title'].strip(u' ').lower()
            search_as_category_sites = [loadLocal(link, search_phrase) for link in search_as_category_links]
            sites = map(loadLocal, self.links) + search_as_category_sites
            self.links += search_as_category_links
            self.sites = zip(sites, self.links)
        else:
            self.sites = zip(map(loadLocal, self.links), self.links)
        return None

    def load_links_and_sites_not_in_list(self, lItem):
        self.load_links_and_all_sites_links(lItem)
        sites_in_list = set([link[u'cfg'] for link in self.links])
        self.cfg_links_not_in_list = [link for link in self.all_sites_links if link[u'cfg'] not in sites_in_list]
        for link in self.cfg_links_not_in_list:
            site = loadLocal(link)
            for type, infos, links in site.links.files():
                if type == self.links[0][u'type']:
                    site.start = links[0][u'url']
                    self.sites.append((site, links[0]))
                    break
        return None