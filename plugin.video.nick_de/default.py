#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import sys
import re
import os
import random
import xbmcplugin
import xbmcgui
import xbmcaddon

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.nick_de'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
jrOnly = addon.getSetting("jrOnly") == "true"
forceViewMode = addon.getSetting("forceView") == "true"
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == "true"
viewMode = str(addon.getSetting("viewID"))
translation = addon.getLocalizedString
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
iconJr = xbmc.translatePath('special://home/addons/'+addonID+'/iconJr.png')
urlMain = "http://www.nick.de"
urlMainJR = "http://www.nickjr.de"
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')]


def index():
    if jrOnly:
        nickJrMain()
    else:
        addDir(translation(30001), "", 'nickMain', icon)
        addDir(translation(30002), "", 'nickJrMain', iconJr)
        xbmcplugin.endOfDirectory(pluginhandle)


def nickMain():
    addDir(translation(30003), urlMain+"/videos", 'listVideos', icon)
    addDir(translation(30004), urlMain+"/videos", 'listShows', icon)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def nickJrMain():
    addDir(translation(30003), urlMainJR+"/videos", 'listVideosJR', iconJr)
    addDir(translation(30004), urlMainJR+"/videos", 'listShowsJR', iconJr)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listVideos(url):
    content = opener.open(url).read()
    spl = content.split("class='playlist-item'")
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match1 = re.compile("class='title'>(.+?)<", re.DOTALL).findall(entry)
        match2 = re.compile("class='subtitle'>(.*?)<", re.DOTALL).findall(entry)
        title = match1[0]
        if match2 and match2[0]:
            title = title+" - "+match2[0]
        title = cleanTitle(title)
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0].replace("140x105","640x")
        match = re.compile("href='(.+?)'", re.DOTALL).findall(entry)
        url = match[0]
        addLink(title, url, 'playVideo', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listShows(url):
    content = opener.open(url).read()
    match = re.compile('<li class=\'item\'><a href="(.+?)".*?alt="(.+?)" src="(.+?)"', re.DOTALL).findall(content)
    for url, title, thumb in match:
        if url.startswith("/shows/"):
            title = title[:title.rfind(" - ")]
            title = cleanTitle(title)
            addDir(title, urlMain+url, 'listVideos', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listShowsJR(url):
    content = opener.open(url).read()
    content = content[content.find("id='teaser_collection_featured_franchise_videos'"):]
    spl = content.split("class='teaser_item'")
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
        title = match[0]
        title = cleanTitle(title)
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0]
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = urlMainJR+match[0]
        addDir(title, url, 'listVideosJR', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listVideosJR(url):
    content = opener.open(url).read()
    if "id='teaser_collection_videos_hub_newest'" in content:
        content = content[content.find("id='teaser_collection_videos_hub_newest'"):]
        content = content[:content.find("<!-- all shows -->")]
    spl = content.split("class='teaser_item'")
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
        title = match[0]
        title = cleanTitle(title)
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0]
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = urlMainJR+match[0]
        addLink(title, url, 'playVideo', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def playVideo(url):
    content = opener.open(url).read()
    match1 = re.compile('flashvars.*?mrss.*?"(.+?)"', re.DOTALL).findall(content)
    match2 = re.compile("flashvars.*?mrss.*?'(.+?)'", re.DOTALL).findall(content)
    if urlMain in url:
        content = opener.open(match1[0]).read()
    elif urlMainJR in url:
        content = opener.open(match2[0]).read()
    match = re.compile("<media:content.+?url='(.+?)'", re.DOTALL).findall(content)
    content = opener.open(match[0]).read()
    match = re.compile('type="video/mp4" bitrate="(.+?)">.+?<src>(.+?)</src>', re.DOTALL).findall(content)
    bitrate = 0
    for br, urlTemp in match:
        if int(br) > bitrate:
            bitrate = int(br)
            finalUrl = urlTemp
    listitem = xbmcgui.ListItem(path=finalUrl+" swfVfy=1 swfUrl=http://player.mtvnn.com/g2/g2player_2.1.7.swf")
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def queueVideo(url, name, thumb):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name, thumbnailImage=thumb)
    playlist.add(url, listitem)


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#039;", "\\").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö").replace("&#x27;", "'")
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
    liz.setProperty('IsPlayable', 'true')
    liz.addContextMenuItems([(translation(30006), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+str(name)+'&thumb='+urllib.quote_plus(iconimage)+')',)])
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
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))

if mode == 'listVideos':
    listVideos(url)
elif mode == 'listVideosJR':
    listVideosJR(url)
elif mode == 'listShows':
    listShows(url)
elif mode == 'listShowsJR':
    listShowsJR(url)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'queueVideo':
    queueVideo(url, name, thumb)
elif mode == 'nickMain':
    nickMain()
elif mode == 'nickJrMain':
    nickJrMain()
else:
    index()
