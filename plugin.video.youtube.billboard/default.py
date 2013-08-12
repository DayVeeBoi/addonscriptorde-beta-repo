#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import xbmcaddon
import xbmcplugin
import xbmcgui
import random
import sqlite3
import sys
import re
import os

addon = xbmcaddon.Addon()
pluginhandle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
xbox = xbmc.getCondVisibility("System.Platform.xbox")
socket.setdefaulttimeout(30)
opener = urllib2.build_opener()
userAgent = "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0"
opener.addheaders = [('User-Agent', userAgent)]
urlMain = "http://www.billboard.com"


def getDbPath():
    path = xbmc.translatePath("special://userdata/Database")
    files = os.listdir(path)
    latest = ""
    for file in files:
        if file[:8] == 'MyVideos' and file[-3:] == '.db':
            if file > latest:
                latest = file
    return os.path.join(path, latest)


def getPlayCount(url):
    c.execute('SELECT playCount FROM files WHERE strFilename=?', [url])
    result = c.fetchone()
    if result:
        result = result[0]
        if result:
            return int(result)
        return 0
    return -1


def index():
    addDir("Hot100", urlMain+"/rss/charts/hot-100", "listVideos")
    addDir("Pop", urlMain+"/rss/charts/pop-songs", "listVideos")
    addDir("Rock", urlMain+"/rss/charts/rock-songs", "listVideos")
    addDir("Alternative", urlMain+"/rss/charts/alternative-songs", "listVideos")
    addDir("R&B/Hip-Hop", urlMain+"/rss/charts/r-b-hip-hop-songs", "listVideos")
    addDir("Country", urlMain+"/rss/charts/country-songs", "listVideos")
    addDir("Latin", urlMain+"/rss/charts/latin-songs", "listVideos")
    addDir("Dance/Electronic", urlMain+"/rss/charts/dance-electronic-songs", "listVideos")
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideos(url):
    xbmcplugin.setContent(pluginhandle, "episodes")
    addDir("[B]- "+translation(30001)+"[/B]", url, "autoPlay", "all")
    addDir("[B]- "+translation(30002)+"[/B]", url, "autoPlay", "random")
    addDir("[B]- "+translation(30003)+"[/B]", url, "autoPlay", "unwatched")
    content = opener.open(url).read()
    match = re.compile('<item>.+?<title>(.+?)</title>', re.DOTALL).findall(content)
    for title in match:
        title = cleanTitle(title[title.find(":")+1:])
        addLink(cleanTitle(title), title, "playVideo", "")
    xbmcplugin.endOfDirectory(pluginhandle)


def playVideo(title):
    #API sometimes delivers other results when sorting by relevance than site search!?!
    #content = opener.open("http://gdata.youtube.com/feeds/api/videos?vq="+urllib.quote_plus(title)+"&max-results=1&start-index=1&orderby=relevance&time=all_time&v=2").read()
    #match=re.compile('<yt:videoid>(.+?)</yt:videoid>', re.DOTALL).findall(content)
    content = opener.open("https://www.youtube.com/results?search_query="+urllib.quote_plus(title)+"&lclk=video").read()
    content = content[content.find('id="search-results"'):]
    match=re.compile('data-context-item-id="(.+?)"', re.DOTALL).findall(content)
    if xbox:
        url = "plugin://video/YouTube/?path=/root/video&action=play_video&videoid=" + match[0]
    else:
        url = "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=" + match[0]
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def autoPlay(url, type):
    entries = []
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    content = opener.open(url).read()
    match = re.compile('<item>.+?<title>(.+?)</title>', re.DOTALL).findall(content)
    for title in match:
        title = cleanTitle(title[title.find(":")+1:])
        url = sys.argv[0]+"?url="+urllib.quote_plus(title)+"&mode=playVideo"
        if type in ["all", "random"]:
            listitem = xbmcgui.ListItem(title)
            entries.append([title, url])
        elif type=="unwatched" and getPlayCount(url) < 0:
            listitem = xbmcgui.ListItem(title)
            entries.append([title, url])
    if type=="random":
        random.shuffle(entries)
    for title, url in entries:
        listitem = xbmcgui.ListItem(title)
        playlist.add(url, listitem)
    xbmc.Player().play(playlist)


def translation(id):
    return addon.getLocalizedString(id).encode('utf-8')


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#039;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
    title = title.strip()
    return title


def addLink(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, type=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&type="+str(type)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png")
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
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


dbPath = getDbPath()
conn = sqlite3.connect(dbPath)
c = conn.cursor()

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
type = urllib.unquote_plus(params.get('type', ''))

if mode == 'listVideos':
    listVideos(url)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'autoPlay':
    autoPlay(url, type)
else:
    index()
