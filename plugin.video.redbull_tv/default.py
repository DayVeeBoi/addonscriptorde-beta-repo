#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import httplib
import socket
import sys
import re
import os
import json
import time
import xbmcplugin
import xbmcgui
import xbmcaddon

addon = xbmcaddon.Addon()
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
translation = addon.getLocalizedString
forceViewMode = addon.getSetting("forceViewMode") == "true"
viewMode = str(addon.getSetting("viewMode"))
maxBitRate = addon.getSetting("maxBitRate")
maxBitRate = [512000, 1024000, 2048000, 3072000, 4096000, 5120000][int(maxBitRate)]
addonDir = xbmc.translatePath(addon.getAddonInfo('path'))
icon = os.path.join(addonDir ,'icon.png')
mainUrlLive = "http://live.redbull.tv"
mainUrl = "http://www.redbull.tv"


def index():
    addDir(translation(30005), "live", 'listEvents', "")
    addDir(translation(30006), "latest", 'listEvents', "")
    #addDir(translation(30002), mainUrl+"/videos", 'listVideos', "")
    #addDir(translation(30003), mainUrl+"/shows?page=0&per_page=100", 'listShows', "")
    #addDir(translation(30004), "", 'search', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listEvents(url):
    matchPage = ""
    if url.startswith("http://"):
        content = getUrl(url)
        matchPage = re.compile('<a href="/includes/fragments/schedule_list.php\\?pg=(.+?)" class="(.+?)">', re.DOTALL).findall(content)
        spl = content.split('<td class="status"><span class="prev">Past</span></td>')
    else:
        content = getUrl(mainUrlLive+"/includes/fragments/schedule_list.php?pg=1")
        if url == "live":
            if '<span class="live">Live</span>' in content:
                match = re.compile('<td class="description">(.+?)</td>', re.DOTALL).findall(content)
                desc = match[0]
                match = re.compile('<a href="(.+?)">(.+?)<span>(.+?)</span>', re.DOTALL).findall(content)
                url = mainUrlLive+match[0][0]
                title = match[0][1]
                subTitle = match[0][2]
                title = "NOW LIVE: "+title
                title = cleanTitle(title)
                addLink(title, url, 'playEvent', "", subTitle+"\n"+desc)
            spl = content.split('<td class="status"><span>Upcoming</span></td>')
        elif url == "latest":
            matchPage = re.compile('<a href="/includes/fragments/schedule_list.php\\?pg=(.+?)" class="(.+?)">', re.DOTALL).findall(content)
            spl = content.split('<td class="status"><span class="prev">Past</span></td>')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<span class="localtime-date-only-med">(.+?)</span>', re.DOTALL).findall(entry)
        date = match[0]
        spl2 = date.split("-")
        day = spl2[2]
        month = spl2[1]
        if len(day) == 1:
            day = "0"+day
        if len(month) == 1:
            month = "0"+month
        date = day+"."+month
        match = re.compile('<span class="localtime-time-only">(.+?)</span>', re.DOTALL).findall(entry)
        timeFrom = match[0]
        spl2 = timeFrom.split("-")
        timeFrom = spl2[3]+":"+spl2[4]
        if len(timeFrom) == 4:
            timeFrom = "0"+timeFrom
        match = re.compile('<span class="localtime-time-only tz-abbr">(.+?)</span>', re.DOTALL).findall(entry)
        timeTo = match[0]
        spl2 = timeTo.split("-")
        timeTo = spl2[3]+":"+spl2[4]
        if len(timeTo) == 4:
            timeTo = "0"+timeTo
        match = re.compile('<td class="description">(.+?)</td>', re.DOTALL).findall(entry)
        desc = match[0]
        match = re.compile('<a href="(.+?)">(.+?)<span>(.+?)</span>', re.DOTALL).findall(entry)
        url = mainUrlLive+match[0][0]
        title = match[0][1]
        subTitle = match[0][2]
        title = date+" "+timeFrom+" (GMT) - "+title
        title = cleanTitle(title)
        addLink(title, url, 'playVideo', "", date+" "+timeFrom+"-"+timeTo+" (GMT): "+subTitle+"\n"+desc)
    if matchPage:
        for pageNr, title in matchPage:
            if title == "next":
                addDir(translation(30001), mainUrlLive+"/includes/fragments/schedule_list.php?pg="+pageNr, 'listEvents', "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def latestVideos(url):
    content = getUrl(url)
    content = content[content.find('<h3>LATEST EPISODES</h3>'):]
    content = content[:content.find('</ul>')]
    spl = content.split('<li')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<span class="date">(.+?)</span>', re.DOTALL).findall(entry)
        date = match[0]
        match = re.compile('<span class="season">(.+?)</span>', re.DOTALL).findall(entry)
        subTitle = match[0]
        match = re.compile('<span class="title">(.+?)</span>', re.DOTALL).findall(entry)
        title = date+" - "+match[0]+" - "+subTitle
        title = cleanTitle(title)
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = mainUrl+match[0]
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = mainUrl+match[0].replace(" ", "%20")
        addLink(title, url, 'playVideo', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listShows(url):
    urlMain = url
    content = getUrl(url)
    spl = content.split("class='grid__unit")
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
        title = match[0].strip()
        title = cleanTitle(title)
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = mainUrl+match[0]
        match = re.compile('data-srcset="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0]
        addDir(title, url, 'listVideos', thumb)
    start = urlMain.split("=")[-1]
    match = re.compile('class="next" onclick="javascript:loadShows\\(\'name\', (.+?)\\)', re.DOTALL).findall(content)
    if match:
        addDir(translation(30001), urlMain.replace("start="+start, "start="+match[0]), 'listShows', "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listVideos(url):
    content = getUrl(url)
    spl = content.split("class='grid__unit")
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = mainUrl+match[0]
        match = re.compile('data-srcset="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0]
        if "/episodes/" in url:
            match = re.compile("class='h3 teaser__title.+?'>(.+?)<", re.DOTALL).findall(entry)
            title = match[0]
            match = re.compile("class='h4 teaser__subtitle'>(.+?)<", re.DOTALL).findall(entry)
            title = match[0]+": "+title
            addLink(title, url, 'playVideo', thumb, "", "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def search():
    keyboard = xbmc.Keyboard('', translation(30004))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText().replace(" ", "+")
        content = getUrl(mainUrl+'/cs/Satellite?_=1341632208902&pagename=RBWebTV%2FRBWTVSearchResult&q='+search_string)
        if "<!-- Episodes -->" in content:
            content = content[content.find('<!-- Episodes -->'):]
            spl = content.split('<div class="results-item">')
            for i in range(1, len(spl), 1):
                entry = spl[i]
                match = re.compile('<span style="font-weight: bold;">(.+?)</span><br/>', re.DOTALL).findall(entry)
                title = match[0]
                title = cleanTitle(title)
                match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
                url = mainUrl+match[0]
                addLink(title, url, 'playVideo', "")
        xbmcplugin.endOfDirectory(pluginhandle)


def playVideo(url):
    content = getUrl(url)
    match1 = re.compile("data-counter-target='(.+?)'", re.DOTALL).findall(content)
    match2 = re.compile("data-id='(.+?)'", re.DOTALL).findall(content)
    if match1:
        xbmc.executebuiltin('XBMC.Notification(Info:,Not available yet...,5000,'+icon+')')
    elif match2:
        content = getUrl("https://api.redbull.tv/v1/videos/"+match2[0])
        content = json.loads(content)
        listItem = xbmcgui.ListItem(path=content["videos"]["live"]["uri"])
        xbmcplugin.setResolvedUrl(pluginhandle, True, listItem)
    else:
        xbmc.executebuiltin('XBMC.Notification(Info:,'+str(translation(30104))+'!,5000,'+icon+')')


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#39;", "'").replace("&#039;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
    title = title.strip()
    return title


def getUrl(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:22.0) Gecko/20100101 Firefox/22.0')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link


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

if mode == 'listVideos':
    listVideos(url)
elif mode == 'latestVideos':
    latestVideos(url)
elif mode == 'listShows':
    listShows(url)
elif mode == 'listEvents':
    listEvents(url)
elif mode == 'playEvent':
    playEvent(url)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'search':
    search()
else:
    index()
