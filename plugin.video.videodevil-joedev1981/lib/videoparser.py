# -*- coding: latin-1 -*-

import sys, traceback
import os
import re
import urllib, urllib2
import cookielib

import xbmc, xbmcgui

from lib.common import inheritInfos, smart_unicode

from lib.utils.encodingUtils import clean_safe, decode
from lib.utils.fileUtils import smart_read_file
import sesame

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
USERAGENT = u'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-GB; rv:1.8.1.18) Gecko/20081029 Firefox/2.0.0.18'

urlopen = urllib2.urlopen
cj = cookielib.MozillaCookieJar(xbmc.translatePath(os.path.join(settingsDir, 'cookies.txt')))
Request = urllib2.Request

if cj != None:
    try:
        cj.load()
    except IOError as e:
        if e.errno == errno.ENOENT:
            log('Error loading cookies from file: "%s"' % os.path.join(settingsDir, 'cookies.txt'))
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
else:
    opener = urllib2.build_opener()
urllib2.install_opener(opener)

def parseActions(item, convActions, url = None):
    for convAction in convActions:
        if convAction.find(u"(") != -1:
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
#            elif action == u'space':
#                try:
#                    item[u'title'] = u'  ' + item[u'title'].strip(u' ') + u'  '
#                except:
#                    pass
    return item

class CCatcherRuleItem:
    def __init__(self):
        self.target = None
        self.actions = []
        self.dkey = None
        self.dkey_actions = []
        self.info = None
        self.player = None
        self.extension = u'flv'
        self.quality = u'standard'
        self.build = None
        self.type = u'video'
        self.priority = 0


class CCatcherRuleSite:
    def __init__(self):
        self.url = u''
        self.startRE = None
        self.stopRE = None
        self.txheaders = {'User-Agentu':USERAGENT}
        self.limit = 0
        self.data = u''
        self.rules = []


class CCatcherList:
    def __init__(self, lItem):
        self.status = {}
        self.key = []
        self.value = []
        self.skill = u''
        self.player = None
        self.sites = []
        self.urlList = []
        self.extensionList = []
        self.selectionList = []
        self.decryptList = []
        self.playerList = []
        self.videoExtension = u'.flv'
        self.dkey = None
        self.link = None
        self.videoItem = self.getDirectLink(lItem)

    def getDirectLink(self, lItem):
        if u'catcher' in lItem:
            filename = lItem[u'catcher']
        else:
            netloc = lItem[u'url'].replace(u'//', u'/').split(u'/')[1].replace(u'www.', u'')
            idx = 0
            for i in range(netloc.count(u'.')):
                name = netloc[idx:]
                if os.path.isfile(os.path.join(catDir, name + u'.catcher')):
                    filename =  name + u'.catcher'
                    break
                idx += name.find(u'.') + 1
            else:
                name = lItem[u'cfg'][:-3] + u'catcher'
                if os.path.isfile(os.path.join(catDir, name)):
                    filename = name
                else:
                    filename = u'simple-match.catcher'
        self.loadCatcher(filename)
        redirected = self.parseVideoPage(lItem[u'url'])
        if redirected != None:
            return redirected.videoItem
        if self.link == None and len(self.urlList) > 0:
            self.selectLink()
#        if self.link != None:
#            tmp = {
#                u'url': self.link,
#                u'extension': self.videoExtension
#                }
#            if self.player != None:
#                tmp[u'player'] = self.player
#            tmp = inheritInfos(tmp, lItem)
#            return tmp
#        elif len(self.urlList) > 0:
#            self.selectLink()
        if self.link != None:
            tmp = {
                u'url': self.link,
                u'extension': self.videoExtension
                }
            if self.player != None:
                tmp[u'player'] = self.player
            tmp = inheritInfos(tmp, lItem)
            return tmp
        return None

    def loadCatcher(self, filename):
        del self.key[:]
        del self.value[:]
        self.key, self.value = smart_read_file(filename)
        if self.key == None and self.value == None:
            return None
        site = None
        rule = None
        while self.key:
            old_line = len(self.key)
            if self.loadKey(u'url'):
                if site:
                    self.sites.append(site)
                site = CCatcherRuleSite()
                site.url = self.value.pop()
            if self.loadKey(u'data'):
                site.data = self.value.pop()
            if self.loadKey(u'header'):
                index = self.value[-1].find(u'|')
                site.txheaders[self.value[-1][:index]] = self.value[-1][index+1:]
                del self.value[-1]
            if self.loadKey(u'limit'):
                site.limit = int(self.value.pop())
            if self.loadKey(u'startRE'):
                site.startRE = self.value.pop()
            if self.loadKey(u'stopRE'):
                site.stopRE = self.value.pop()
            while self.key:
                old_line = len(self.key)
                if self.loadKey(u'target'):
                    if rule:
                        site.rules.append(rule)
                    rule = CCatcherRuleItem()
                    rule.target = smart_unicode(self.value.pop())
                if self.loadKey(u'quality'):
                    rule.quality = self.value.pop()
                    continue
                if self.loadKey(u'priority'):
                    rule.priority = int(self.value.pop())
                    continue
                if self.loadKey(u'type'):
                    rule.type = self.value.pop()
                    if rule.type == u'forward' or rule.type.startswith(u'redirect'):
                        site.rules.append(rule)
                        rule = None
                        break
                else:
                    if self.loadKey(u'actions'):
                        if self.value[-1].find(u'|') != -1:
                            rule.actions.extend(self.value.pop().split(u'|'))
                        else:
                            rule.actions.append(self.value.pop())
                    if self.loadKey(u'build'):
                        rule.build = self.value.pop()
                    if self.loadKey(u'dkey'):
                        rule.dkey = smart_unicode(self.value.pop())
                        if self.loadKey(u'dkey_actions'):
                            if self.value[-1].find(u'|') != -1:
                                rule.dkey_actions.extend(self.value.pop().split(u'|'))
                            else:
                                rule.dkey_actions.append(self.value.pop())
                    if self.loadKey(u'extension'):
                        rule.extension = self.value.pop()
                    if self.loadKey(u'info'):
                        rule.info = self.value.pop()
                    if self.loadKey(u'player'):
                        rule.player = self.value.pop()
                if len(self.key) == old_line:
                    log(u'Syntax Error:\n"%s" is invalid.' % self.filename)
            if len(self.key) == old_line:
                log(u'Syntax Error:\n"%s" is invalid.' % self.filename)
        if rule != None:
            site.rules.append(rule)
        self.sites.append(site)
        return None

    def loadKey(self, txt):
        if self.key[-1] == txt:
            del self.key[-1]
            return True
        return False

    def parseVideoPage(self, url):
        video_found = False
        for index, site in enumerate(self.sites):
            if video_found:
                break
            # Download website
            if site.data == u'':
                if site.url.find(u'%') != -1:
                    url = site.url % url
                req = Request(url, None, site.txheaders)
                urlfile = opener.open(req)
                if site.limit == 0:
                    data = urlfile.read()
                else:
                    data = urlfile.read(site.limit)
            else:
                data_url = site.data % url
                req = Request(site.url, data_url, site.txheaders)
                response = urlopen(req)
                if site.limit == 0:
                    data = response.read()
                else:
                    data = response.read(site.limit)
            if enable_debug:
                f = open(os.path.join(cacheDir, 'site.html'), 'w')
                f.write(u'<Titel>'+ url + u'</Title>\n\n')
                f.write(data)
                f.close()

            if site.startRE:
                start = data.find(site.startRE.encode('utf-8'))
                if start == -1:
                    log(u'startRe not found for %s' % url)
                else:
                    data = data[start:]
                    if site.stopRE:
                        stop = data.find(site.stopRE.encode('utf-8'))
                        if stop == -1:
                            log(u'stopRe not found for %s' % url)
                        else:
                            data = data[:stop]

            # If user setting is not set to "Ask me"
            # Sort rules to parse in the order specified in the settings
            # Parsing will continue until a match is found with rule.priority anything other than 0
            if len(site.rules) > 1:
                decorated1 = [(rule.priority, i, rule) for i, rule in enumerate(site.rules) if rule.priority < 0]
                decorated1 = sorted(decorated1, reverse = True)
                if int(addon.getSetting(u'video_type')) == 3:
                    decorated = [(rule.priority, i, rule) for i, rule in enumerate(site.rules) if rule.priority >= 0]
                    decorated = sorted(decorated)
                    site.rules = [rule for priority, i, rule in decorated]
                elif int(addon.getSetting(u'video_type')) == 2:
                    decorated = [(rule.priority, i, rule) for i, rule in enumerate(site.rules) if rule.priority > 0]
                    decorated = sorted(decorated)
                    if len(decorated) % 2 == 0:
                        decorated = decorated[len(decorated) // 2 - 1:] + list(reversed(decorated[:len(decorated) // 2 - 1]))
                    else:
                        decorated = decorated[len(decorated) // 2:] + list(reversed(decorated[:len(decorated) // 2]))
                    site.rules = [rule for rule in site.rules if rule.priority == 0] + [rule for priority, i, rule in decorated]
                elif int(addon.getSetting(u'video_type')) == 1:
                    decorated = [(rule.priority, i, rule) for i, rule in enumerate(site.rules) if rule.priority > 0]
                    decorated = sorted(decorated, reverse = True)
                    site.rules = [rule for rule in site.rules if rule.priority == 0] + [rule for priority, i, rule in decorated]
                site.rules += [rule for priority, i, rule in decorated1]
            # Parse Website
            for rule in site.rules:
                match = re.search(rule.target, data, re.IGNORECASE + re.DOTALL + re.MULTILINE)
                if match:
                    link = match.group(1)
                    if len(rule.actions) > 0:
                        for group in range(1, len(match.groups()) + 1):
                            if group == 1:
                                link = {u'match' : link}
                            else:
                                link[u'group' + str(group)] = match.group(group)
                        link = parseActions(link, rule.actions)[u'match']
                    if rule.build != None:
                        link = rule.build % link
                    if rule.type == u'video':
                        video_found = True
                        self.urlList.append(link)
                        self.extensionList.append(rule.extension)
                        self.playerList.append(rule.player)
                        if rule.dkey != None:
                            match = re.search(rule.dkey, data, re.IGNORECASE + re.DOTALL + re.MULTILINE)
                            if match:
                                dkey = match.group(1)
                                if len(rule.dkey_actions) > 0:
                                    dkey = {u'match' : dkey}
                                    dkey = parseActions(dkey, rule.dkey_actions)[u'match']
                                self.decryptList.append(dkey)
                        else:
                            self.decryptList.append(None)
                        if int(addon.getSetting(u'video_type')) == 0:
                            selList_type = {
                                u'low' : __language__(30056), 
                                u'standard' : __language__(30057), 
                                u'high' : __language__(30058)
                            }
                            append = rule.info or rule.extension
                            self.selectionList.append(selList_type[rule.quality] + u' (' + append + u')')
                    elif rule.type == u'dkey':
                        self.dkey = link
                    elif rule.type == u'forward':
                        url = clean_safe(urllib.unquote(link))
                        break
                    elif rule.type.startswith(u'redirect'):
                        tmp_lItem = {u'url': clean_safe(urllib.unquote(link))}
                        if rule.type.find(u"(") != -1:
                            tmp_lItem[u'catcher'] = rule.type[rule.type.find(u"(") + 1:-1]
                        ### need to make the else statement below an elif statement 
                        ### and make the else default to simple-match catcher 
                        else:
                            for root, dirs, files in os.walk(catDir):
                                for filename in files:
                                    if url.find(filename) != -1:
                                        tmp_lItem[u'catcher'] = filename
                        ret_videoItem = CCatcherList(tmp_lItem)
                        if ret_videoItem.videoItem != None:
                            return ret_videoItem
                        break
                    if int(addon.getSetting(u'video_type')) != 0 and rule.priority != 0:
                        break
        return None

    def selectLink(self):
        if int(addon.getSetting(u'video_type')) != 0:
            selection = 0
        else:
            dia = xbmcgui.Dialog()
            selection = dia.select(__language__(30055), self.selectionList)
        self.urlList[selection] = clean_safe(urllib.unquote(self.urlList[selection]))
        if self.dkey != None:
            self.dkey = clean_safe(urllib.unquote(self.dkey))
            self.urlList[selection] = sesame.decrypt(self.urlList[selection], self.dkey, 256)
        elif self.decryptList[selection] != None:
            self.decryptList[selection] = clean_safe(urllib.unquote(self.decryptList[selection]))
            self.urlList[selection] = sesame.decrypt(self.urlList[selection], self.decryptList[selection], 256)
        self.link = self.urlList[selection]
        self.videoExtension = u'.' + self.extensionList[selection]
        self.player = self.playerList[selection]
        return None