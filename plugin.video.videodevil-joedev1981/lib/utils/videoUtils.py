# -*- coding: latin-1 -*-

import sys, os.path
import os, traceback

import xbmc, xbmcgui

from lib.utils.fileUtils import clean_filename

addon = sys.modules["__main__"].addon
__language__ = sys.modules["__main__"].__language__
rootDir = sys.modules["__main__"].rootDir
settingsDir = sys.modules["__main__"].settingsDir
cacheDir = sys.modules["__main__"].cacheDir
resDir = sys.modules["__main__"].resDir
imgDir = sys.modules["__main__"].imgDir
catDir = sys.modules["__main__"].catDir

def playVideo(videoItem):
    if videoItem == None or videoItem[u'url'] == None:
        return
    url = videoItem[u'url']
    if u'icon' not in videoItem:
        videoItem[u'icon'] = os.path.join(imgDir, u'video.png')
    if u'title' not in videoItem:
        videoItem[u'title'] = u'...'
    listitem = xbmcgui.ListItem(videoItem[u'title'], videoItem[u'title'], videoItem[u'icon'], videoItem[u'icon'])
    listitem.setInfo(u'video', {u'Title': videoItem[u'title']})
    for info_name, info_value in videoItem.iteritems():
        try:
            listitem.setInfo(type = u'Video', infoLabels = {info_name: info_value})
        except:
            pass
    if addon.getSetting(u'download') == u'true':
        return downloadMovie(videoItem)
    elif addon.getSetting(u'download') == u'false' and addon.getSetting(u'download_ask') == u'true':
        dia = xbmcgui.Dialog()
        if dia.yesno(u'', __language__(30052)):
            return downloadMovie(videoItem)
    if u'player' in videoItem:
        if videoItem[u'player'] == u'auto':
            player_type = xbmc.PLAYER_CORE_AUTO
        elif videoItem[u'player'] == u'mplayer':
            player_type = xbmc.PLAYER_CORE_MPLAYER
        elif videoItem[u'player'] == u'dvdplayer':
            player_type = xbmc.PLAYER_CORE_DVDPLAYER
    else:
        player_type = {
            0:xbmc.PLAYER_CORE_AUTO, 
            1:xbmc.PLAYER_CORE_MPLAYER, 
            2:xbmc.PLAYER_CORE_DVDPLAYER
        }
        player_type = player_type[int(addon.getSetting(u'player_type'))]
    xbmc.Player(player_type).play(str(videoItem[u'url']), listitem)
    xbmc.sleep(200)
    return -1

def downloadMovie(videoItem):
    from SimpleDownloader import SimpleDownloader
    downloader = SimpleDownloader()
    download_path = addon.getSetting(u'download_path')
    if download_path == u'':
        try:
            download_path = xbmcgui.Dialog().browse(0, __language__(30017), u'files', '', False, False)
            addon.setSetting(id='download_path', value=download_path)
            if not os.path.exists(download_path):
                os.mkdir(download_path)
        except:
            pass
    tmp = {
        u'url': videoItem[u'url'],
        u'Title': videoItem[u'title'],
        u'download_path': download_path
    }
    downloader.download(clean_filename(videoItem[u'title'].strip(u' ')) + videoItem[u'extension'], tmp)
    return -2