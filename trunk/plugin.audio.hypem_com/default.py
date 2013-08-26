#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import cookielib
import sys
import re
import os
import json
import base64
import xbmcplugin
import xbmcgui
import xbmcaddon

socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')
cj = cookielib.LWPCookieJar()
urlMain = "http://www.hypem.com"
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
userAgent = "Mozilla/5.0 (Windows NT 5.1; rv:23.0) Gecko/20100101 Firefox/23.0"
opener.addheaders = [('User-agent', userAgent)]
addonUserDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
cookieFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/cookies")
username=addon.getSetting("username")
password=addon.getSetting("password")

if not os.path.isdir(addonUserDataFolder):
    os.mkdir(addonUserDataFolder)
if os.path.exists(cookieFile):
    cj.load(cookieFile)


def index():
    if username and password:
        login()
    if username:
        addDir(translation(30006), "", 'myMain', "")
    addDir(translation(30002) + " (" + translation(30012) + ")", urlMain+"/latest/1?ax=1", 'listSongs', "")
    addDir(translation(30002) + " (" + translation(30010) + ")", urlMain+"/latest/remix/1?ax=1", 'listSongs', "")
    addDir(translation(30002) + " (" + translation(30011) + ")", urlMain+"/latest/noremix/1?ax=1", 'listSongs', "")
    addDir(translation(30003) + " (" + translation(30012) + ")", urlMain+"/popular/1?ax=1", 'listSongs', "")
    addDir(translation(30003) + " (" + translation(30010) + ")", urlMain+"/popular/remix/1?ax=1", 'listSongs', "")
    addDir(translation(30003) + " (" + translation(30011) + ")", urlMain+"/popular/noremix/1?ax=1", 'listSongs', "")
    addDir(translation(30004), urlMain+"/popular/lastweek/1?ax=1", 'listSongs', "")
    addDir(translation(30019), "", 'listZeitgeist', "")
    addDir(translation(30005), "", 'listGenres', "")
    addDir(translation(30013), "", 'search', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def myMain():
    addDir(translation(30018), urlMain+"/"+username+"/feed/1?ax=1", 'listSongs', "")
    addDir(translation(30014), "", 'listMyArtists', "")
    addDir(translation(30007), urlMain+"/"+username+"/1?ax=1", 'listSongs', "")
    addDir(translation(30008), urlMain+"/"+username+"/history/1?ax=1", 'listSongs', "")
    addDir(translation(30009), urlMain+"/"+username+"/obsessed/1?ax=1", 'listSongs', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listSongs(url):
    content = opener.open(url).read()
    cj.save(cookieFile)
    match = re.compile('id="displayList-data">(.+?)<', re.DOTALL).findall(content)
    jsonContent = json.loads(match[0].strip())
    for track in jsonContent['tracks']:
        url = "/serve/source/"+track['id']+"/"+track['key']
        title = (track['artist'].encode('utf-8')+" - "+track['song'].encode('utf-8')).strip()
        addLink(title, url, 'playSong', track['time'], track['id'], track['artist'].encode('utf-8'))
    match = re.compile('"page_next":"(.+?)"', re.DOTALL).findall(content)
    if match:
        url = match[0].replace("\\","")
        addDir(translation(30001), urlMain+url+"?ax=1", 'listSongs', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listGenres():
    content = opener.open(urlMain).read()
    match = re.compile('<li><a href="/tags/(.+?)">(.+?)<', re.DOTALL).findall(content)
    for id, title in match:
        addDir(title, urlMain+"/tags/"+id+"/1?ax=1", 'listSongs', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def playSong(url):
    spl = url.split("/")
    id = spl[-2]
    key = spl[-1]
    content = opener.open(urlMain+url).read()
    match = re.compile('"url":"(.+?)"', re.DOTALL).findall(content)
    url = match[0].replace("\\","")
    content = opener.open(urlMain+"/serve/source/"+id+"/"+key+"?retry=1&bytesLoaded=null&duration=0&transferTime=0&prev_url="+base64.b64encode(url)).read()
    match = re.compile('"url":"(.+?)"', re.DOTALL).findall(content)
    url = match[0].replace("\\","")
    listitem = xbmcgui.ListItem(path=url+"|User-Agent="+userAgent)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
    if username and password:
        session = getSession()
        opener.open("http://hypem.com/inc/user_action.php?act=log_action&type=listen&session="+session+"&val="+id+"&playback_manual=1")


def search():
    keyboard = xbmc.Keyboard('', translation(30013))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText().replace(" ", "%20")
        listSongs(urlMain+"/search/"+search_string+"/1?ax=1&sortby=fav")


def login():
    content = opener.open(urlMain+"/1?ax=1").read()
    if "show_lightbox('account')" not in content:
        cj.save(cookieFile)
        session = getSession()
        content = opener.open("https://hypem.com/inc/user_action.php", "act=login&session="+session+"&user_screen_name="+username+"&user_password="+password).read()


def getSession():
    fh = open(cookieFile, 'r')
    cookies = fh.read()
    fh.close()
    match = re.compile('AUTH="03%3A(.+?)%', re.DOTALL).findall(cookies)
    return match[0]


def toggleLike(songID):
    session = getSession()
    opener.open("https://hypem.com/inc/user_action.php", "act=toggle_favorite&session="+session+"&type=item&val="+songID)
    xbmc.executebuiltin("Container.Refresh")


def toggleFollow(artist):
    session = getSession()
    opener.open("https://hypem.com/inc/user_action.php", "act=toggle_favorite&session="+session+"&type=query&val="+artist)
    xbmc.executebuiltin("Container.Refresh")


def listMyArtists():
    content = opener.open(urlMain+"/"+username+"/list_artists").read()
    match = re.compile('<a href="/search/(.+?)">(.+?)<', re.DOTALL).findall(content)
    for id, title in match:
        addDirR(title.title(), urlMain+"/search/"+id+"/1?ax=1", 'listSongs', "", title)
    xbmcplugin.endOfDirectory(pluginhandle)


def listZeitgeist():
    addDir("2011", urlMain+"/zeitgeist/2011/songs_list?ax=1", 'listSongs', "")
    addDir("2012", urlMain+"/zeitgeist/2012/tracks_list?ax=1", 'listSongs', "")
    xbmcplugin.endOfDirectory(pluginhandle)


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


def addLink(name, url, mode, duration, songID, artist):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultAudio.png")
    liz.setInfo(type="music", infoLabels={"title": name})
    liz.addStreamInfo('video', { 'duration': int(duration) })
    liz.setProperty('IsPlayable', 'true')
    entries = []
    if username and password:
        entries.append((translation(30015), 'RunPlugin(plugin://'+addonID+'/?mode=toggleLike&url='+urllib.quote_plus(songID)+')',))
        entries.append((translation(30016), 'RunPlugin(plugin://'+addonID+'/?mode=toggleFollow&url='+urllib.quote_plus(artist)+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="music", infoLabels={"title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addDirR(name, url, mode, iconimage, artist):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="music", infoLabels={"title": name})
    entries = []
    if username and password:
        entries.append((translation(30017), 'RunPlugin(plugin://'+addonID+'/?mode=toggleFollow&url='+urllib.quote_plus(artist)+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))

if mode == 'listSongs':
    listSongs(url)
elif mode == 'listGenres':
    listGenres()
elif mode == 'myMain':
    myMain()
elif mode == 'toggleLike':
    toggleLike(url)
elif mode == 'toggleFollow':
    toggleFollow(url)
elif mode == 'listMyArtists':
    listMyArtists()
elif mode == 'listZeitgeist':
    listZeitgeist()
elif mode == 'playSong':
    playSong(url)
elif mode == 'search':
    search()
else:
    index()
