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
    rpath = _addon.getAddonInfo('path') + os.path.sep + 'bin' + os.path.sep + dname + os.path.sep
    if platform.system() == 'Windows':
        result = rpath + 'win32' + os.path.sep + dname
    if platform.system() == 'Linux':
        result = rpath + 'linux64' + os.path.sep + dname
        if dname == 'docker':
            result = result + '.start'
        os.system('chmod +x ' + result)
    return result
