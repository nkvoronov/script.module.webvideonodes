import os
import sys
import xbmc
import xbmcvfs
import xbmcgui
import xbmcplugin
import xbmcaddon
from urllib.parse import quote
from urllib.parse import quote_plus
from urllib.parse import unquote_plus
from .options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from .webdriver import get_driver_path
from .webdriver import run_selenium_doker

def SettingBoolToInt(val):
    if val == 'true':
        return 1
    else:
        return 0
        
categories_file = 'categories-list'
search_file = 'search-list'

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
            self._fanart = self._addon.getAddonInfo('fanart')
            self._profile = xbmcvfs.translatePath(self._addon.getAddonInfo('profile'))
            #data dir
            dataDir = xbmcvfs.translatePath(self._addon.getAddonInfo('profile')) + 'data'
            if not os.path.exists(dataDir):
                os.makedirs(dataDir)
            #files
            self._fileCategories = dataDir + os.path.sep + categories_file
            self._fileSearches = dataDir + os.path.sep + search_file
            self._listCategories = {}
            self._listSearches = {}
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
        xbmc.log('## ' + self._addon.getAddonInfo('name') + ' ## ' + source + ' ## ' + text, xbmc.LOGINFO)

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
        try:
            self.addLog('VideoNodes::openUrlRequest', 'enter_function')
            self.addLog('VideoNodes::openUrlRequest','OPEN URL: ' + url)
            headers = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3',
            'Content-Type': 'application/x-www-form-urlencoded'}
            connect = urllib.request.urlopen(urllib.request.Request(url, urllib.urlencode({}), headers))
            html = connect.read()
            connect.close()
            self.addLog('VideoNodes::openUrlRequest', 'exit_function')
            return html.strip()
        except Exception as e:
            dialog = xbmcgui.Dialog()
            dialog.ok('Open Url Request', 'ERROR: (' + repr(e) + ')')
            self.addLog('VideoNodes::openUrlRequest', 'ERROR: (' + repr(e) + ')')
            
    def RunWebBrowser(self):
        if self._options.isdocker == 1:
            run_selenium_doker()
            driver = webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub', desired_capabilities=DesiredCapabilities.CHROME)
        else:
            driverPath = get_driver_path('chromedriver')
            self.addLog('RunWebBrowser','Driver path: ' + driverPath)
            croptions = webdriver.ChromeOptions()
            croptions.add_argument('disable-infobars')
            prefs = {'profile.default_content_settings.popups' : 2, 'profile.default_content_setting_values.notifications' : 2}
            croptions.add_experimental_option('prefs',prefs)
            if self._options.isvisible_browser != 1:
                croptions.add_argument('headless')
            if xbmc.getCondVisibility('System.HasAddon(service.libreelec.settings)+System.HasAddon(browser.chrome)'):	
                croptions.binary_location = xbmcaddon.Addon('browser.chrome').getAddonInfo('path') + os.path.sep + 'bin' + os.path.sep + 'chrome-start'
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
            wait = WebDriverWait(driver, self._options.timeout)
            wait.until(element_present)
            self.addLog('WaitWebBrowser','Page source: ' + 'OK')
        except Exception as e:
            pass

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
            return keyboard.getText()
        return default
        
    def addFolder(self, localpath, handle, url, page, mode, title, img='DefaultFolder.png', info=None):
        Item = xbmcgui.ListItem(title, title)
        Item.setArt({'icon': "DefaultFolder.png", 'fanart': self._fanart})
        Item.setInfo(type = 'video', infoLabels = {'title':title})
        params = 'title=' + quote_plus(title) 
        if url != 'none':
            params = params + '&url=' + quote_plus(url)
        if int(page) != 0:
            params = params + '&page=' + str(int(page))        
        Path = self.buildPath(localpath, mode, params)        
        xbmcplugin.addDirectoryItem(handle, Path, Item, True, self._options.itemonpage + 4)
        
    def addItem(self, localpath, handle, url, mode, title, img='DefaultVideo.png', info=None):
        Item = xbmcgui.ListItem(title, title)
        Item.setArt({'poster': img, 'icon': "DefaultFolder.png", 'fanart': self._fanart})
        Item.setInfo(type = 'video', infoLabels = {'title':title})
        params = 'title=' + quote_plus(title) + '&img=' + quote_plus(img) + '&url=' + quote_plus(url)
        Path = self.buildPath(localpath, mode, params)
        xbmcplugin.addDirectoryItem(handle, Path, Item, False, self._options.itemonpage + 4)

    def addNextPage(self, localpath, handle, url, page, mode, endList):
        if endList:
            self.addFolder(localpath, handle, url, int(page)+1, mode, self.getLang(30009) + str(int(page)+1))
        xbmcplugin.endOfDirectory(handle)
        if self._options.contentviewnum != 0:
            xbmc.executebuiltin('Container.SetViewMode(' + str(self._options.contentviewnum) + ')')

    def showRoot(self, localpath, handle):
        xbmcplugin.setContent(int(sys.argv[1]), 'files')
        self.addLog('showRoot')
        for title, mode in sorted(self._options.root_list.items()):
            self.addFolder(localpath, handle, 'none', int('0'), str(mode), self.getLang(int(title)))
        xbmcplugin.endOfDirectory(handle)

    def searchVideos(self, localpath, handle):
        xbmcplugin.setContent(int(sys.argv[1]), 'files')
        self.addFolder(localpath, handle, 'none', int('0'), '13', '(' + self.getLang(30005) + ')')
        self.addFolder(localpath, handle, 'none', int('0'), '14', '(' + self.getLang(30006) + ')')
        if os.path.isfile(self._fileSearches):
            self.loadSearches(localpath, handle, '10')
        xbmcplugin.endOfDirectory(handle)

    def newSearchVideos(self, localpath, handle):
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        vq = self.getKeyboard( heading=self.getLang(30010))
        if ( not vq ): return False, 0
        searchUrl = self._options.base_url + self._options.search_query_ref + quote(vq)
        self.addLog('newSearchVideos', 'SEARCHING URL: ' + searchUrl)
        self.showSearchList(localpath, handle, searchUrl, 1, '10')
        if os.path.isfile(self._fileSearches):
            self.loadSearches(localpath, handle, '10', 0)
        if vq not in self._listSearches:
            self.addLog('newSearchVideos','DATA: ' + vq + ' = ' + searchUrl)
            self._listSearches[vq] = searchUrl
            self.saveSearches()

    def showSearchList(self, localpath, handle, url, page, mode):
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        pageUrl = self.buildUrl(1, url, page)
        count = self.showListCommon(localpath, handle, pageUrl, False)
        self.addNextPage(localpath, handle, url, page, mode, count == self._options.itemonpage)

    def showCategories(self, localpath, handle):
        xbmcplugin.setContent(int(sys.argv[1]), 'files')
        self.addFolder(localpath, handle, 'none', int('0'), '15', '(' + self.getLang(30003) + ')')
        self.getCategories(localpath, handle, '11')
        xbmcplugin.endOfDirectory(handle)
        
    def loadSearches(self, localpath, handle, mode, addFolder=1):
        self._listSearches = {}
        with open(self._fileSearches) as file:
            for item in file:
                if '|' in item:
                    title,url,end = item.split('|')
                    self._listSearches[title] = url
                    self.addLog('loadSearches','DATA: ' + title + ' = ' + url)
                    if addFolder:
                        self.addFolder(localpath, handle, url, 1, mode, title)
                else:
                    pass

    def loadCategories(self, localpath, handle, mode):
        self._listCategories = {}
        with open(self._fileCategories) as file:
            for item in file:
                if '|' in item:
                    title,url,end = item.split('|')
                    self._listCategories[title] = url
                    self.addFolder(localpath, handle, url, int('0'), mode, title)
                else:
                    pass
                    
    def saveSearches(self):
        with open(self._fileSearches, 'w') as file:
            for title in sorted(self._listSearches.keys()):
                url = self._listSearches[title]
                self.addLog('saveSearches','DATA: ' + title + ' = ' + url)
                file.write('%s|%s|e\n' % (title, url))
        
    def saveCategories(self, localpath, handle, mode):
        self._listCategories = self.getNetCategories()
        with open(self._fileCategories, 'w') as file:
            for title in sorted(self._listCategories.keys()):
                url = self._listCategories[title]
                file.write('%s|%s|e\n' % (title, url))
                self.addFolder(localpath, handle, url, int('0'), mode, title)
        
    def getNetCategories(self):
        list = {}
        return list
        
    def getCategories(self, localpath, handle, mode):
        if os.path.isfile(self._fileCategories):
            self.loadCategories(localpath, handle, mode)
        else:
            self.saveCategories(localpath, handle, mode)

    def showCatList(self, localpath, handle, url, page, mode):
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        pageUrl = self.buildUrl(2, url, page)
        count = self.showListCommon(localpath, handle, pageUrl, False)
        self.addNextPage(localpath, handle, url, page, mode, count == self._options.itemonpage)

    def showAllList(self, localpath, handle, url, page, mode):
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        if url == None:
            url = self._options.base_url
        pageUrl = self.buildUrl(3, url, page)
        count = self.showListCommon(localpath, handle, pageUrl, True)
        self.addNextPage(localpath, handle, url, page, mode, count == self._options.itemonpage)
        
    def addNavFolders(self, localpath, handle):
        self.addFolder(localpath, handle, 'none', int('0'), '', self.getLang(30004))
        self.addFolder(localpath, handle, 'none', int('0'), str(0), self.getLang(30000))
        self.addFolder(localpath, handle, 'none', int('0'), str(1), self.getLang(30001))

    def showListCommon(self, localpath, handle, url, isall):
        pass

    def getVideo(self, url):
        return url

    def playVideo(self, localpath, handle, url, title, img):
        try:
            self.addLog('playVideo','URL: ' + url)
            xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
            playUrl = self.getVideo(url)
            xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
            self.addLog('playVideo','Play URL: ' + playUrl)
            if playUrl != 'none':
                playTitle = unquote_plus(title)
                playImg = unquote_plus(img)
                Item = xbmcgui.ListItem(playTitle, playTitle)
                Item.setArt({'poster': playImg, 'icon': "DefaultFolder.png", 'fanart': self._fanart})
                Item.setInfo(type = 'video', infoLabels = {'title':playTitle})
                xbmc.Player().play(playUrl, Item)
        except Exception as e:
            xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('Play Video', 'ERROR: ' + repr(e))
            self.addLog('playVideo', 'ERROR: (' + repr(e) + ')')

    def parseNodes(self):
        params = self.getParams(sys.argv)
        mode = None
        url = None
        page = 1
        title = ''
        img = ''

        try:
            url = unquote_plus(params['url'])
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
            title = params['title']
        except:
            pass
        try:
            img = params['img']
        except:
            pass

        if mode == None:
            self.showRoot(sys.argv[0], int(sys.argv[1]))
        elif mode == 0:
            self.searchVideos(sys.argv[0], int(sys.argv[1]))
        elif mode == 1:
            self.showCategories(sys.argv[0], int(sys.argv[1]))
        elif mode == 2:
            self.showAllList(sys.argv[0], int(sys.argv[1]), url, page, '12')
        elif mode == 10:
            self.showSearchList(sys.argv[0], int(sys.argv[1]), url, page, '10')
        elif mode == 11:
            self.showCatList(sys.argv[0], int(sys.argv[1]), url, page, '11')
        elif mode == 12:
            self.showAllList(sys.argv[0], int(sys.argv[1]), url, page, '12')
        elif mode == 13:
            self.newSearchVideos(sys.argv[0], int(sys.argv[1]))
        elif mode == 14:
            if os.path.exists(self._fileSearches):
                os.remove(self._fileSearches)
                xbmc.executebuiltin('Container.Refresh')
        elif mode == 15:
            if os.path.exists(self._fileCategories):
                os.remove(self._fileCategories)
                xbmc.executebuiltin('Container.Refresh')
        elif mode == 20:
            self.playVideo(sys.argv[0], int(sys.argv[1]), url, title, img)