#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import sys
import re
import os
import sqlite3
import random
import datetime
import xbmcplugin
import xbmcgui
import xbmcaddon


addon = xbmcaddon.Addon()
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
xbox = xbmc.getCondVisibility("System.Platform.xbox")
translation = addon.getLocalizedString

opener = urllib2.build_opener()
userAgent = "XBMC | "+addonID+" | "+addon.getAddonInfo('version')
opener.addheaders = [('User-Agent', userAgent)]
urlMain = "http://www.reddit.com"

cat_new = addon.getSetting("cat_new") == "true"
cat_hot_h = addon.getSetting("cat_hot_h") == "true"
cat_hot_d = addon.getSetting("cat_hot_d") == "true"
cat_hot_w = addon.getSetting("cat_hot_w") == "true"
cat_hot_m = addon.getSetting("cat_hot_m") == "true"
cat_top_d = addon.getSetting("cat_top_d") == "true"
cat_top_w = addon.getSetting("cat_top_w") == "true"
cat_hot_m = addon.getSetting("cat_hot_m") == "true"
cat_hot_y = addon.getSetting("cat_hot_y") == "true"
cat_hot_a = addon.getSetting("cat_hot_a") == "true"

filter = addon.getSetting("filter") == "true"
filterRating = int(addon.getSetting("filterRating"))
filterThreshold = int(addon.getSetting("filterThreshold"))

showAll = addon.getSetting("showAll") == "true"
showUnwatched = addon.getSetting("showUnwatched") == "true"
showUnfinished = addon.getSetting("showUnfinished") == "true"

forceViewMode = addon.getSetting("forceViewMode") == "true"
viewMode = str(addon.getSetting("viewMode"))

searchSort = int(addon.getSetting("searchSort"))
searchSort = ["ask", "relevance", "new", "hot", "top", "comments"][searchSort]
searchTime = int(addon.getSetting("searchTime"))
searchTime = ["ask", "hour", "day", "week", "month", "year", "all"][searchTime]

addonUserDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
subredditsFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/subreddits")
if not os.path.isdir(addonUserDataFolder):
    os.mkdir(addonUserDataFolder)

allHosterQuery = urllib.quote_plus("site:youtu.be OR site:youtube.com OR site:vimeo.com OR site:liveleak.com OR site:dailymotion.com")


def getDbPath():
    path = xbmc.translatePath("special://userdata/Database")
    files = os.listdir(path)
    latest = ""
    for file in files:
        if file[:8] == 'MyVideos' and file[-3:] == '.db':
            if file > latest:
                latest = file
    return os.path.join(path, latest)


def getPlayCount(url):
    c.execute('SELECT playCount FROM files WHERE strFilename=?', [url])
    result = c.fetchone()
    if result:
        result = result[0]
        if result:
            return int(result)
        return 0
    return -1


def addSubreddit():
    keyboard = xbmc.Keyboard('', translation(30001))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        subreddit = keyboard.getText()
        fh = open(subredditsFile, 'a')
        fh.write(subreddit+'\n')
        fh.close()


def removeSubreddit(subreddit):
    fh = open(subredditsFile, 'r')
    content = fh.read()
    fh.close()
    fh = open(subredditsFile, 'w')
    fh.write(content.replace(subreddit+'\n', ''))
    fh.close()
    xbmc.executebuiltin("Container.Refresh")


def index():
    content = ""
    if os.path.exists(subredditsFile):
        fh = open(subredditsFile, 'r')
        content = fh.read()
        fh.close()
    if "all\n" not in content:
        fh = open(subredditsFile, 'a')
        fh.write('all\n')
        fh.close()
    entries = []
    if os.path.exists(subredditsFile):
        fh = open(subredditsFile, 'r')
        content = fh.read()
        fh.close()
        spl = content.split('\n')
        for i in range(0, len(spl), 1):
            if spl[i]:
                subreddit = spl[i].strip()
                entries.append(subreddit.title())
    entries.sort()
    for entry in entries:
        if entry == "all":
            addDir(entry, entry.lower(), 'listSorting', "")
        else:
            addDirR(entry, entry.lower(), 'listSorting', "")
    addDir("[ Vimeo.com ]", "all", 'listSorting', "", "site:vimeo.com")
    addDir("[ Youtube.com ]", "all", 'listSorting', "", "site:youtu.be+OR+site:youtube.com")
    addDir("[ Liveleak.com ]", "all", 'listSorting', "", "site:liveleak.com")
    addDir("[ Dailymotion.com ]", "all", 'listSorting', "", "site:dailymotion.com")
    addDir("[B]- "+translation(30001)+"[/B]", "", 'addSubreddit', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listSorting(subreddit, hosterQuery):
    hosterQuery = urllib.quote_plus(hosterQuery)
    if not hosterQuery:
        hosterQuery = allHosterQuery
    if cat_new:
        addDir(translation(30003), urlMain+"/r/"+subreddit+"/search.json?q="+hosterQuery+"&sort=new&restrict_sr=on&limit=100", 'listVideos', "")
    if cat_hot_h:
        addDir(translation(30002)+": "+translation(30006), urlMain+"/r/"+subreddit+"/search.json?q="+hosterQuery+"&sort=hot&restrict_sr=on&limit=100&t=hour", 'listVideos', "")
    if cat_hot_d:
        addDir(translation(30002)+": "+translation(30007), urlMain+"/r/"+subreddit+"/search.json?q="+hosterQuery+"&sort=hot&restrict_sr=on&limit=100&t=day", 'listVideos', "")
    if cat_hot_w:
        addDir(translation(30002)+": "+translation(30008), urlMain+"/r/"+subreddit+"/search.json?q="+hosterQuery+"&sort=hot&restrict_sr=on&limit=100&t=week", 'listVideos', "")
    if cat_hot_m:
        addDir(translation(30002)+": "+translation(30009), urlMain+"/r/"+subreddit+"/search.json?q="+hosterQuery+"&sort=hot&restrict_sr=on&limit=100&t=month", 'listVideos', "")
    if cat_top_d:
        addDir(translation(30004)+": "+translation(30007), urlMain+"/r/"+subreddit+"/search.json?q="+hosterQuery+"&sort=top&restrict_sr=on&limit=100&t=day", 'listVideos', "")
    if cat_top_w:
        addDir(translation(30004)+": "+translation(30008), urlMain+"/r/"+subreddit+"/search.json?q="+hosterQuery+"&sort=top&restrict_sr=on&limit=100&t=week", 'listVideos', "")
    if cat_hot_m:
        addDir(translation(30004)+": "+translation(30009), urlMain+"/r/"+subreddit+"/search.json?q="+hosterQuery+"&sort=top&restrict_sr=on&limit=100&t=month", 'listVideos', "")
    if cat_hot_y:
        addDir(translation(30004)+": "+translation(30010), urlMain+"/r/"+subreddit+"/search.json?q="+hosterQuery+"&sort=top&restrict_sr=on&limit=100&t=year", 'listVideos', "")
    if cat_hot_a:
        addDir(translation(30004)+": "+translation(30011), urlMain+"/r/"+subreddit+"/search.json?q="+hosterQuery+"&sort=top&restrict_sr=on&limit=100&t=all", 'listVideos', "")
    addDir("[B]- "+translation(30017)+"[/B]", subreddit, "search", "", hosterQuery)
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideos(url):
    currentUrl = url
    xbmcplugin.setContent(pluginhandle, "episodes")
    if showAll:
        addDir("[B]- "+translation(30012)+"[/B]", url, 'playRandomly', "", "ALL")
    if showUnwatched:
        addDir("[B]- "+translation(30014)+"[/B]", url, 'playRandomly', "", "UNWATCHED")
    if showUnfinished:
        addDir("[B]- "+translation(30015)+"[/B]", url, 'playRandomly', "", "UNFINISHED")
    content = opener.open(url).read()
    spl = content.split('"content"')
    for i in range(1, len(spl), 1):
        entry = spl[i].replace('\\"', '\'')
        try:
            match = re.compile('"title": "(.+?)"', re.DOTALL).findall(entry)
            title = cleanTitle(match[0])
            match = re.compile('"description": "(.+?)"', re.DOTALL).findall(entry)
            description = cleanTitle(match[0])
            match = re.compile('"created_utc": (.+?),', re.DOTALL).findall(entry)
            date = match[0].split(".")[0]
            dateTime = str(datetime.datetime.fromtimestamp(int(date)).strftime('%Y-%m-%d %H:%M'))
            date = dateTime.split(" ")[0]
            match = re.compile('"ups": (.+?),', re.DOTALL).findall(entry)
            ups = int(match[0].replace("}", ""))
            match = re.compile('"downs": (.+?),', re.DOTALL).findall(entry)
            downs = int(match[0].replace("}", ""))
            rating = int(ups*100/(ups+downs))
            if filter and (ups+downs) > filterThreshold and rating < filterRating:
                continue
            match = re.compile('"num_comments": (.+?),', re.DOTALL).findall(entry)
            comments = match[0]
            description = dateTime+"  |  "+str(ups+downs)+" votes: "+str(rating)+"% Up  |  "+comments+" comments\n"+description
            match = re.compile('"thumbnail_url": "(.+?)"', re.DOTALL).findall(entry)
            thumb = match[0]
            matchYoutube = re.compile('"url": "http://www.youtube.com/watch\\?v=(.+?)"', re.DOTALL).findall(entry)
            matchVimeo = re.compile('"url": "http://vimeo.com/(.+?)"', re.DOTALL).findall(entry)
            matchDailyMotion = re.compile('"url": "http://www.dailymotion.com/video/(.+?)_', re.DOTALL).findall(entry)
            matchLiveLeak = re.compile('"url": "http://www.liveleak.com/view\\?i=(.+?)"', re.DOTALL).findall(entry)
            url = ""
            if matchYoutube:
                url = getYoutubeUrl(matchYoutube[0])
            elif matchVimeo:
                url = getVimeoUrl(matchVimeo[0].replace("#", ""))
            elif matchDailyMotion:
                url = getDailyMotionUrl(matchDailyMotion[0])
            elif matchLiveLeak:
                url = getLiveLeakUrl(matchLiveLeak[0])
            if url:
                addLink(title, url, 'playVideo', thumb, description, date)
        except:
            pass
    match = re.compile('"after": "(.+?)"', re.DOTALL).findall(content)
    if match:
        after = match[0]
        if "&after=" in currentUrl:
            nextUrl = currentUrl[:currentUrl.find("&after=")]+"&after="+after
        else:
            nextUrl = currentUrl+"&after="+after
        addDir(translation(30016), nextUrl, 'listVideos', "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def playRandomly(url, type):
    entries = []
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    content = opener.open(url).read()
    spl = content.split('"content"')
    for i in range(1, len(spl), 1):
        entry = spl[i].replace('\\"', '\'')
        try:
            match = re.compile('"title": "(.+?)"', re.DOTALL).findall(entry)
            title = cleanTitle(match[0])
            match = re.compile('"ups": (.+?),', re.DOTALL).findall(entry)
            ups = int(match[0].replace("}", ""))
            match = re.compile('"downs": (.+?),', re.DOTALL).findall(entry)
            downs = int(match[0].replace("}", ""))
            rating = int(ups*100/(ups+downs))
            if filter and (ups+downs) > filterThreshold and rating < filterRating:
                continue
            matchYoutube = re.compile('"url": "http://www.youtube.com/watch\\?v=(.+?)"', re.DOTALL).findall(entry)
            matchVimeo = re.compile('"url": "http://vimeo.com/(.+?)"', re.DOTALL).findall(entry)
            matchDailyMotion = re.compile('"url": "http://www.dailymotion.com/video/(.+?)_', re.DOTALL).findall(entry)
            matchLiveLeak = re.compile('"url": "http://www.liveleak.com/view\\?i=(.+?)"', re.DOTALL).findall(entry)
            url = ""
            if matchYoutube:
                url = getYoutubeUrl(matchYoutube[0])
            elif matchVimeo:
                url = getVimeoUrl(matchVimeo[0].replace("#", ""))
            elif matchDailyMotion:
                url = getDailyMotionUrl(matchDailyMotion[0])
            elif matchLiveLeak:
                url = getLiveLeakUrl(matchLiveLeak[0])
            if url:
                url = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode=playVideo"
                if type == "ALL":
                    listitem = xbmcgui.ListItem(title)
                    entries.append([title, url])
                elif type == "UNWATCHED" and getPlayCount(url) < 0:
                    listitem = xbmcgui.ListItem(title)
                    entries.append([title, url])
                elif type == "UNFINISHED" and getPlayCount(url) == 0:
                    listitem = xbmcgui.ListItem(title)
                    entries.append([title, url])
        except:
            pass
    random.shuffle(entries)
    for title, url in entries:
        listitem = xbmcgui.ListItem(title)
        playlist.add(url, listitem)
    xbmc.Player().play(playlist)


def getYoutubeUrl(id):
    if xbox:
        url = "plugin://video/YouTube/?path=/root/video&action=play_video&videoid=" + id
    else:
        url = "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=" + id
    return url


def getVimeoUrl(id):
    if xbox:
        url = "plugin://video/Vimeo/?path=/root/video&action=play_video&videoid=" + id
    else:
        url = "plugin://plugin.video.vimeo/?path=/root/video&action=play_video&videoid=" + id
    return url


def getDailyMotionUrl(id):
    if xbox:
        url = "plugin://video/DailyMotion.com/?url=" + id + "&mode=playVideo"
    else:
        url = "plugin://plugin.video.dailymotion_com/?url=" + id + "&mode=playVideo"
    return url


def getLiveLeakUrl(id):
    if xbox:
        url = "plugin://video/Reddit.com/?url=" + id + "&mode=playLiveLeakVideo"
    else:
        url = "plugin://plugin.video.reddit_tv/?url=" + id + "&mode=playLiveLeakVideo"
    return url


def playVideo(url):
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def playLiveLeakVideo(id):
    content = opener.open("http://www.liveleak.com/view?i="+id).read()
    matchHD = re.compile('hd_file_url=(.+?)&', re.DOTALL).findall(content)
    matchSD = re.compile('file: "(.+?)"', re.DOTALL).findall(content)
    if matchHD:
        url = urllib.unquote_plus(matchHD[0])
    elif matchSD:
        url = matchSD[0]
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def queueVideo(url, name):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name)
    playlist.add(url, listitem)


def search(subreddit, hosterQuery):
    hosterQuery = urllib.quote_plus(hosterQuery)
    if not hosterQuery:
        hosterQuery = allHosterQuery
    keyboard = xbmc.Keyboard('', translation(30017))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText().replace(" ", "+")
        if searchSort == "ask":
            searchAskOne(urlMain+"/r/"+subreddit+"/search.json?q="+hosterQuery+"%20"+search_string+"&restrict_sr=on&limit=100&sort=")
        else:
            if searchTime == "ask":
                searchAskTwo(urlMain+"/r/"+subreddit+"/search.json?q="+hosterQuery+"%20"+search_string+"&restrict_sr=on&limit=100&sort="+searchSort+"&t=")
            else:
                listVideos(urlMain+"/r/"+subreddit+"/search.json?q="+hosterQuery+"%20"+search_string+"&restrict_sr=on&limit=100&sort="+searchSort+"&t="+searchTime)


def searchAskOne(url):
    addDir(translation(30114), url+"relevance", 'searchAskTwo', "")
    addDir(translation(30115), url+"new", 'searchAskTwo', "")
    addDir(translation(30116), url+"hot", 'searchAskTwo', "")
    addDir(translation(30117), url+"top", 'searchAskTwo', "")
    addDir(translation(30118), url+"comments", 'searchAskTwo', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def searchAskTwo(url):
    if searchTime == "ask":
        addDir(translation(30119), url+"&t=hour", 'listVideos', "")
        addDir(translation(30120), url+"&t=day", 'listVideos', "")
        addDir(translation(30121), url+"&t=week", 'listVideos', "")
        addDir(translation(30122), url+"&t=month", 'listVideos', "")
        addDir(translation(30123), url+"&t=year", 'listVideos', "")
        addDir(translation(30124), url+"&t=all", 'listVideos', "")
        xbmcplugin.endOfDirectory(pluginhandle)
    else:
        listVideos(url+"&t="+searchTime)


def cleanTitle(title):
        title = title.replace("&lt;","<").replace("&gt;",">").replace("&amp;","&").replace("&#039;","'").replace("&quot;","\"")
        title = title.replace("\u2014", "—")
        return title.strip()


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addLink(name, url, mode, iconimage, description, date):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": description, "Aired": date})
    liz.setProperty('IsPlayable', 'true')
    liz.addContextMenuItems([(translation(30018), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+urllib.quote_plus(name)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage, type=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&type="+str(type)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addDirR(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.addContextMenuItems([(translation(30013), 'RunPlugin(plugin://'+addonID+'/?mode=removeSubreddit&url='+urllib.quote_plus(url)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


dbPath = getDbPath()
conn = sqlite3.connect(dbPath)
c = conn.cursor()

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
type = urllib.unquote_plus(params.get('type', ''))
name = urllib.unquote_plus(params.get('name', ''))

if mode == 'listVideos':
    listVideos(url)
elif mode == 'listSorting':
    listSorting(url, type)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'playLiveLeakVideo':
    playLiveLeakVideo(url)
elif mode == 'addSubreddit':
    addSubreddit()
elif mode == 'removeSubreddit':
    removeSubreddit(url)
elif mode == 'playRandomly':
    playRandomly(url, type)
elif mode == 'queueVideo':
    queueVideo(url, name)
elif mode == 'searchAskOne':
    searchAskOne(url)
elif mode == 'searchAskTwo':
    searchAskTwo(url)
elif mode == 'search':
    search(url, type)
else:
    index()