#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import re
import sys
import xbmcplugin
import xbmcgui
import xbmcaddon

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.atv_at'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
translation = addon.getLocalizedString
forceViewMode = addon.getSetting("forceViewMode") == "true"
viewMode = str(addon.getSetting("viewMode"))
urlMain = "http://atv.at"


def index():
    content = getUrl(urlMain+"/mediathek")
    spl = content.split('class="program"')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('alt="(.+?)"', re.DOTALL).findall(entry)
        title = match[0]
        title = cleanTitle(title)
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = match[0]
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0]
        addDir(title, url, 'listVideos', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideos(url):
    content = getUrl(url)
    contentMain = content
    if 'class="teaser_list"' in content:
        content = content[content.find('class="teaser_list"'):]
        content = content[:content.find('</ul>')]
    spl = content.split('class="teaser"')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = match[0]
        match = re.compile('class="title">(.+?)<', re.DOTALL).findall(entry)
        title = cleanTitle(match[0])
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0].replace("&amp;","&")
        addLink(title, url, 'playVideo', thumb)
    match = re.compile('jsb_MoreTeasersButton" data-jsb="url=(.+?)"', re.DOTALL).findall(contentMain)
    if match:
        addDir(translation(30001), urllib.unquote_plus(match[0]), 'listVideos', "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def playVideo(url):
    content = getUrl(url)
    matchUrls = re.compile('streaming&.+?src&.+?http:(.+?)&', re.DOTALL).findall(content)
    req = urllib2.Request("http:"+matchUrls[0].replace("\\", ""))
    try:
        urllib2.urlopen(req)
        if len(matchUrls) > 1:
            urlFull = "stack://"
            for url in matchUrls:
                if "m3u8" in url:
                    urlFull += "http:"+url.replace("\\", "")+" , "
            urlFull = urlFull[:-3]
            listitem = xbmcgui.ListItem(path=urlFull)
            xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
        elif len(matchUrls) == 1:
            urlFull = "http:"+matchUrls[0].replace("\\", "")
            listitem = xbmcgui.ListItem(path=urlFull)
            xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
    except:
        xbmc.executebuiltin('XBMC.Notification(Info:,'+str(translation(30002))+',5000)')


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#039;", "\\").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
    title = title.replace("\\u00c4", "Ä").replace("\\u00e4", "ä").replace("\\u00d6", "Ö").replace("\\u00f6", "ö").replace("\\u00dc", "Ü").replace("\\u00fc", "ü").replace("\\u00df", "ß")
    title = title.strip()
    return title


def getUrl(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:23.0) Gecko/20100101 Firefox/23.0')
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


def addLink(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = params.get('mode')
url = params.get('url')
if isinstance(url, type(str())):
    url = urllib.unquote_plus(url)

if mode == 'listVideos':
    listVideos(url)
elif mode == 'playVideo':
    playVideo(url)
else:
    index()
