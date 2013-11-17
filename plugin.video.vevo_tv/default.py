#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import urllib
import xbmcplugin
import xbmcgui
import xbmcaddon

addon = xbmcaddon.Addon()
pluginhandle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
translation = addon.getLocalizedString
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
quality = addon.getSetting("quality")
quality = ["stream2272000", "stream512000"][int(quality)]

def index():
    addLink("VEVO TV (US)", "", 'playUS', icon)
    addLink("VEVO TV (EU)", "", 'playEU', icon)
    xbmcplugin.endOfDirectory(pluginhandle)


def playUS():
    fullUrl = "rtmp://vevohp2livefs.fplive.net:1935/vevohp2live-live/ playpath="+quality
    listitem = xbmcgui.ListItem(path=fullUrl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def playEU():
    fullUrl = "rtmp://vevoeu01livefs.fplive.net:1935/vevoeu01live-live/ playpath="+quality
    listitem = xbmcgui.ListItem(path=fullUrl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addLink(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))

if mode == 'playUS':
    playUS()
elif mode == 'playEU':
    playEU()
else:
    index()
