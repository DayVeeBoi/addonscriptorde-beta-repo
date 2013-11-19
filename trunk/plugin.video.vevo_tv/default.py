#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import sys
import json
import random
import urllib
import urllib2
import xbmcplugin
import xbmcgui
import xbmcaddon

addon = xbmcaddon.Addon()
pluginhandle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
xbox = xbmc.getCondVisibility("System.Platform.xbox")
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
bitrateOfficial = addon.getSetting("bitrateOfficial")
bitrateOfficial = ["512000", "800000", "1392000", "2272000", "3500000"][int(bitrateOfficial)]
bitrateCustom = addon.getSetting("bitrateCustom")
bitrateCustom = ["564000", "864000", "1328000", "1728000", "2528000", "3328000", "4392000", "5392000"][int(bitrateCustom)]
urlMainApi = "http://api.vevo.com/mobile/v1"
urlMain = "http://www.vevo.com"


def index():
    addLink("VEVO TV (US #1)", "TIVEVSTRUS00", 'playOfficial', "")
    addLink("VEVO TV (US #2)", "TIVEVSTRUS01", 'playOfficial', "")
    addLink("VEVO TV (US #3)", "TIVEVSTRUS02", 'playOfficial', "")
    addLink("VEVO TV (DE)", "TIVEVSTRDE00", 'playOfficial', "")
    addDir(translation(30001), "default", 'customMain', "")
    addDir(translation(30004), "live", 'customMain', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def customMain(type):
    currentMode = 'listCustomModes'
    if type=="live":
        currentMode = 'listCustomModesLive'
    content = getUrl(urlMain)
    if "var $data" in content:
        addDir("- All Genres", "all", currentMode, "")
        content = getUrl(urlMainApi+"/genre/list.json?culture=en_US")
        content = json.loads(content)
        for item in content["result"]:
            addDir(item["Value"], item["Key"], currentMode, "")
        xbmcplugin.endOfDirectory(pluginhandle)
    else:
        xbmc.executebuiltin('XBMC.Notification(Info:,'+translation(30002)+',5000)')


def listCustomModes(id):
    genres = ""
    if id!="all":
        genres = "genres="+id+"&"
    addDir("Top100", urlMainApi+"/video/list.json?"+genres+"order=MostViewedThisWeek&offset=0&max=100", 'playCustom', "", "100", "false")
    addDir("Top10 (Shuffled)", urlMainApi+"/video/list.json?"+genres+"order=MostViewedThisWeek&offset=0&max=100", 'playCustom', "", "10", "true")
    addDir("Top20 (Shuffled)", urlMainApi+"/video/list.json?"+genres+"order=MostViewedThisWeek&offset=0&max=100", 'playCustom', "", "20", "true")
    addDir("Top50 (Shuffled)", urlMainApi+"/video/list.json?"+genres+"order=MostViewedThisWeek&offset=0&max=100", 'playCustom', "", "50", "true")
    addDir("Top100 (Shuffled)", urlMainApi+"/video/list.json?"+genres+"order=MostViewedThisWeek&offset=0&max=100", 'playCustom', "", "100", "true")
    addDir("Top100 AllTime", urlMainApi+"/video/list.json?"+genres+"order=MostViewedAllTime&offset=0&max=100", 'playCustom', "", "100", "false")
    addDir("Top10 AllTime (Shuffled)", urlMainApi+"/video/list.json?"+genres+"order=MostViewedAllTime&offset=0&max=100", 'playCustom', "", "10", "true")
    addDir("Top20 AllTime (Shuffled)", urlMainApi+"/video/list.json?"+genres+"order=MostViewedAllTime&offset=0&max=100", 'playCustom', "", "20", "true")
    addDir("Top50 AllTime (Shuffled)", urlMainApi+"/video/list.json?"+genres+"order=MostViewedAllTime&offset=0&max=100", 'playCustom', "", "50", "true")
    addDir("Top100 AllTime (Shuffled)", urlMainApi+"/video/list.json?"+genres+"order=MostViewedAllTime&offset=0&max=100", 'playCustom', "", "100", "true")
    addDir("All (Shuffled)", urlMainApi+"/video/list.json?"+genres+"order=Random&offset=0&max=100", 'playCustom', "", "100", "false")
    xbmcplugin.endOfDirectory(pluginhandle)


def listCustomModesLive(id):
    genres = ""
    if id!="all":
        genres = "genres="+id+"&"
    addDir("Top100", urlMainApi+"/video/list.json?"+genres+"order=MostViewedThisWeek&offset=0&max=100&max=100&islive=true", 'playCustom', "", "100", "false")
    addDir("Top10 (Shuffled)", urlMainApi+"/video/list.json?"+genres+"order=MostViewedThisWeek&offset=0&max=100&islive=true", 'playCustom', "", "10", "true")
    addDir("Top20 (Shuffled)", urlMainApi+"/video/list.json?"+genres+"order=MostViewedThisWeek&offset=0&max=100&islive=true", 'playCustom', "", "20", "true")
    addDir("Top50 (Shuffled)", urlMainApi+"/video/list.json?"+genres+"order=MostViewedThisWeek&offset=0&max=100&islive=true", 'playCustom', "", "50", "true")
    addDir("Top100 (Shuffled)", urlMainApi+"/video/list.json?"+genres+"order=MostViewedThisWeek&offset=0&max=100&islive=true", 'playCustom', "", "100", "true")
    addDir("Top100 AllTime", urlMainApi+"/video/list.json?"+genres+"order=MostViewedAllTime&offset=0&max=100&islive=true", 'playCustom', "", "100", "false")
    addDir("Top10 AllTime (Shuffled)", urlMainApi+"/video/list.json?"+genres+"order=MostViewedAllTime&offset=0&max=100&islive=true", 'playCustom', "", "10", "true")
    addDir("Top20 AllTime (Shuffled)", urlMainApi+"/video/list.json?"+genres+"order=MostViewedAllTime&offset=0&max=100&islive=true", 'playCustom', "", "20", "true")
    addDir("Top50 AllTime (Shuffled)", urlMainApi+"/video/list.json?"+genres+"order=MostViewedAllTime&offset=0&max=100&islive=true", 'playCustom', "", "50", "true")
    addDir("Top100 AllTime (Shuffled)", urlMainApi+"/video/list.json?"+genres+"order=MostViewedAllTime&offset=0&max=100&islive=true", 'playCustom', "", "100", "true")
    addDir("All (Shuffled)", urlMainApi+"/video/list.json?"+genres+"order=Random&offset=0&max=100&islive=true", 'playCustom', "", "100", "false")
    xbmcplugin.endOfDirectory(pluginhandle)


def playOfficial(id):
    content = getUrl(urlMain)
    if "noVTV: false" in content:
        content = getUrl("http://smil.lvl3.vevo.com/v3/smil/"+id+"/"+id+"r.smil")
        matchBase=re.compile('<meta base="(.+?)" />', re.DOTALL).findall(content)
        matchPlaypath=re.compile('<video src="(.+?)" system-bitrate="(.+?)" />', re.DOTALL).findall(content)
        for url, bitrate in matchPlaypath:
            if int(bitrate)<=int(bitrateOfficial):
                fullUrl = matchBase[0]+" playpath="+url+" live=true"
        listitem = xbmcgui.ListItem(path=fullUrl)
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
    else:
        xbmc.executebuiltin('XBMC.Notification(Info:,'+translation(30003)+',5000)')


def playCustom(url, count, shuffled):
    entries = []
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    content = getUrl(url)
    content = json.loads(content)
    counter = 0
    for item in content["result"]:
        title = item["artists_main"][0]["name"]+" - "+item["title"]
        thumb = item["image_url"]
        if xbox==True:
            url="plugin://video/VEVO TV/?url="+item["isrc"]+"&mode=playVideo"
        else:
            url="plugin://plugin.video.vevo_tv/?url="+item["isrc"]+"&mode=playVideo"
        entries.append([title, url, thumb])
        counter += 1
        if counter==count:
            break
    if shuffled:
        random.shuffle(entries)
    for title, url, thumb in entries:
        listitem = xbmcgui.ListItem(title, thumbnailImage=thumb)
        playlist.add(url, listitem)
    xbmc.Player().play(playlist)


def playVideo(id):
    try:
        content = getUrl("http://vevoodfs.fplive.net/Video/V2/VFILE/"+id+"/"+id.lower()+"r.smil")
        matchBase=re.compile('<meta base="(.+?)" />', re.DOTALL).findall(content)
        matchPlaypath=re.compile('<video src="(.+?)" system-bitrate="(.+?)" />', re.DOTALL).findall(content)
        for url, bitrate in matchPlaypath:
            if int(bitrate)<=int(bitrateCustom):
                fullUrl = matchBase[0]+" playpath="+url
        listitem = xbmcgui.ListItem(path=fullUrl)
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
    except:
        pass


def getUrl(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    return link


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


def addLink(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage, count=100, shuffled="false"):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&count="+str(count)+"&shuffled="+str(shuffled)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
count = urllib.unquote_plus(params.get('count', ''))
shuffled = urllib.unquote_plus(params.get('shuffled', ''))

if mode == 'playVideo':
    playVideo(url)
elif mode == 'playOfficial':
    playOfficial(url)
elif mode == 'playCustom':
    playCustom(url, int(count), shuffled=="true")
elif mode == 'customMain':
    customMain(url)
elif mode == 'listCustomModes':
    listCustomModes(url)
elif mode == 'listCustomModesLive':
    listCustomModesLive(url)
else:
    index()
