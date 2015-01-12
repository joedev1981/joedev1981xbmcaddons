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
        self.selectLinkMode = self._start_view_modes_for_link
        self.selectItemMode = None

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
        if self.current == self.modes[u'START']:
            self.selectLinkMode = self._start_view_modes_for_link
            self.selectItemMode = None
        elif self.current == self.modes[u'VIEW_RSS'] or self.current == self.modes[u'VIEW_SEARCH'] or self.current == self.modes[u'VIEW_RSS_DIRECTORY']:
            self.selectLinkMode = self._single_view_non_directory_modes_for_link
            self.selectItemMode = self._single_view_non_directory_modes_for_item
        elif self.current == self.modes[u'VIEWALL_RSS'] or self.current == self.modes[u'VIEWALL_SEARCH']:
            self.selectLinkMode = self._multi_view_non_directory_modes_for_link
            self.selectItemMode = self._multi_view_non_directory_modes_for_item
        elif self.current == self.modes[u'VIEW_DIRECTORY']:
            self.selectLinkMode = self._single_view_directory_modes_for_link
            self.selectItemMode = None
        elif self.current == self.modes[u'VIEWALL_DIRECTORY']:
            self.selectLinkMode = self._multi_view_directory_modes_for_link
            self.selectItemMode = self._multi_view_directory_modes_for_item

    def getMode(self):
        return self.current

    def _start_view_modes_for_link(self, link):
        if link[u'url'] == u'sites.list':
            link[u'mode'] = str(self.modes[u'VIEWALL_RSS'])
        else:
            link[u'mode'] = str(self.modes[u'VIEW_RSS'])
        return link

    def _single_view_non_directory_modes_for_link(self, link):
        if link[u'type'] == u'search':
            link[u'mode'] = str(self.modes[u'VIEW_SEARCH'])
        elif getFileExtension(link[u'url']) == u'list':
            link[u'mode'] = str(self.modes[u'VIEW_DIRECTORY'])
        else:
            link[u'mode'] = str(self.modes[u'VIEW_RSS_DIRECTORY'])
        return link

    def _single_view_non_directory_modes_for_item(self, item):
        if item[u'type'] == u'video':
            item[u'mode'] = str(self.modes[u'PLAY'])
        elif item[u'type'] == u'search':
            item[u'mode'] = str(self.modes[u'VIEW_SEARCH'])
        else:
            item[u'mode'] = str(self.modes[u'VIEW_RSS'])
        return item

    def _multi_view_non_directory_modes_for_link(self, link):
        if link[u'type'] == u'video':
            link[u'mode'] = str(self.modes[u'PLAY'])
        elif link[u'type'] == u'next':
            link[u'mode'] = str(self.modes[u'VIEWALL_RSS'])
        elif link[u'type'] == u'search':
            link[u'mode'] = str(self.modes[u'VIEWALL_SEARCH'])
        else:
            link[u'mode'] = str(self.modes[u'VIEWALL_DIRECTORY'])
        return link

    def _multi_view_non_directory_modes_for_item(self, item):
        if item[u'type'] == u'video':
            item[u'mode'] = str(self.modes[u'PLAY'])
        elif item[u'type'] == u'next':
            item[u'mode'] = str(self.modes[u'VIEWALL_RSS'])
        else:
            item[u'mode'] = str(self.modes[u'VIEWALL_DIRECTORY'])
        return item

    def _single_view_directory_modes_for_link(self, link):
        link[u'mode'] = str(self.modes[u'VIEW_RSS'])
        return link

    def _multi_view_directory_modes_for_link(self, link):
        if link[u'type'] == u'search':
            link[u'mode'] = str(self.modes[u'VIEWALL_SEARCH'])
        else:
            link[u'mode'] = str(self.modes[u'VIEWALL_RSS'])
        return link

    def _multi_view_directory_modes_for_item(self, item):
        if item[u'type'] == u'video':
            item[u'mode'] = str(self.modes[u'PLAY'])
        else:
            item[u'mode'] = str(self.modes[u'VIEWALL_RSS'])
        return item

    #if self.selectMode is ever integrated (replacing self.selectLinkMode and self.selectItemMode)
    def _start_view_modes(self, item):
        if link[u'url'] == u'sites.list':
            link[u'mode'] = str(self.modes[u'VIEWALL_RSS'])
        else:
            link[u'mode'] = str(self.modes[u'VIEW_RSS'])
        return item

    def _single_view_non_directory_modes(self, item):
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
        return item

    def _multi_view_non_directory_modes(self, item):
        if item[u'type'] == u'video':
            item[u'mode'] = str(self.modes[u'PLAY'])
        elif item[u'type'] == u'next':
            item[u'mode'] = str(self.modes[u'VIEWALL_RSS'])
        elif item[u'type'] == u'search':
            item[u'mode'] = str(self.modes[u'VIEWALL_SEARCH'])
        else:
            item[u'mode'] = str(self.modes[u'VIEWALL_DIRECTORY'])
        return item

    def _single_view_directory_modes(self, item):
        item[u'mode'] = str(self.modes[u'VIEW_RSS'])
        return item

    def _multi_view_directory_modes(self, item):
        if item[u'type'] == u'video':
            item[u'mode'] = str(self.modes[u'PLAY'])
        elif item[u'type'] == u'search':
            item[u'mode'] = str(self.modes[u'VIEWALL_SEARCH'])
        else:
            item[u'mode'] = str(self.modes[u'VIEWALL_RSS'])
        return item