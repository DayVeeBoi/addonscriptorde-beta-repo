#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import sys
import re
import os
import json
import xbmcplugin
import xbmcgui
import xbmcaddon

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.wettercom_tv'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
urlMain = "http://www.wettercom.tv"
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')]

def index():
    content = opener.open(urlMain+"/json/weatherChannelList").read()
    content = json.loads(content)
    for item in content["channels"]:
        addDir(item["name"].encode('utf-8'), urlMain+item["contentUrl"], 'listVideos', urlMain+item["imageUrl"], item["description"].encode('utf-8'))
    content = opener.open(urlMain+"/json/channelList").read()
    content = json.loads(content)
    for item in content["channels"]:
        addDir(item["name"].encode('utf-8'), urlMain+item["contentUrl"], 'listVideos', urlMain+item["imageUrl"], item["description"].encode('utf-8'))
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideos(url):
    content = opener.open(url).read()
    content = json.loads(content)
    for item in content["videos"]:
        try:
            title = item["title"].encode('utf-8')
            try:
                date = str(item["date"])
                date = date[:date.find("|")]
                title = date+" - "+title
            except:
                pass
            title = date+" - "+item["title"].encode('utf-8')
            addLink(title, item["mp4url"], 'playVideo', "http://ls1.wettercomassets.com"+item["thumbnailEndscreenBig"], item["description"].encode('utf-8'), item["duration"])
        except:
            for item2 in item["content"]:
                date = str(item2["date"])
                date = date[:date.find("|")]
                title = date+" - "+item2["title"].encode('utf-8')
                addLink(title, item2["mp4url"], 'playVideo', "http://ls1.wettercomassets.com"+item2["thumbnailEndscreenBig"], item2["description"].encode('utf-8'), item2["duration"])
    xbmcplugin.endOfDirectory(pluginhandle)


def playVideo(url):
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def queueVideo(url, name):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name)
    playlist.add(url, listitem)


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#039;", "\\").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
    title = title.strip()
    return title


def translation(id):
    return addon.getLocalizedString(id).encode('utf-8')


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addLink(name, url, mode, iconimage, desc, duration="", date=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Aired": date})
    if duration:
        liz.addStreamInfo('video', {'duration': duration})
    liz.setProperty('IsPlayable', 'true')
    liz.addContextMenuItems([(translation(30006), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+str(name)+'&thumb='+urllib.quote_plus(iconimage)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage, desc):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc })
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))

if mode == 'listVideos':
    listVideos(url)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'queueVideo':
    queueVideo(url, name)
else:
    index()
