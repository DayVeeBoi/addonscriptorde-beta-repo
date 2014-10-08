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
addonID = 'plugin.video.fernsehkritik_tv'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
forceViewMode = addon.getSetting("forceViewMode") == "true"
viewMode = str(addon.getSetting("viewMode"))
translation = addon.getLocalizedString
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0')]
urlMain = "http://fernsehkritik.tv"


def index():
    content = opener.open(urlMain+"/tv-magazin/komplett/").read()
    spl = content.split('<div class="lclmo" id=')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<a href="(.+?)">(.+?)</a>', re.DOTALL).findall(entry)
        url = urlMain+match[0][0]
        title = match[0][1].replace('&quot;','')
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0]
        thumb = urlMain+thumb.replace('../', '/')
        addLink(title, url, "playVideo", thumb)
    xbmcplugin.endOfDirectory(pluginhandle)


def playVideo(url):
    try:
        content = opener.open(url+"/Start").read()
        match = re.compile(r'var flattr_tle = \'(.+?)\'', re.DOTALL).findall(content)
        title = match[0]
        if 'playlist = [' in content:
            content = content[content.find('playlist = ['):]
            content = content[:content.find('];')]
            match = re.compile(r"\{ url: base \+ '(\d+(?:-\d+)?\.flv)' \}", re.DOTALL).findall(content)
            urlFull="stack://"
            for i,filename in enumerate(match):
              url = 'http://dl' + str(random.randint(2, 3)) + '.fernsehkritik.tv/fernsehkritik' + filename + " , "
              urlFull += url
            urlFull=urlFull[:-3]
            listitem = xbmcgui.ListItem(path=urlFull)
            xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
        else:
            match = re.compile("file=='(.+?)'", re.DOTALL).findall(content)
            filename = match[0]
            listitem = xbmcgui.ListItem(path='http://dl' + str(random.randint(1,3)) + '.fernsehkritik.tv/antik/' + filename)
            xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
    except:
        xbmc.executebuiltin('XBMC.Notification(Info:,Folge ist noch nicht verfügbar!,5000,'+icon+')')


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
    liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Duration": duration})
    liz.setProperty('IsPlayable', 'true')
    liz.addContextMenuItems([(translation(30001), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+str(name)+'&thumb='+urllib.quote_plus(iconimage)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))

if mode == 'playVideo':
    playVideo(url)
elif mode == 'queueVideo':
    queueVideo(url, name, thumb)
else:
    index()
