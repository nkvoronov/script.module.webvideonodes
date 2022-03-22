import os
import xbmc
import xbmcaddon
import platform
import subprocess

_adon_id = 'script.module.webdriver'
_addon = xbmcaddon.Addon(_adon_id)

def run_selenium_doker():
    run_script = get_driver_path('docker')
    try:
        process = subprocess.Popen(run_script)
        code = process.wait()
    except Exception as e:
        if e.errno != errno.ECONNRESET:
            raise
        pass
    return code

def get_driver_path(dname):
    rpath = _addon.getAddonInfo('path') + 'bin' + os.path.sep + dname + os.path.sep
    system = platform.system().lower()
    if 'windows' in system or xbmc.getCondVisibility('system.platform.windows'):
        result = rpath + 'win32' + os.path.sep + dname
    if 'linux' in system or xbmc.getCondVisibility('system.platform.linux'):
        result = rpath + 'linux64' + os.path.sep + dname
        if xbmc.getCondVisibility('system.platform.android'):
            result = rpath + 'android' + os.path.sep + dname        
        if dname == 'docker':
            result = result + '.start'
        os.system('chmod +x ' + result)
    return result
