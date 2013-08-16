#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import re
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin

addon = xbmcaddon.Addon()
pluginhandle = int(sys.argv[1])
forceViewMode = addon.getSetting("forceViewMode") == "true"
viewMode = str(addon.getSetting("viewMode"))


def index():
    xbmcplugin.setContent(pluginhandle, "episodes")
    content = getUrl("http://pantoffel.tv/magazin/")
    spl = content.split('<h1 class="magtitle"')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('>(.+?)<', re.DOTALL).findall(entry)
        title = match[0]
        match = re.compile('<small class="pull-right">(.+?)</small>', re.DOTALL).findall(entry)
        desc1 = match[0]
        match = re.compile('<p style=".+?">(.+?)</p>', re.DOTALL).findall(entry)
        desc2 = match[0]
        desc = desc1+"\n"+desc2
        length = desc1.split(" ")[0]
        date = desc1.split("/")[1].strip()
        splDate = date.split(".")
        date = splDate[2]+"-"+splDate[1]+"-"+splDate[0]
        match = re.compile('<a href="/hd.php\\?ep=(.+?)"', re.DOTALL).findall(entry)
        url = "http://pantoffel.tv/hd.php?ep="+match[0]
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0]
        addLink(title, url, 'playVideo', thumb, length, desc, date)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')
    xbmcplugin.endOfDirectory(pluginhandle)


def playVideo(url):
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def getUrl(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20100101 Firefox/22.0')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addLink(name, url, mode, iconimage, length, desc, date):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Duration": length, "Plot": desc, "Aired": date})
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))

if mode == 'playVideo':
    playVideo(url)
else:
    index()
