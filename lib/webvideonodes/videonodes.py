import os
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib
import urllib2
from .options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.driver_utils import get_driver_path
from selenium.webdriver.common.driver_utils import run_selenium_doker

def SettingBoolToInt(val):
    if val == 'true':
        return 1
    else:
        return 0

class VideoNodes(object):

    def __init__(self, options, addon_id):
        isRun = 1
        if options is None:
            self._options = Options()
            isRun = 0
        else:
            self._options = options
        self._addon_id = addon_id
        if addon_id != None:
            self._addon = xbmcaddon.Addon(addon_id)
        if isRun:
            self.parseNodes()

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, value):
        self._options = value

    def getLang(self, lcode):
        return self._addon.getLocalizedString(lcode)

    def addLog(self, source, text=''):
        if self._options.isdebug == 0:
            return
        xbmc.log('## ' + self._addon.getAddonInfo('name') + ' ## ' + source + ' ## ' + text)

    def getParams(self, args):
        param=[]
        self.addLog('getParams','PARSING ARGUMENTS: ' + str(args))
        paramstring=args[2]
        if len(paramstring)>=2:
            params=args[2]
            cleanedparams=params.replace('?', '')
            if (params[len(params)-1]=='/'):
                params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                splitparams={}
                splitparams=pairsofparams[i].split('=')
                if (len(splitparams))==2:
                    param[splitparams[0]]=splitparams[1]
            return param

    def openUrlRequest(self, url):
        req = urllib2.Request(url, None, 20)
        req.add_header('User-agent','Mozilla/5.0')
        result = resp.read()
        resp.close()
        return result

    def RunWebBrowser(self):
        if self._options.isdocker == 1:
            run_selenium_doker()
            driver = webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub', desired_capabilities=DesiredCapabilities.CHROME)
        else:
            driverPath = get_driver_path('chromedriver')
            self.addLog('RunWebBrowser','Driver path: ' + driverPath)
            croptions = webdriver.ChromeOptions()
            if self._options.isvisible_browser != 1:
                croptions.add_argument('headless')
            if xbmc.getCondVisibility('System.HasAddon(service.libreelec.settings)+System.HasAddon(browser.chromium)'):
                options.binary_location = xbmcaddon.Addon('browser.chromium').getAddonInfo('path') + os.path.sep + 'bin' + os.path.sep + 'google-chrome'
            driver = webdriver.Chrome(driverPath, chrome_options=croptions)
        return driver

    def WaitWebBrowser(self, driver, type, value):
        try:
            if type == 'ID':
                element_present = EC.presence_of_element_located((By.ID, value))
            elif type == 'XPATH':
                element_present = EC.presence_of_element_located((By.XPATH, value))
            elif type == 'LINK_TEXT':
                element_present = EC.presence_of_element_located((By.LINK_TEXT, value))
            elif type == 'PARTIAL_LINK_TEXT':
                element_present = EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, value))
            elif type == 'NAME':
                element_present = EC.presence_of_element_located((By.NAME, value))
            elif type == 'TAG_NAME':
                element_present = EC.presence_of_element_located((By.TAG_NAME, value))
            elif type == 'CLASS_NAME':
                element_present = EC.presence_of_element_located((By.CLASS_NAME, value))
            elif type == 'CSS_SELECTOR':
                element_present = EC.presence_of_element_located((By.CSS_SELECTOR, value))
            WebDriverWait(driver, self._options.timeout).until(element_present)
            self.addLog('WaitWebBrowser','Page source: ' + 'OK')
        except Exception, e:
            dialog = xbmcgui.Dialog()
            dialog.ok('ERROR', 'ERROR: (' + repr(e) + ')')
            self.addLog('WaitWebBrowser', 'ERROR: (' + repr(e) + ')')

    def buildUrlCategories(self, url, page):
        return url

    def buildUrlListSearch(self, url, page):
        return url

    def buildUrlListCategories(self, url, page):
        return url

    def buildUrlListAll(self, url, page):
        return url

    def buildUrl(self, type, url, page=1):
        #Categories
        if type == 0:
            build_url = self.buildUrlCategories(url, page)
        #List Search
        elif type == 1:
            build_url = self.buildUrlListSearch(url, page)
        #List Categories
        elif type == 2:
            build_url = self.buildUrlListCategories(url, page)
        #List All
        elif type == 3:
            build_url = self.buildUrlListAll(url, page)
        return build_url

    def buildPath(self, localpath, mode, params=''):
        if params == '':
            build_path = localpath + '?mode=' + mode
        else:
            build_path = localpath + '?mode=' + mode + '&' + params
        return  build_path

    def getKeyboard(self, default='', heading='', hidden=False ):
        self.addLog('getKeyboard')
        keyboard = xbmc.Keyboard( default, heading, hidden )
        keyboard.doModal()
        if ( keyboard.isConfirmed() ):
            return unicode( keyboard.getText(), 'utf-8' )
        return default

    def addNextPage(self, localpath, handle, url, page, mode):
        name = self.getLang(30011).encode('utf-8')
        Item = xbmcgui.ListItem(name)
        params = 'name=' + urllib.quote_plus(name) + '&url=' + urllib.quote_plus(url) + '&page=' + str(int(page) + 1)
        Path = self.buildPath(localpath, mode, params)
        xbmcplugin.addDirectoryItem(handle, Path, Item, True, self._options.itemonpage)
        xbmcplugin.endOfDirectory(handle)

    def showRoot(self, localpath, handle):
        self.addLog('showRoot')
        for title, mode in self._options.root_list.items():
            Item = xbmcgui.ListItem(self.getLang(int(title)))
            Path = self.buildPath(localpath, str(mode))
            xbmcplugin.addDirectoryItem(handle, Path, Item, True)
        xbmcplugin.endOfDirectory(handle)

    def searchVideos(self, localpath, handle):
        vq = self.getKeyboard( heading=self.getLang(30010) )
        if ( not vq ): return False, 0
        searchUrl = self._options.base_url + self._options.search_query_ref + urllib.quote_plus(vq)
        self.addLog('searchVideos', 'SEARCHING URL: ' + searchUrl)
        self.showSearchList(localpath, handle, searchUrl, 1, '10')

    def showSearchList(self, localpath, handle, url, page, mode):
        pageUrl = self.buildUrl(1, url, page)
        self.showListCommon(localpath, handle, pageUrl, False)
        self.addNextPage(localpath, handle, url, page, mode)

    def showCategories(self, localpath, handle):
        pass

    def showCatList(self, localpath, handle, url, page, mode):
        pageUrl = self.buildUrl(2, url, page)
        self.showListCommon(localpath, handle, pageUrl, False)
        self.addNextPage(localpath, handle, url, page, mode)

    def showAllList(self, localpath, handle, url, page, mode):
        if url == None:
            url = self._options.base_url
        pageUrl = self.buildUrl(3, url, page)
        self.showListCommon(localpath, handle, pageUrl, True)
        self.addNextPage(localpath, handle, url, page, mode)

    def showListCommon(self, localpath, handle, pageUrl, isAll):
        pass

    def getVideo(self, url):
        return url

    def playVideo(self, localpath, handle, url, name, thumb):
        try:
            self.addLog('playVideo','URL: ' + url)
            xbmc.executebuiltin('ActivateWindow(busydialog)')
            play_url = self.getVideo(url)
            xbmc.executebuiltin('Dialog.Close(busydialog)')
            if play_url != 'none':
                title = urllib.unquote_plus(name)
                icon = urllib.unquote_plus(thumb)
                Item = xbmcgui.ListItem(title, title, icon, icon)
                xbmc.Player().play(play_url, Item)
        except Exception, e:
            xbmc.executebuiltin('Dialog.Close(busydialog)')
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('Play Video', 'ERROR: ' + repr(e))
            self.addLog('playVideo', 'ERROR: (' + repr(e) + ')')

    def parseNodes(self):
        params = self.getParams(sys.argv)
        mode = None
        url = None
        page = 1
        name = ''
        thumb = ''

        try:
            url = urllib.unquote_plus(params['url'])
        except:
            pass
        try:
            mode = int(params['mode'])
        except:
            pass
        try:
            page = int(params['page'])
        except:
            pass
        try:
            name = params['name']
        except:
            pass
        try:
            thumb = params['thumb']
        except:
            pass

        if mode == None:
            xbmcplugin.setContent(int(sys.argv[1]), 'files')
            self.showRoot(sys.argv[0], int(sys.argv[1]))
        elif mode == 0:
            xbmcplugin.setContent(int(sys.argv[1]), 'movies')
            self.searchVideos(sys.argv[0], int(sys.argv[1]))
        elif mode == 1:
            xbmcplugin.setContent(int(sys.argv[1]), 'files')
            self.showCategories(sys.argv[0], int(sys.argv[1]))
        elif mode == 2:
            xbmcplugin.setContent(int(sys.argv[1]), 'movies')
            self.showAllList(sys.argv[0], int(sys.argv[1]), url, page, '12')
        elif mode == 10:
            xbmcplugin.setContent(int(sys.argv[1]), 'movies')
            self.showSearchList(sys.argv[0], int(sys.argv[1]), url, page, '10')
        elif mode == 11:
            xbmcplugin.setContent(int(sys.argv[1]), 'movies')
            self.showCatList(sys.argv[0], int(sys.argv[1]), url, page, '11')
        elif mode == 12:
            xbmcplugin.setContent(int(sys.argv[1]), 'movies')
            self.showAllList(sys.argv[0], int(sys.argv[1]), url, page, '12')
        elif mode == 20:
            self.playVideo(sys.argv[0], int(sys.argv[1]), url, name, thumb)

        if (self._options.contentviewnum <> 0) and (( mode <> None ) or (mode <> 1)):
            xbmc.executebuiltin('Container.SetViewMode(' + str(self._options.contentviewnum) + ')')
