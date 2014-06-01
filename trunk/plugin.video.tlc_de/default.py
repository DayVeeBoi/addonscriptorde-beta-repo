#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import re
import os
import urllib
import urllib2
import httplib
import cookielib
import socket
import xbmcgui
import xbmcaddon
import xbmcplugin
from pyamf import remoting

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.tlc_de'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
xbox = xbmc.getCondVisibility("System.Platform.xbox")
translation = addon.getLocalizedString
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == "true"
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
userDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
channelFavsFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/"+addonID+".favorites")
forceViewMode = addon.getSetting("forceView") == "true"
autoPlay = addon.getSetting("autoPlay") == "true"
viewMode = str(addon.getSetting("viewID"))
maxBitRate = addon.getSetting("maxBitRate")
qual = [512000, 1024000, 1536000, 2048000, 2560000, 3072000]
maxBitRate = qual[int(maxBitRate)]
baseUrl = "http://www.tlc.de"
opener = urllib2.build_opener()
userAgent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0"
opener.addheaders = [('User-Agent', userAgent)]

if not os.path.isdir(userDataFolder):
    os.mkdir(userDataFolder)


def index():
    addDir(translation(30003), baseUrl+"/videos/", 'listVideos', icon)
    addDir(translation(30002), baseUrl+"/wp-content/plugins/dni_plugin_core/ajax.php?action=dni_listing_items_filter&letter=&page=1&id=e00903&post_id=4797&view_type=grid", 'listShows', icon)
    addDir(translation(30010), "", 'listShowsFavs', icon)
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideos(urlMain):
    content = opener.open(urlMain).read()
    spl = content.split('<div class="dni-video-playlist-thumb-box')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('data-content="(.+?)"', re.DOTALL).findall(entry) 
        title = cleanTitle(match[0])
        match = re.compile('href="#(.+?)"', re.DOTALL).findall(entry)
        videoID = match[0]
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0]
        addLink(title, videoID, 'playVideo', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listShows(urlMain):
    content = opener.open(urlMain).read()
    content = content.replace("\\", "")
    spl = content.split('<a')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<h3>(.+?)<\/h3>', re.DOTALL).findall(entry)
        title = match[0]
        if "(" in title:
            title = title[:title.rfind("(")].strip()
        title = cleanTitle(title)
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = match[0]
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = cleanTitle(match[0]).replace("_thumb", "")
        addShowDir(title, url, 'listVideos', thumb)
    #try:
    matchCurrent = re.compile('"current_page":"(.+?)"', re.DOTALL).findall(content)
    matchTotal = re.compile('"total_pages":(.+?),', re.DOTALL).findall(content)
    currentPage = matchCurrent[0]
    nextPage = str(int(currentPage)+1)
    totalPages = matchTotal[0]
    if int(currentPage) < int(totalPages):
        addDir(translation(30001)+" ("+nextPage+")", urlMain.replace("page="+currentPage, "page="+nextPage), 'listShows', icon)
    #except:
    #    pass
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def playVideo(bc_videoID):
    bc_playerID = 3303851611001
    bc_publisherID = 1659832546
    bc_const = "8217bffb94dc0fc594db459f4df970a0ea06e4b5"
    conn = httplib.HTTPConnection("c.brightcove.com")
    envelope = remoting.Envelope(amfVersion=3)
    envelope.bodies.append(("/1", remoting.Request(target="com.brightcove.player.runtime.PlayerMediaFacade.findMediaById", body=[bc_const, bc_playerID, bc_videoID, bc_publisherID], envelope=envelope)))
    conn.request("POST", "/services/messagebroker/amf?playerId=" + str(bc_playerID), str(remoting.encode(envelope).read()), {'content-type': 'application/x-amf'})
    response = conn.getresponse().read()
    response = remoting.decode(response).bodies[0][1].body
    streamUrl = ""
    for item in sorted(response['renditions'], key=lambda item: item['encodingRate'], reverse=False):
        encRate = item['encodingRate']
        if encRate < maxBitRate:
            streamUrl = item['defaultURL']
    if not streamUrl:
        streamUrl = response['FLVFullLengthURL']
    if streamUrl:
        listitem = xbmcgui.ListItem(path=streamUrl)
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
        if autoPlay:
            while True:
                if xbmc.Player().isPlaying() and xbmc.getCondVisibility("Player.Paused"):
                    xbmc.Player().pause()
                    break
                xbmc.sleep(100)
            xbmc.sleep(500)
            while xbmc.getCondVisibility("Player.Paused"):
                if xbmc.Player().isPlaying():
                    xbmc.Player().pause()
                    break
                xbmc.sleep(100)


def queueVideo(url, name, thumb):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name, thumbnailImage=thumb)
    playlist.add(url, listitem)


def listShowsFavs():
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    if os.path.exists(channelFavsFile):
        fh = open(channelFavsFile, 'r')
        all_lines = fh.readlines()
        for line in all_lines:
            title = line[line.find("###TITLE###=")+12:]
            title = title[:title.find("#")]
            url = line[line.find("###URL###=")+10:]
            url = url[:url.find("#")]
            thumb = line[line.find("###THUMB###=")+12:]
            thumb = thumb[:thumb.find("#")]
            addShowRDir(title, urllib.unquote_plus(url), "listVideos", thumb)
        fh.close()
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def favs(param):
    mode = param[param.find("###MODE###=")+11:]
    mode = mode[:mode.find("###")]
    channelEntry = param[param.find("###TITLE###="):]
    if mode == "ADD":
        if os.path.exists(channelFavsFile):
            fh = open(channelFavsFile, 'r')
            content = fh.read()
            fh.close()
            if content.find(channelEntry) == -1:
                fh = open(channelFavsFile, 'a')
                fh.write(channelEntry+"\n")
                fh.close()
        else:
            fh = open(channelFavsFile, 'a')
            fh.write(channelEntry+"\n")
            fh.close()
    elif mode == "REMOVE":
        refresh = param[param.find("###REFRESH###=")+14:]
        refresh = refresh[:refresh.find("#")]
        fh = open(channelFavsFile, 'r')
        content = fh.read()
        fh.close()
        entry = content[content.find(channelEntry):]
        fh = open(channelFavsFile, 'w')
        fh.write(content.replace(channelEntry+"\n", ""))
        fh.close()
        if refresh == "TRUE":
            xbmc.executebuiltin("Container.Refresh")


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#039;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
    title = title.replace("u00c4", "Ä").replace("u00e4", "ä").replace("u00d6", "Ö").replace("u00f6", "ö").replace("u00dc", "Ü").replace("u00fc", "ü").replace("u00df", "ß").replace("u2013", "–")
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


def addLink(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&title="+urllib.quote_plus(name)+"&thumb="+urllib.quote_plus(iconimage)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.setProperty('IsPlayable', 'true')
    if useThumbAsFanart and iconimage != icon:
        liz.setProperty("fanart_image", iconimage)
    liz.addContextMenuItems([(translation(30009), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&title='+str(name)+'&thumb='+urllib.quote_plus(iconimage)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    if useThumbAsFanart and iconimage != icon:
        liz.setProperty("fanart_image", iconimage)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addShowDir(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&title="+urllib.quote_plus(name)+"&thumb="+urllib.quote_plus(iconimage)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    if useThumbAsFanart and iconimage != icon:
        liz.setProperty("fanart_image", iconimage)
    playListInfos = "###MODE###=ADD###TITLE###="+name+"###URL###="+urllib.quote_plus(url)+"###THUMB###="+iconimage+"###END###"
    liz.addContextMenuItems([(translation(30011), 'RunPlugin(plugin://'+addonID+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addShowRDir(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&title="+urllib.quote_plus(name)+"&thumb="+urllib.quote_plus(iconimage)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    if useThumbAsFanart and iconimage != icon:
        liz.setProperty("fanart_image", iconimage)
    playListInfos = "###MODE###=REMOVE###REFRESH###=TRUE###TITLE###="+name+"###URL###="+urllib.quote_plus(url)+"###THUMB###="+iconimage+"###END###"
    liz.addContextMenuItems([(translation(30012), 'RunPlugin(plugin://'+addonID+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
isSingle = urllib.unquote_plus(params.get('isSingle', 'yes'))
thumb = urllib.unquote_plus(params.get('thumb', ''))
title = urllib.unquote_plus(params.get('title', ''))

if mode == 'listVideos':
    listVideos(url)
elif mode == 'listShows':
    listShows(url)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'queueVideo':
    queueVideo(url, title, thumb)
elif mode == 'listShowsFavs':
    listShowsFavs()
elif mode == 'favs':
    favs(url)
else:
    index()
