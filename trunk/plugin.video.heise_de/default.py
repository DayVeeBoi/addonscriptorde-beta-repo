#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import sys
import re
import os
import json
import random
import xbmcplugin
import xbmcgui
import xbmcaddon

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.heise_de'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
forceViewMode = addon.getSetting("forceView") == "true"
viewMode = str(addon.getSetting("viewID"))
maxQuality = addon.getSetting("maxQuality")
maxQuality = [360, 720][int(maxQuality)]
translation = addon.getLocalizedString
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0')]
urlMain = "http://www.heise.de"


def index():
    addDir("Meistgesehene Videos", "", 'listVideosTop', "")
    content = opener.open(urlMain+"/video").read()
    contentMain = content
    content = content[content.find('id="teaser_reiter_nav"'):]
    content = content[:content.find('</ul>')]
    match = re.compile('<li rel="(.+?)".+?href=".+?">(.+?)<', re.DOTALL).findall(content)
    for reiterID, title in match:
        match2 = re.compile('id="'+reiterID+'".+?class="clearfix more_reiter"><a href="(.+?)"', re.DOTALL).findall(contentMain)
        if match2:
            addDir(title, urlMain+"/video/"+match2[0].replace("offset=10","offset=0")+"&hajax=1", 'listVideos', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideos(url):
    content = opener.open(url).read().replace("\\","")
    spl = content.split('class="rahmen"')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<h3><a href="(.+?)">(.+?)<', re.DOTALL).findall(entry)
        url = urlMain+match[0][0]
        title = cleanTitle(match[0][1])
        match = re.compile('<p>(.+?)<', re.DOTALL).findall(entry)
        desc = cleanTitle(match[0]).replace("n        ","")
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = urlMain+match[0]
        addLink(title, url, 'playVideo', thumb, desc)
    match = re.compile('class="clearfix more_reiter"><a href="(.+?)"', re.DOTALL).findall(content)
    if match:
        addDir("Next Page", urlMain+"/video/"+match[0]+"&hajax=1", 'listVideos', "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listVideosTop():
    content = opener.open(urlMain+"/video/").read().replace("\\","")
    content = content[content.find('class="kasten video first"'):]
    content = content[:content.find('</div>')]
    spl = content.split('class="clearfix"')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<h4><a href="(.+?)">(.+?)<', re.DOTALL).findall(entry)
        url = urlMain+match[0][0]
        title = cleanTitle(match[0][1])
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0].replace("//","http://")
        addLink(title, url, 'playVideo', thumb, "")
    match = re.compile('class="clearfix more_reiter"><a href="(.+?)"', re.DOTALL).findall(content)
    if match:
        addDir("Next Page", urlMain+"/video/"+match[0]+"&hajax=1", 'listVideos', "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def playVideo(url):
    content = opener.open(url).read()
    match1 = re.compile('data-container="(.+?)"', re.DOTALL).findall(content)
    match2 = re.compile('data-sequenz="(.+?)"', re.DOTALL).findall(content)
    content = opener.open("http://www.heise.de/videout/feed?container="+match1[0]+"&sequenz="+match2[0]).read()
    match = re.compile('file="(.+?)" label="(.+?)" type="(.+?)"', re.DOTALL).findall(content)
    streamingurl = ""
    for url, res, type in match:
        if type=="video/mp4":
            streamingurl = url
            break
    listitem = xbmcgui.ListItem(path=streamingurl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def queueVideo(url, name, thumb):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name, thumbnailImage=thumb)
    playlist.add(url, listitem)


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#039;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("u2013", "-").replace("u00c4", "Ä").replace("u00dc", "Ü").replace("u00d6", "Ö").replace("u00e4", "ä").replace("u00fc", "ü").replace("u00f6", "ö").replace("u00df", "ß").replace("u00a0", " ")
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
elif mode == 'listVideosTop':
    listVideosTop()
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'queueVideo':
    queueVideo(url, name, thumb)
else:
    index()
