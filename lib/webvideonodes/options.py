class Options(object):

    def __init__(self):
        self._base_url = ''
        self._search_query_ref = ''
        self._isdocker = 0
        self._isdebug = 0
        self._isandroid = 0
        self._isvisible_browser = 0
        self._itemonpage = 20
        self._contentviewnum = 50
        self._timeout = 60
        self._root_list = {}

    @property
    def base_url(self):
        return self._base_url

    @base_url.setter
    def base_url(self, value):
        self._base_url = value
        
    @property
    def search_query_ref(self):
        return self._search_query_ref

    @search_query_ref.setter
    def search_query_ref(self, value):
        self._search_query_ref = value

    @property
    def isdocker(self):
        return self._isdocker

    @isdocker.setter
    def isdocker(self, value):
        self._isdocker = value
       
    @property
    def isandroid(self):
        return self._isandroid

    @isandroid.setter
    def isandroid(self, value):
        self._isandroid = value

    @property
    def isdebug(self):
        return self._isdebug

    @isdebug.setter
    def isdebug(self, value):
        self._isdebug = value 

    @property
    def isvisible_browser(self):
        return self._isvisible_browser

    @isvisible_browser.setter
    def isvisible_browser(self, value):
        self._isvisible_browser = value

    @property
    def itemonpage(self):
        return self._itemonpage

    @itemonpage.setter
    def itemonpage(self, value):
        self._itemonpage = value   

    @property
    def contentviewnum(self):
        return self._contentviewnum

    @contentviewnum.setter
    def contentviewnum(self, value):
        self._contentviewnum = value   

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        self._timeout = value        
        
    @property
    def root_list(self):
        return self._root_list

    @root_list.setter
    def root_list(self, value):
        self._root_list = value