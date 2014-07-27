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
import json
import time

addon = xbmcaddon.Addon()
pluginhandle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
xbox = xbmc.getCondVisibility("System.Platform.xbox")
userDataFolder=xbmc.translatePath("special://profile/addon_data/"+addonID)
cacheDir = os.path.join(userDataFolder, "cache")
socket.setdefaulttimeout(30)
opener = urllib2.build_opener()
userAgent = "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0"
opener.addheaders = [('User-Agent', userAgent)]
urlMain = "http://www.billboard.com"

if not os.path.isdir(userDataFolder):
  os.mkdir(userDataFolder)
if not os.path.isdir(cacheDir):
  os.mkdir(cacheDir)


def index():
    addDir(translation(30005), urlMain+"/rss/charts/hot-100", "listCharts")
    addDir("Trending 140", "Top 140 in Trending", "listChartsNew")
    addDir("Last 24 Hours", "Top 140 in Overall", "listChartsNew")
    addDir(translation(30006), "genre", "listChartsTypes")
    addDir(translation(30007), "country", "listChartsTypes")
    addDir(translation(30008), "other", "listChartsTypes")
    xbmcplugin.endOfDirectory(pluginhandle)


def listChartsTypes(type):
    if type=="genre":
        addDir(translation(30009), urlMain+"/rss/charts/pop-songs", "listCharts")
        addDir(translation(30010), urlMain+"/rss/charts/rock-songs", "listCharts")
        addDir(translation(30011), urlMain+"/rss/charts/alternative-songs", "listCharts")
        addDir(translation(30012), urlMain+"/rss/charts/r-b-hip-hop-songs", "listCharts")
        addDir(translation(30013), urlMain+"/rss/charts/r-and-b-songs", "listCharts")
        addDir(translation(30014), urlMain+"/rss/charts/rap-songs", "listCharts")
        addDir(translation(30015), urlMain+"/rss/charts/country-songs", "listCharts")
        addDir(translation(30016), urlMain+"/rss/charts/latin-songs", "listCharts")
        addDir(translation(30017), urlMain+"/rss/charts/jazz-songs", "listCharts")
        addDir(translation(30018), urlMain+"/rss/charts/dance-club-play-songs", "listCharts")
        addDir(translation(30019), urlMain+"/rss/charts/dance-electronic-songs", "listCharts")
        addDir(translation(30020), urlMain+"/rss/charts/heatseekers-songs", "listCharts")
    elif type=="country":
        addDir(translation(30021), urlMain+"/rss/charts/canadian-hot-100", "listCharts")
        addDir(translation(30022), urlMain+"/rss/charts/k-pop-hot-100", "listCharts")
        addDir(translation(30023), urlMain+"/rss/charts/japan-hot-100", "listCharts")
        addDir(translation(30024), urlMain+"/rss/charts/germany-songs", "listCharts")
        addDir(translation(30025), urlMain+"/rss/charts/france-songs", "listCharts")
        addDir(translation(30026), urlMain+"/rss/charts/united-kingdom-songs", "listCharts")
    elif type=="other":
        addDir(translation(30028), urlMain+"/rss/charts/radio-songs", "listCharts")
        addDir(translation(30029), urlMain+"/rss/charts/digital-songs", "listCharts")
        addDir(translation(30030), urlMain+"/rss/charts/streaming-songs", "listCharts")
        addDir(translation(30031), urlMain+"/rss/charts/on-demand-songs", "listCharts")
    xbmcplugin.endOfDirectory(pluginhandle)


def listCharts(url):
    xbmcplugin.setContent(pluginhandle, "episodes")
    addDir("[B]- "+translation(30001)+"[/B]", url, "autoPlay", "all")
    addDir("[B]- "+translation(30002)+"[/B]", url, "autoPlay", "random")
    content = opener.open(url).read()
    match = re.compile('<item>.+?<artist>(.+?)</artist>.+?<chart_item_title>(.+?)</chart_item_title>', re.DOTALL).findall(content)
    for artist, title in match:
        title = cleanTitle(artist+" - "+title[title.find(":")+1:]).replace("Featuring", "Feat.")
        addLink(title, title, "playVideo", "", "", "", title)
    xbmcplugin.endOfDirectory(pluginhandle)


def listChartsNew(url):
    xbmcplugin.setContent(pluginhandle, "episodes")
    addDir("[B]- "+translation(30001)+"[/B]", url, "autoPlayNew", "all")
    addDir("[B]- "+translation(30002)+"[/B]", url, "autoPlayNew", "random")
    content = opener.open("http://realtime.billboard.com/").read()
    content = content[content.find("<h1>"+url+"</h1>"):]
    content = content[:content.find("</table>")]
    match = re.compile('<tr>.*?<td>(.+?)</td>.*?<td><a href=".*?">(.+?)</a></td>.*?<td>(.+?)</td>.*?<td>(.+?)</td>.*?</tr>', re.DOTALL).findall(content)
    for nr, artist, title, rating in match:
        if "(" in title:
            title = title[:title.find("(")].strip()
        title = cleanTitle(artist+" - "+title).replace("Featuring", "Feat.")
        addLink(title, title, "playVideo", "", "", "", title)
    xbmcplugin.endOfDirectory(pluginhandle)


def cache(title):
    cacheFile = os.path.join(cacheDir, (''.join(c for c in unicode(title, 'utf-8') if c not in '/\\:?"*|<>')).strip())
    if os.path.exists(cacheFile) and (time.time()-os.path.getmtime(cacheFile) < 60*60*24):
        fh = open(cacheFile, 'r')
        content = fh.read()
        fh.close()
    else:
        content = getYoutubeId(title)
        fh = open(cacheFile, 'w')
        fh.write(content)
        fh.close()
    return content


def playVideo(title):
    listitem = xbmcgui.ListItem(path=getYoutubePluginUrl(cache(title)))
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def getYoutubeId(title):
    url = "http://gdata.youtube.com/feeds/api/videos?vq="+urllib.quote_plus(title)+"&max-results=1&start-index=1&orderby=relevance&time=all_time&v=2"
    content = opener.open(url).read()
    match=re.compile('<yt:videoid>(.+?)</yt:videoid>', re.DOTALL).findall(content)
    return match[0]


def getYoutubePluginUrl(id):
    if xbox:
        return "plugin://video/YouTube/?path=/root/video&action=play_video&videoid=" + id
    else:
        return "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=" + id


def queueVideo(url, name):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name)
    playlist.add(url, listitem)


def autoPlay(url, type):
    entries = []
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    content = opener.open(url).read()
    match = re.compile('<item>.+?<artist>(.+?)</artist>.+?<chart_item_title>(.+?)</chart_item_title>', re.DOTALL).findall(content)
    for artist, title in match:
        title = cleanTitle(artist+" - "+title[title.find(":")+1:]).replace("Featuring", "Feat.")
        url = sys.argv[0]+"?url="+urllib.quote_plus(title)+"&mode=playVideo&name="+str(title)+"&chartTitle="+str(title)
        if type in ["all", "random"]:
            listitem = xbmcgui.ListItem(title)
            entries.append([title, url])
    if type=="random":
        random.shuffle(entries)
    for title, url in entries:
        listitem = xbmcgui.ListItem(title)
        playlist.add(url, listitem)
    xbmc.Player().play(playlist)


def autoPlayNew(url, type):
    entries = []
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    content = opener.open("http://realtime.billboard.com/").read()
    content = content[content.find("<h1>"+url+"</h1>"):]
    content = content[:content.find("</table>")]
    match = re.compile('<tr>.*?<td>(.+?)</td>.*?<td><a href=".*?">(.+?)</a></td>.*?<td>(.+?)</td>.*?<td>(.+?)</td>.*?</tr>', re.DOTALL).findall(content)
    for nr, artist, title, rating in match:
        if "(" in title:
            title = title[:title.find("(")].strip()
        title = cleanTitle(artist+" - "+title).replace("Featuring", "Feat.")
        url = sys.argv[0]+"?url="+urllib.quote_plus(title)+"&mode=playVideo&name="+str(title)+"&chartTitle="+str(title)
        if type in ["all", "random"]:
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
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#39;", "'").replace("&#039;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
    title = title.strip()
    return title


def addLink(name, url, mode, iconimage, desc="", length="", chartTitle=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+str(name)+"&chartTitle="+str(chartTitle)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Duration": length})
    liz.setProperty('IsPlayable', 'true')
    entries = []
    entries.append((translation(30004), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+urllib.quote_plus(name)+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, type=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&type="+str(type)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultMusicVideos.png")
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

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
type = urllib.unquote_plus(params.get('type', ''))
chartTitle = urllib.unquote_plus(params.get('chartTitle', ''))

if mode == 'listCharts':
    listCharts(url)
elif mode == 'listChartsNew':
    listChartsNew(url)
elif mode == 'listChartsTypes':
    listChartsTypes(url)
elif mode == 'listVideos':
    listVideos(url)
elif mode == 'cache':
    cache(url)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'queueVideo':
    queueVideo(url, name)
elif mode == 'autoPlay':
    autoPlay(url, type)
elif mode == 'autoPlayNew':
    autoPlayNew(url, type)
else:
    index()
