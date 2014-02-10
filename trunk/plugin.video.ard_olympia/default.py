#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import sys
import re
import os
import xbmcplugin
import xbmcgui
import xbmcaddon

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.ard_olympia'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
translation = addon.getLocalizedString
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
baseUrl = "http://ard.br.de"
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')]


def index():
    addDir("LIVE", url, 'live', icon)
    addDir("On Demand", url, 'ondemand', icon)
    xbmcplugin.endOfDirectory(pluginhandle)


def live():
    content = opener.open(baseUrl+"/olympia-sotschi-2014/live/index.html").read()
    spl = content.split('data-ctrl-liveDashboard-livestream=')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<p><strong>(.+?)</strong></p>', re.DOTALL).findall(entry)
        title = match[0]
        match = re.compile('class="time">(.+?)<', re.DOTALL).findall(entry)
        title = match[0]+" - "+title
        title = cleanTitle(title)
        match = re.compile("'playerXml':'(.+?)'", re.DOTALL).findall(entry)
        url = baseUrl+match[0]
        match = re.compile("'src':'(.+?)'", re.DOTALL).findall(entry)
        thumb = baseUrl+match[0]
        thumb = thumb[:thumb.rfind("~")]+".jpg"
        addLink(title, url, 'playLive', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.executebuiltin('Container.SetViewMode(51)')


def ondemand():
    content = opener.open(baseUrl+"/olympia-sotschi-2014/zeitplan/index.html").read()
    spl = content.split('<div data-ctrl-klappe-klappe')
    for i in range(len(spl)-1, 0, -1):
        entry = spl[i]
        if ">on demand<" in entry:
            match = re.compile('class="disciplineInformation">.+?>(.+?)</span>.+?>(.+?)<', re.DOTALL).findall(entry)
            title = match[0][0]+" "+match[0][1]
            match = re.compile('<h4>(.+?)</h4>', re.DOTALL).findall(entry)
            title = match[0]+" - "+title
            match = re.compile("'filters':\\['2014-(.+?)-(.+?)'", re.DOTALL).findall(entry)
            title = match[0][1]+"."+match[0][0]+" - "+title
            title = cleanTitle(title)
            match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
            url = baseUrl+match[0]
            addLink(title, url, 'playVideo', icon)
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.executebuiltin('Container.SetViewMode(51)')


def playVideo(url):
    content = opener.open(url).read()
    match = re.compile("dataURL:'(.+?)'", re.DOTALL).findall(content)
    content = opener.open(baseUrl+match[0]).read()
    match = re.compile('<iOSStreamingUrl>(.+?)</iOSStreamingUrl>', re.DOTALL).findall(content)
    finalUrl = match[0]
    try:
        opener.open(finalUrl)
        listitem = xbmcgui.ListItem(path=finalUrl)
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
    except:
        xbmc.executebuiltin('XBMC.Notification(Info:,Sorry. Not available in your country!,10000)')


def playLive(url):
    content = opener.open(url).read()
    match = re.compile('<asset type="Live HLS">.+?<url>(.+?)</url>', re.DOTALL).findall(content)
    finalUrl = match[0]
    try:
        opener.open(finalUrl)
        listitem = xbmcgui.ListItem(path=finalUrl)
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
    except:
        xbmc.executebuiltin('XBMC.Notification(Info:,Sorry. Not available in your country!,10000)')


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#039;", "\\").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
    title = title.strip()
    return title


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addLink(name, url, mode, iconimage, desc="", duration=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Duration": duration})
    if iconimage!=icon:
        liz.setProperty("fanart_image", iconimage)
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage, desc="", duration=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Duration": duration})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))

if mode == 'live':
    live()
elif mode == 'ondemand':
    ondemand()
elif mode == 'playLive':
    playLive(url)
elif mode == 'playVideo':
    playVideo(url)
else:
    index()
