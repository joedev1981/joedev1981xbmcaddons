# -*- coding: latin-1 -*-
from lib.utils.fileUtils import getFileExtension

class Mode:
    def __init__(self):
        self.current = 0
        self.modes = {
            u'START': 0,
            u'PLAY': 1,
            u'DOWNLOAD': 2,
            u'ADD': 5,
            u'REMOVE': 6,
            u'VIEW_RSS': 10,
            u'VIEW_SEARCH': 11,
            u'VIEW_RSS_DIRECTORY': 12,
            u'VIEW_DIRECTORY': 13,
            u'VIEWALL_RSS': 20,
            u'VIEWALL_SEARCH': 21,
            u'VIEWALL_DIRECTORY': 22
        }

    def __getitem__(self, m):
        return self.modes[m]

    def __eq__(self, m):
        return self.current == self.modes[m]

    def __str__(self):
        for key, value in self.modes.iteritems():
            if value == self.current:
                return u'Mode is %s' % key

    def setMode(self, m):
        try:
            self.current = self.modes[m]
        except KeyError:
            self.current = int(m)

    def getMode(self):
        return self.current

    def selectItemMode(self, item):
        if self.current == self.modes[u'VIEW_RSS'] or self.current == self.modes[u'VIEW_SEARCH'] or self.current == self.modes[u'VIEW_RSS_DIRECTORY']:
            if item[u'type'] == u'video':
                item[u'mode'] = str(self.modes[u'PLAY'])
            elif item[u'type'] == u'search':
                item[u'mode'] = str(self.modes[u'VIEW_SEARCH'])
            else:
                item[u'mode'] = str(self.modes[u'VIEW_RSS'])

        elif self.current == self.modes[u'VIEWALL_RSS'] or self.current == self.modes[u'VIEWALL_SEARCH']:
            if item[u'type'] == u'video':
                item[u'mode'] = str(self.modes[u'PLAY'])
            elif item[u'type'] == u'next':
                item[u'mode'] = str(self.modes[u'VIEWALL_RSS'])
            else:
                item[u'mode'] = str(self.modes[u'VIEWALL_DIRECTORY'])
        elif self.current == self.modes[u'VIEWALL_DIRECTORY']:
            if item[u'type'] == u'video':
                item[u'mode'] = str(self.modes[u'PLAY'])
            else:
                item[u'mode'] = str(self.modes[u'VIEWALL_RSS'])
        return item

    def selectLinkMode(self, link):
        if self.current == self.modes[u'START']:
            if link[u'url'] == u'sites.list':
                link[u'mode'] = str(self.modes[u'VIEWALL_RSS'])
            else:
                link[u'mode'] = str(self.modes[u'VIEW_RSS'])

        elif self.current == self.modes[u'VIEW_RSS'] or self.current == self.modes[u'VIEW_SEARCH'] or self.current == self.modes[u'VIEW_RSS_DIRECTORY']:
            if link[u'type'] == u'search':
                link[u'mode'] = str(self.modes[u'VIEW_SEARCH'])
            elif getFileExtension(link[u'url']) == u'list':
                link[u'mode'] = str(self.modes[u'VIEW_DIRECTORY'])
            else:
                link[u'mode'] = str(self.modes[u'VIEW_RSS_DIRECTORY'])
        elif self.current == self.modes[u'VIEW_DIRECTORY']:
            link[u'mode'] = str(self.modes[u'VIEW_RSS'])

        elif self.current == self.modes[u'VIEWALL_RSS'] or self.current == self.modes[u'VIEWALL_SEARCH']:
            if link[u'type'] == u'video':
                link[u'mode'] = str(self.modes[u'PLAY'])
            elif link[u'type'] == u'next':
                link[u'mode'] = str(self.modes[u'VIEWALL_RSS'])
            elif link[u'type'] == u'search':
                link[u'mode'] = str(self.modes[u'VIEWALL_SEARCH'])
            else:
                link[u'mode'] = str(self.modes[u'VIEWALL_DIRECTORY'])
        elif self.current == self.modes[u'VIEWALL_DIRECTORY']:
            if link[u'type'] == u'search':
                link[u'mode'] = str(self.modes[u'VIEWALL_SEARCH'])
            else:
                link[u'mode'] = str(self.modes[u'VIEWALL_RSS'])
        return link

    def selectMode(self, item, islink = False):
        if self.current == self.modes[u'START']:
            if item[u'url'] == u'sites.list':
                item[u'mode'] = str(self.modes[u'VIEWALL_RSS'])
            else:
                item[u'mode'] = str(self.modes[u'VIEW_RSS'])

        elif self.current == self.modes[u'VIEW_RSS'] or self.current == self.modes[u'VIEW_SEARCH'] or self.current == self.modes[u'VIEW_RSS_DIRECTORY']:
            if item[u'type'] == u'video':
                item[u'mode'] = str(self.modes[u'PLAY'])
            elif item[u'type'] == u'search':
                item[u'mode'] = str(self.modes[u'VIEW_SEARCH'])
            elif getFileExtension(item[u'url']) == u'list':
                item[u'mode'] = str(self.modes[u'VIEW_DIRECTORY'])
            elif islink:
                item[u'mode'] = str(self.modes[u'VIEW_RSS_DIRECTORY'])
            else:
                item[u'mode'] = str(self.modes[u'VIEW_RSS'])
        elif self.current == self.modes[u'VIEW_DIRECTORY']: # and islink ?
            item[u'mode'] = str(self.modes[u'VIEW_RSS'])

        elif self.current == self.modes[u'VIEWALL_RSS'] or self.current == self.modes[u'VIEWALL_SEARCH']:
            if item[u'type'] == u'video':
                item[u'mode'] = str(self.modes[u'PLAY'])
            elif item[u'type'] == u'next':
                item[u'mode'] = str(self.modes[u'VIEWALL_RSS'])
            elif item[u'type'] == u'search':
                item[u'mode'] = str(self.modes[u'VIEWALL_SEARCH'])
            else:
                item[u'mode'] = str(self.modes[u'VIEWALL_DIRECTORY'])
        elif self.current == self.modes[u'VIEWALL_DIRECTORY']:
            if item[u'type'] == u'video':
                item[u'mode'] = str(self.modes[u'PLAY'])
            elif item[u'type'] == u'search':
                item[u'mode'] = str(self.modes[u'VIEWALL_SEARCH'])
            else:
                item[u'mode'] = str(self.modes[u'VIEWALL_RSS'])
        return item