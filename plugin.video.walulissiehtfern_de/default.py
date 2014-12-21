#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import xbmcaddon
import xbmcplugin
import xbmcgui
import sys
import re

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.walulissiehtfern_de'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
xbox = xbmc.getCondVisibility("System.Platform.xbox")
translation = addon.getLocalizedString
forceViewMode = addon.getSetting("forceView") == "true"
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
viewMode = str(addon.getSetting("viewID"))
baseUrl = "http://www.walulissiehtfern.de"


def index():
    content = getUrl(baseUrl+"/folgen/")
    spl = content.split('class="mainvideo_bild">')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('alt="(.+?)"', re.DOTALL).findall(entry)
        title = match[0]
        title = cleanTitle(title)
        match = re.compile('<div class="text_description">.+?>(.+?)<', re.DOTALL).findall(entry)
        desc = match[0]
        desc = cleanTitle(desc)
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = match[0].replace("../",baseUrl+"/")
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0].replace("../",baseUrl+"/")
        addLink(title, url, "playVideo", thumb, desc)
    xbmcplugin.endOfDirectory(pluginhandle)


def playVideo(url):
    content = getUrl(url)
    match = re.compile('"src": ".+?youtube.com/watch\\?v=(.+?)"', re.DOTALL).findall(content)
    if xbox:
        url = "plugin://video/YouTube/?path=/root/video&action=play_video&videoid=" + match[0]
    else:
        url = "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=" + match[0]
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def getUrl(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')
    response = urllib2.urlopen(req)
    content = response.read()
    response.close()
    return content


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#039;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
    title = title.strip()
    return title


def addLink(name, url, mode, iconimage, desc=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    liz.setProperty('IsPlayable', 'true')
    liz.setProperty("fanart_image", iconimage)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))

if mode == 'playVideo':
    playVideo(url)
else:
    index()
