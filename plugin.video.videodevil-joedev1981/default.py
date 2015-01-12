import xbmc, xbmcaddon
import xbmcplugin, xbmcgui
import sys, os, traceback
import urllib
import time

xbmc.log('Initializing VideoDevil')

addon = xbmcaddon.Addon(id='plugin.video.videodevil-joedev1981')
if addon.getSetting('enable_debug') == 'true':
    enable_debug = True
    xbmc.log('VideoDevil debug logging enabled')
else:
    enable_debug = False


__plugin__ = 'VideoDevil-joedev1981'
__author__ = 'sfaxman'
__credits__ = 'bootsy'
__version__ = '0.0.2'
__language__ = addon.getLocalizedString
rootDir = addon.getAddonInfo('path')
if rootDir[-1] == ';':
    rootDir = rootDir[0:-1]
rootDir = xbmc.translatePath(rootDir)
settingsDir = addon.getAddonInfo('profile')
settingsDir = xbmc.translatePath(settingsDir)
cacheDir = os.path.join(settingsDir, 'cache')
allsitesDir = os.path.join(settingsDir, 'allsites')
resDir = os.path.join(rootDir, 'resources')
imgDir = os.path.join(resDir, 'images')
catDir = os.path.join(resDir, 'catchers')
handle = int(sys.argv[1])

def log(s):
    if enable_debug:
        try:
            xbmc.log(s)
        except UnicodeEncodeError:
            xbmc.log(smart_unicode(s).encode('ISO-8859-1'))
    return

from lib.common import smart_unicode

from lib.entities.Mode import Mode
mode = Mode()

xbmc.log('VideoDevil initialized')

def decodeUrl(url):
    item = {}
    if url.find('&') == -1:
        item[u'url'] = smart_unicode(urllib.unquote(url))
        item[u'type'] = u'start'
    else:
        for info_name_value in url.split('&'):
            info_name, info_value = info_name_value.split('=', 1)
            if info_name == 'mode':
                mode.setMode(info_value)
            else:
                if info_name == 'url':
                    info_value = info_value.replace('%20', '%2520')
                item[smart_unicode(info_name)] = urllib.unquote(smart_unicode(info_value))
    return item

try:
    if len(sys.argv[2]) <= 2:
        consenting = True
        if addon.getSetting('hide_warning') == 'false':
            dialog = xbmcgui.Dialog()
            if not dialog.yesno(__language__(30061), __language__(30062), __language__(30063), __language__(30064), __language__(30065), __language__(30066)):
                consenting = False
        if consenting:
            if (not addon.getSetting('first_run')) or enable_debug:
                if not addon.getSetting('first_run'):
                    addon.setSetting('first_run', '1')
                if not os.path.isdir(settingsDir):
                    xbmc.log('Creating settings directory ' + str(settingsDir))
                    os.mkdir(settingsDir)
                    xbmc.log('Settings directory created')
                if not os.path.isdir(cacheDir):
                    xbmc.log('Creating cache directory ' + str(cacheDir))
                    os.mkdir(cacheDir)
                    xbmc.log('Cache directory created')
                if not os.path.isdir(allsitesDir):
                    xbmc.log('Creating all sites directory ' + str(allsitesDir))
                    os.mkdir(allsitesDir)
                    xbmc.log('All sites directory created')
            log(
                'Directories utilized:' + '\n' +
                'Settings directory: ' + str(settingsDir) + '\n' +
                'Cache directory: ' + str(cacheDir) + '\n' +
                'Resource directory: ' + str(resDir) + '\n' +
                'Image directory: ' + str(imgDir) + '\n' +
                'Catchers directory: ' + str(catDir) + '\n' +
                'All sites directory: ' + str(allsitesDir)
            )
            log('Purging cache directories')
            for root, dirs, files in os.walk(cacheDir, topdown = False):
                for name in files:
                    os.remove(os.path.join(root, name))
            for root, dirs, files in os.walk(allsitesDir):
                if root == allsitesDir:
                    for name in files:
                        if not enable_debug:
                            if name == 'search.list':
                                continue
                            else:
                                cache_setting = addon.getSetting(name[:-5] + '_all_sites_cache')
                                if cache_setting:
                                    if time.time() - float(cache_setting) < 3600:
                                        continue
                        os.remove(os.path.join(root, name))
                else:
                    cache_setting = addon.getSetting(os.path.basename(root) + '_all_sites_cache')
                    if cache_setting and not enable_debug:
                        if time.time() - float(cache_setting) < 3600:
                            continue
                    for name in files:
                        os.remove(os.path.join(root, name))
            log('Cache directories purged')
            from lib.parseview import parseView
            parseView(handle, decodeUrl('sites.list'))
            if int(addon.getSetting('list_view')) == 0:
                xbmc.executebuiltin("Container.SetViewMode(500)")
            xbmcplugin.endOfDirectory(handle = int(sys.argv[1]))
            xbmc.log('End of directory')
    else:
        params = sys.argv[2][1:]
        lItem = decodeUrl(params)
        log('currentView:\n' + '\n'.join((k + '=' + v for k, v in lItem.iteritems())))
        if mode == 'PLAY' or mode == 'DOWNLOAD':
            from lib.videoparser import CCatcherList
            videoItem = CCatcherList(lItem).videoItem
            if mode == 'PLAY':
                from lib.utils.videoUtils import playVideo
                result = playVideo(videoItem)
            elif mode == 'DOWNLOAD':
                from lib.utils.videoUtils import downloadMovie
                result = downloadMovie(videoItem)
        else:
            from lib.parseview import parseView
            result = parseView(handle, lItem).result
        if result == 0:
            if int(addon.getSetting('list_view')) == 0:
                xbmc.executebuiltin("Container.SetViewMode(500)")
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmc.log('End of directory')
        elif result == -2:
            xbmc.executebuiltin('Container.Refresh')
except Exception, e:
    if enable_debug:
        traceback.print_exc(file = sys.stdout)
    dialog = xbmcgui.Dialog()
    dialog.ok('VideoDevil Error', 'Error running VideoDevil.\n\nReason:\n' + str(e))