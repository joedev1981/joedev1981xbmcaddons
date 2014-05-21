# -*- coding: latin-1 -*-
#from string import capitalize, lower
import sys, os.path
import os, traceback
import re
import urllib, urllib2
import cookielib
import threading
import Queue

import xbmc

from lib.common import inheritInfos, smart_unicode

from lib.utils.encodingUtils import clean_safe
from lib.utils.xbmcUtils import addListItem, addListItems

from lib.entities.CItemTypes import CItemTypes

import sesame

mode = sys.modules["__main__"].mode
addon = sys.modules["__main__"].addon
__language__ = sys.modules["__main__"].__language__
rootDir = sys.modules["__main__"].rootDir
settingsDir = sys.modules["__main__"].settingsDir
cacheDir = sys.modules["__main__"].cacheDir
resDir = sys.modules["__main__"].resDir
imgDir = sys.modules["__main__"].imgDir
catDir = sys.modules["__main__"].catDir
enable_debug = sys.modules["__main__"].enable_debug
log = sys.modules["__main__"].log

urlopen = urllib2.urlopen
cj = cookielib.LWPCookieJar()
Request = urllib2.Request

if cj != None:
    if os.path.isfile(xbmc.translatePath(os.path.join(settingsDir, u'cookies.lwp'))):
        cj.load(xbmc.translatePath(os.path.join(settingsDir, u'cookies.lwp')))
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
else:
    opener = urllib2.build_opener()
    urllib2.install_opener(opener)

def parseActions(item, convActions, url = None):
    for convAction in convActions:
        if convAction.find(u'(') != -1:
            action = convAction[0:convAction.find(u'(')]
            param = convAction[len(action) + 1:-1]
            if param.find(u', ') != -1:
                params = param.split(u', ')
                if action == u'replace':
                    item[params[0]] = item[params[0]].replace(params[1], params[2])
                elif action == u'join':
                    j = []
                    for i in range(1, len(params)):
                        j.append(item[params[i]])
                    item[params[1]] = params[0].join(j)
                elif action == u'decrypt':
                    item[u'match'] = sesame.decrypt(item[params[0]], item[params[1]], 256)
            else:
                if action == u'unquote':
                    item[param] = urllib.unquote(item[param])
                elif action == u'quote':
                    item[param] = urllib.quote(item[param])
                elif action == u'decode':
                    item[param] = decode(item[param])
        else:
            action = convAction
            if action == u'append':
                item[u'url'] = url + item[u'url']
            elif action == u'appendparam':
                if url[-1] == u'?':
                    item[u'url'] = url + item[u'url']
                else:
                    item[u'url'] = url + u'&' + item[u'url']
            elif action == u'replaceparam':
                if url.rfind(u'?') == -1:
                    item[u'url'] = url + u'?' + item[u'url']
                else:
                    item[u'url'] = url[:url.rfind(u'?')] + u'?' + item[u'url']
            elif action == u'striptoslash':
                if url.rfind(u'/'):
                    idx = url.rfind(u'/')
                    if url[:idx + 1] == u'http://':
                        item[u'url'] = url + u'/' + item[u'url']
                    else:
                        item[u'url'] = url[:idx + 1] + item[u'url']
    return item

def fetchHTML(site, lItem):
    req = Request(site.start, None, site.txheaders)
    try:
        handle = urlopen(req)
    except:
        if enable_debug:
            traceback.print_exc(file = sys.stdout)
        return u'Skipping due to failure'
    data = handle.read()
    handle.close()
    return site, lItem, data


def loadRemote(site, lItem, data):
    if enable_debug:
        f = open(os.path.join(cacheDir, site.cfg + u'.page.html'), 'w')
        f.write(u'<Title>'+ site.start + u'</Title>\n\n')
        f.write(data)
        f.close()
    items = CItemTypes()
    data = smart_unicode(data)
    if mode == u'VIEWALL_DIRECTORY':
        lock = [u'video']
    else:
        lock = []
    for item_rule in site.rules:
        rule_items, tmp_rule_items = [], []
        if item_rule.type in lock:
            continue
        elif item_rule.skill.find(u'recursive') != -1:  #Need to fix this
            site.start = tmp[u'url']
            loadRemote(site, lItem, fetchHTML(site, lItem)[2])
            tmp = None
        else:
            item_rule.infosRE = re.compile(item_rule.infos, re.IGNORECASE + re.DOTALL + re.MULTILINE)
            reInfos = item_rule.infosRE.findall(data)
            if len(reInfos) >= 1:
                if item_rule.type != u'video':
                    lock.append(item_rule.type)
                tmp_rule_items = [dict(zip(item_rule.order, infos_values)) for infos_values in reInfos]
                for info in item_rule.info_list:
                    if info.name in item_rule.order:
                        if info.build.find(u'%s') != -1:
                            for tmp in tmp_rule_items:
                                tmp[info.name] = info.build % tmp[info.name]
                    elif info.rule != u'':
                        for tmp in tmp_rule_items:
                            info_rule = info.rule
                            if info.rule.find(u'%s') != -1:
                                info_rule = info.rule % tmp[info.src]
                            infosearch = re.search(info_rule, data)
                            if infosearch:
                                tmp[info.name] = info.build % infosearch.group(1).strip()
                            elif info.default != u'':
                                tmp[info.name] = info.default
                    else:
                        if info.build.find(u'%s') != -1:
                            for tmp in tmp_rule_items:
                                tmp[info.name] = info.build % tmp[info.src]
                        else:
                            for tmp in tmp_rule_items:
                                tmp[info.name] = info.build
                if len(item_rule.actions) > 0:
                    for tmp in tmp_rule_items:
                        tmp = parseActions(tmp, item_rule.actions, site.start)
                for tmp in tmp_rule_items:
                    tmp[u'url'] = item_rule.url_build % tmp[u'url']
                    tmp[u'type'] = item_rule.type
                for i, tmp in enumerate(tmp_rule_items):
                    for item in tmp_rule_items[i + 1:]:
                        if tmp[u'url'] == item[u'url']:
                            break
                    else:
                        rule_items.append(tmp)
                infoFormatter(rule_items, item_rule.order + [info.name for info in item_rule.info_list])
                if item_rule.skill.find(u'space') != -1:
                    for item in rule_items:
                        item[u'title'] = u'   ' + item[u'title'] + u'   '
                elif item_rule.skill.find(u'bottom') == -1:
                    for item in rule_items:
                        item[u'title'] = u' ' + item[u'title'] + u' '
            if item_rule.curr:
                item_rule.currRE = re.compile(item_rule.curr, re.IGNORECASE + re.DOTALL + re.MULTILINE)
                reCurr = item_rule.currRE.findall(data)
                if len(reCurr) >= 1:
                    lock.append(item_rule.type)
                for infos_value in reCurr:
                    tmp = currBuilder(site, item_rule, lItem, site.start, infos_value = infos_value)
                    for item in rule_items:
                        if tmp[u'url'] == item[u'url']:
                            break
                    else:
                        rule_items.append(tmp)
            if rule_items:
                if item_rule.type == u'video':
                    addListItems([inheritInfos(item, lItem) for item in rule_items])
                else:
                    tmp_infos = {}
                    tmp_infos[u'type'] = item_rule.type
                    for info in item_rule.info_list:
                        if info.name == u'title':
                            tmp_infos[u'title'] = info.build
                        elif info.name == u'icon':
                            tmp_infos[u'icon'] = info.build
                    items[item_rule.type] = (inheritInfos(tmp_infos, lItem), [inheritInfos(item, lItem) for item in rule_items])
    return items

# Helper functions for loadRemote
def currBuilder(site, rule, lItem, url, match = None, infos_value = None):
    if infos_value == None:
        title = match.group(1).strip()
    else:
        title = infos_value.strip()
    tmp = {}
    if rule.skill.find(u'space') != -1:
        tmp[u'title'] = u'   ' + title + u' (' + __language__(30106) + u')   '
    else:
        tmp[u'title'] = u'  ' + title + u' (' + __language__(30106) + u')  '
    tmp[u'url'] = url
    tmp[u'type'] = rule.type
    for info in rule.info_list:
        if info.name == u'icon':
            tmp[u'icon'] = info.build
    return tmp

def infoFormatter(items, infos):
    if u'title' in infos:
        for item in items:
            if item[u'title'] != u'':
                item[u'title'] = clean_safe(item[u'title'].replace(u'\r\n', u'').replace(u'\n', u'').replace(u'\t', u''))
                item[u'title'] = item[u'title'].lstrip(u' -@#$%^&*_-+=.,\';:"\|/?`~>)]}!u')
                item[u'title'] = item[u'title'].rstrip(u' -@#$%^&*_-+=.,;:\'"\|/?`~<([{')
                item[u'title'] = item[u'title'].title()
            else:
                item[u'title'] = u' ... '
    if u'duration' in infos:
        for item in items:
            item[u'duration'] = item[u'duration'].strip(u' ()')
            if item[u'duration'][-2] == u':':
                item[u'duration'] = item[u'duration'][:-2] + u'0' + item[u'duration'][-2:]
            item[u'title'] = item[u'title'] + u' (' +  item[u'duration'] + u')'
    if u'icon' in infos:
        for item in items:
            if item[u'icon'] == u'':
                item[u'icon'] = os.path.join(imgDir, u'video.png')
    for info in infos:
        if info.endswith(u'.tmp'):
            for item in items:
                del item[info]
    return items

class ThreadUrl(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, fetch_queue, parse_queue, continuous = False):
        threading.Thread.__init__(self)
        self.fetch_queue = fetch_queue
        self.parse_queue = parse_queue
        self.continuous = continuous

    def run(self):
        args = self.fetch_queue.get()
        site, lItem = args
        results = fetchHTML(site, lItem)
        self.parse_queue.put(results)
        self.fetch_queue.task_done()
        while self.continuous:
            args = self.fetch_queue.get()
            if isinstance(args, str) and args == u'quit':
                self.continuous = False
            else:
                site, lItem = args
                results = fetchHTML(site, lItem)
                self.parse_queue.put(results)
            self.fetch_queue.task_done()

class remoteParser:
    def __init__(self):
        self.fetch_queue = None
        self.parse_queue = None
        self.fetch_threads = []
        self.task_count = 0
        self.items = CItemTypes()

    def start_fetch_threads(self):
        for fetch_thread in self.fetch_threads:
            fetch_thread.start()

    def kill_fetch_threads(self):
        for fetch_thread in self.fetch_threads:
            self.fetch_queue.put(u'quit')

    def populate_fetch_queue(self, tasks):
        for task in tasks:
            self.fetch_queue.put(task)

    def wait_for_fetch_queue(self):
        self.fetch_queue.join()

    def wait_for_parse_queue(self):
        self.parse_queue.join()

    def spawn_fetch_threads(self, count): #by default thread does not loop continuously set 3rd arg to True loop continuously
        for i in range(count):
            fetch_thread = ThreadUrl(self.fetch_queue, self.parse_queue)
            fetch_thread.setDaemon(True)
            self.fetch_threads.append(fetch_thread)

    def remoteDataMiner(self):
        for i in range(self.task_count):
            args = self.parse_queue.get()
            if isinstance(args, str) and args == u'Skipping due to failure':
                log(u'Skipping due to failure')
            else:
                site, lItem, data = args
                items = loadRemote(site, lItem, data)
                for type, infos, items in items.files():
                    self.items[type] = (infos, items)
            self.parse_queue.task_done()

    def main(self, tasks):
        self.task_count += len(tasks)
        if len(tasks) > 1:
            self.fetch_queue = Queue.Queue()
            self.parse_queue = Queue.Queue()
            self.spawn_fetch_threads(len(tasks))
            self.start_fetch_threads()
            self.populate_fetch_queue(tasks)
#            self.kill_fetch_threads()
            self.remoteDataMiner()
            self.wait_for_fetch_queue()
            self.wait_for_parse_queue()
        elif len(tasks) == 1:
            args = fetchHTML(*tasks[0])
            if isinstance(args, str) and args == u'Skipping due to failure':
                log(u'Skipping due to failure')
            else:
                self.items = loadRemote(*args)
        cj.save(os.path.join(settingsDir, u'cookies.lwp'))
        return self.items