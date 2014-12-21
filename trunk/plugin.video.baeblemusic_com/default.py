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
addonID = 'plugin.video.baeblemusic_com'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
forceViewMode = addon.getSetting("forceViewMode") == "true"
viewMode = str(addon.getSetting("viewMode"))
maxBitRate = addon.getSetting("maxBitRate")
maxBitRate = [360000, 580000, 1160000, 1560000, 2160000, 2760000, 3560000][int(maxBitRate)]
translation = addon.getLocalizedString
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0')]
urlMain = "http://www.baeblemusic.com"


def index():
    addDir("Concerts", "getAllConcerts", 'listVideosMain', "")
    addDir("Sessions", "getAllGuestApt", 'listVideosMain', "")
    addDir("Music Videos", "getAllMusicVideosWithDisplay", 'listVideosMain', "")
    addDir("Interviews", "getAllInterviewVideos", 'listVideosMain', "")
    addDir("Artists", "getAllBandsWithDisplay", 'listVideosMain', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideosMain(url):
    addDir("Most Recent", url+":newest:1", 'listVideos', "")
    addDir("Trending", url+":trend:1", 'listVideos', "")
    addDir("Highest Rated", url+":rated:1", 'listVideos', "")
    addDir("Most Viewed", url+":viewed:1", 'listVideos', "")
    addDir("Staff Picks", url+":picks:1", 'listVideos', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideos(url):
    type = url.split(":")[0]
    sorting = url.split(":")[1]
    page = url.split(":")[2]
    data = """<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <"""+type+""" xmlns="http://www.baeblemusic.com">
      <inSortBy>"""+sorting+"""</inSortBy>
      <inPageNum>"""+page+"""</inPageNum>
    </"""+type+""">
  </soap12:Body>
</soap12:Envelope>"""
    headers = {'Host':'www.baeblemusic.com', 'Content-Type':'application/soap+xml; charset=utf-8', 'Content-Length':len(data)}
    req = urllib2.Request("http://www.baeblemusic.com/webservices/baeble.asmx", data, headers)
    content = urllib2.urlopen(req).read()
    spl = content.split('&lt;table&gt;')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = match[0]
        match = re.compile('color:#FFF"&gt;(.+?)&lt;', re.DOTALL).findall(entry)
        title = cleanTitle(match[0])
        match = re.compile('color:#000"&gt;(.+?)&lt;', re.DOTALL).findall(entry)
        if match and type!="getAllInterviewVideos":
            title += " - "+cleanTitle(match[0])
        match = re.compile('color:#000;"&gt;(.+?)&lt;', re.DOTALL).findall(entry)
        desc = ""
        if match:
            desc = cleanTitle(match[0])
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0]#.replace("-320.jpg",".jpg")
        if type=="getAllBandsWithDisplay":
            addDir(title, url, 'listArtistVideos', thumb)
        else:
            addLink(title, url, 'playVideo', thumb, desc)
    addDir("Next Page", type+":"+sorting+":"+str(int(page)+1), 'listVideos', "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listArtistVideos(url):
    content = opener.open(url).read()
    spl = content.split('overflow:hidden"><a')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = urlMain+match[0]
        match = re.compile('<div style="font-family:Arial;.+?>(.+?)<.+?href=.+?>(.+?)<', re.DOTALL).findall(entry)
        title = cleanTitle(match[0][0]+" - "+match[0][1])
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0]#.replace("-320.jpg",".jpg")
        addLink(title, url, 'playVideo', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def playVideo(url):
    content = opener.open(url).read()
    match = re.compile('file: "(.+?)"', re.DOTALL).findall(content)
    streamUrl = ""
    for url in match:
        if url.endswith(".m3u8"):
            streamUrl = url
    if not streamUrl:
        for url in match:
            if url.endswith(".mp4"):
                streamUrl = url
    if streamUrl.endswith(".m3u8"):
        content = opener.open(streamUrl).read()
        mainUrl = streamUrl[:streamUrl.rfind("/")]
        match = re.compile('BANDWIDTH=(.+?)\n(.+?).m3u8', re.DOTALL).findall(content)
        streamUrl = ""
        bitrate = 0
        for bitrateTemp, url in match:
            if int(bitrateTemp) <= maxBitRate and int(bitrateTemp) >= bitrate:
                streamUrl = mainUrl+"/"+url+".m3u8"
                bitrate = int(bitrateTemp)
    listitem = xbmcgui.ListItem(path=streamUrl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def queueVideo(url, name, thumb):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name, thumbnailImage=thumb)
    playlist.add(url, listitem)


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#039;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
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
    liz.setProperty('IsPlayable', 'true')
    liz.addContextMenuItems([(translation(30007), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+str(name)+'&thumb='+urllib.quote_plus(iconimage)+')',)])
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
elif mode == 'listVideosMain':
    listVideosMain(url)
elif mode == 'listArtistVideos':
    listArtistVideos(url)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'queueVideo':
    queueVideo(url, name, thumb)
else:
    index()
