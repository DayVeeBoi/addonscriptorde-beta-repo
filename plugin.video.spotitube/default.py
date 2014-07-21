#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
import sys
import json
import shutil
import random
import socket
import urllib
import urllib2
import datetime
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs
import time

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.spotitube'
addon = xbmcaddon.Addon(id=addonID)
pluginhandle = int(sys.argv[1])
socket.setdefaulttimeout(30)
opener = urllib2.build_opener()
xbox = xbmc.getCondVisibility("System.Platform.xbox")
region = xbmc.getLanguage(xbmc.ISO_639_1, region=True).split("-")[1]
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
addonUserDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
cacheDir = xbmc.translatePath(addon.getSetting("cacheDir"))
blacklist = addon.getSetting("blacklist").split(',')
infoEnabled = addon.getSetting("showInfo") == "true"
infoType = addon.getSetting("infoType")
infoDelay = int(addon.getSetting("infoDelay"))
infoDuration = int(addon.getSetting("infoDuration"))
forceView = addon.getSetting("forceView") == "true"
viewIDVideos = str(addon.getSetting("viewIDVideos"))
viewIDPlaylists = str(addon.getSetting("viewIDPlaylists"))
viewIDGenres = str(addon.getSetting("viewIDGenres"))
userAgent = "Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0"
opener.addheaders = [('User-Agent', userAgent)]

if not os.path.isdir(addonUserDataFolder):
    os.mkdir(addonUserDataFolder)
if not cacheDir.startswith(('smb://', 'nfs://', 'upnp://', 'ftp://')) and not os.path.isdir(cacheDir):
    os.mkdir(cacheDir)


def index():
    addDir(translation(30002), "", "spotifyMain", "", "browse")
    addDir(translation(30003), "", "spotifyMain", "", "play")
    xbmcplugin.endOfDirectory(pluginhandle)


def spotifyMain(type):
    addDir(translation(30004), "http://api.tunigo.com/v3/space/toplists?region="+region+"&page=0&per_page=50&platform=web", "listSpotifyPlaylists", "", type)
    addDir(translation(30005), "http://api.tunigo.com/v3/space/featured-playlists?region="+region+"&page=0&per_page=50&dt="+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M").replace(":","%3A")+"%3A00&platform=web", "listSpotifyPlaylists", "", type)
    addDir(translation(30006), "http://api.tunigo.com/v3/space/genres?region="+region+"&per_page=1000&platform=web", "listSpotifyGenres", "", type)
    xbmcplugin.endOfDirectory(pluginhandle)


def listSpotifyGenres(url, type):
    content = opener.open(url).read()
    content = json.loads(content)
    for item in content['items']:
        genreID = item['genre']['templateName']
        try:
            thumb = item['genre']['iconImageUrl']
        except:
            thumb = ""
        title = item['genre']['name'].encode('utf-8')
        if title.strip().lower()!="top lists":
            addDir(title, "http://api.tunigo.com/v3/space/"+genreID+"?region="+region+"&page=0&per_page=50&platform=web", "listSpotifyPlaylists", thumb, type)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIDGenres+')')


def listSpotifyPlaylists(url, type):
    content = opener.open(url).read()
    content = json.loads(content)
    for item in content['items']:
        uri = item['playlist']['uri'].encode('utf-8')
        try:
            thumb = "http://d3rt1990lpmkn.cloudfront.net/300/"+item['playlist']['image']
        except:
            thumb = ""
        title = item['playlist']['title'].encode('utf-8')
        description = item['playlist']['description'].encode('utf-8')
        if type=="browse":
            addDir(title, uri, "listSpotifyVideos", thumb, "", description)
        elif type=="play":
            addDir(title, uri, "playSpotifyVideos", thumb, "", description)
    match=re.compile('page=(.+?)&per_page=(.+?)&', re.DOTALL).findall(url)
    currentPage = int(match[0][0])
    perPage = int(match[0][1])
    nextPage = currentPage+1
    if nextPage*perPage<content['totalItems']:
        addDir(translation(30001), url.replace("page="+str(currentPage),"page="+str(nextPage)), "listSpotifyPlaylists", "", type)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIDPlaylists+')')


def listSpotifyVideos(url):
    content = cache("https://embed.spotify.com/?uri="+url, 1)
    spl=content.split('music-paused item')
    for i in range(1,len(spl),1):
        entry=spl[i]
        match=re.compile('class="artist.+?>(.+?)<', re.DOTALL).findall(entry)
        artist=match[0]
        match=re.compile('class="track-title.+?>(.+?)<', re.DOTALL).findall(entry)
        videoTitle=match[0]
        videoTitle=videoTitle[videoTitle.find(".")+1:].strip()
        if " - " in videoTitle:
            videoTitle=videoTitle[:videoTitle.rfind(" - ")]
        if " [" in videoTitle:
            videoTitle=videoTitle[:videoTitle.rfind(" [")]
        if "," in artist:
            artist = artist.split(",")[0]
        title=cleanTitle(artist+" - "+videoTitle)
        match=re.compile('data-ca="(.+?)"', re.DOTALL).findall(entry)
        thumb=match[0]
        filtered = False
        for entry2 in blacklist:
            if entry2.strip().lower() and entry2.strip().lower() in title.lower():
                filtered = True
        if filtered:
            continue
        addLink(title, title.replace(" - ", " "), "playYTByTitle", thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')


def playSpotifyVideos(url):
    musicVideos = []
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    content = cache("https://embed.spotify.com/?uri="+url, 1)
    spl=content.split('music-paused item')
    for i in range(1,len(spl),1):
        entry=spl[i]
        match=re.compile('class="artist.+?>(.+?)<', re.DOTALL).findall(entry)
        artist=match[0]
        match=re.compile('class="track-title.+?>(.+?)<', re.DOTALL).findall(entry)
        videoTitle=match[0]
        videoTitle=videoTitle[videoTitle.find(".")+1:].strip()
        if " - " in videoTitle:
            videoTitle=videoTitle[:videoTitle.rfind(" - ")]
        if " [" in videoTitle:
            videoTitle=videoTitle[:videoTitle.rfind(" [")]
        if "," in artist:
            artist = artist.split(",")[0]
        title=cleanTitle(artist+" - "+videoTitle)
        match=re.compile('data-ca="(.+?)"', re.DOTALL).findall(entry)
        thumb=match[0]
        filtered = False
        for entry2 in blacklist:
            if entry2.strip().lower() and entry2.strip().lower() in title.lower():
                filtered = True
        if filtered:
            continue
        if xbox:
            url = "plugin://video/Spotitube Playlists/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=playYTByTitle"
        else:
            url = "plugin://"+addonID+"/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=playYTByTitle"
        musicVideos.append([title, url, thumb])
    random.shuffle(musicVideos)
    for title, url, thumb in musicVideos:
        listitem = xbmcgui.ListItem(title, thumbnailImage=thumb)
        playlist.add(url, listitem)
    xbmc.Player().play(playlist)


def playYTByTitle(title):
    try:
        youtubeID = getYoutubeId(title)
        if xbox:
            url = "plugin://video/YouTube/?path=/root/video&action=play_video&videoid=" + youtubeID
        else:
            url = "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=" + youtubeID
        listitem = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
        if infoEnabled:
            showInfo()
    except:
        pass


def getYoutubeId(title):
    content = cache("http://gdata.youtube.com/feeds/api/videos?vq="+urllib.quote_plus(title)+"&max-results=1&start-index=1&orderby=relevance&time=all_time&v=2", 1)
    match=re.compile('<yt:videoid>(.+?)</yt:videoid>', re.DOTALL).findall(content)
    return match[0]


def cache(url, duration):
    cacheFile = os.path.join(cacheDir, (''.join(c for c in unicode(url, 'utf-8') if c not in '/\\:?"*|<>')).strip())
    if os.path.exists(cacheFile) and duration!=0 and (time.time()-os.path.getmtime(cacheFile) < 60*60*24*duration):
        fh = open(cacheFile, 'r')
        content = fh.read()
        fh.close()
    else:
        content = opener.open(url).read()
        fh = open(cacheFile, 'w')
        fh.write(content)
        fh.close()
    return content


def showInfo():
    count = 0
    while not xbmc.Player().isPlaying():
        xbmc.sleep(200)
        if count==50:
            break
        count+=1
    xbmc.sleep(infoDelay*1000)
    if infoType == "0":
        xbmc.executebuiltin('XBMC.ActivateWindow(12901)')
        xbmc.sleep(infoDuration*1000)
        xbmc.executebuiltin('XBMC.ActivateWindow(12005)')
    elif infoType == "1":
        title = 'Now playing:'
        videoTitle = xbmc.getInfoLabel('VideoPlayer.Title').replace(","," ")
        thumb = xbmc.getInfoImage('VideoPlayer.Cover')
        xbmc.executebuiltin('XBMC.Notification(%s, %s, %s, %s)' % (title, videoTitle, infoDuration*1000, thumb))


def translation(id):
    return addon.getLocalizedString(id).encode('utf-8')


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
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


def addLink(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok

def addDir(name, url, mode, iconimage, type="", description=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&type="+str(type)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
type = urllib.unquote_plus(params.get('type', ''))

if mode == 'playYTByTitle':
    playYTByTitle(url)
elif mode == 'spotifyMain':
    spotifyMain(type)
elif mode == 'listSpotifyGenres':
    listSpotifyGenres(url, type)
elif mode == 'listSpotifyPlaylists':
    listSpotifyPlaylists(url, type)
elif mode == 'listSpotifyVideos':
    listSpotifyVideos(url)
elif mode == 'playSpotifyVideos':
    playSpotifyVideos(url)
elif mode == 'none':
    pass
else:
    index()
