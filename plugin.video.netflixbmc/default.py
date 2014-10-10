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
import time
import shutil
import subprocess
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs


socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')
cj = cookielib.MozillaCookieJar()
urlMain = "http://www.netflix.com"
osWin = xbmc.getCondVisibility('system.platform.windows')
osLinux = xbmc.getCondVisibility('system.platform.linux')
osOsx = xbmc.getCondVisibility('system.platform.osx')
addonDir = xbmc.translatePath(addon.getAddonInfo('path'))
defaultFanart = os.path.join(addonDir ,'fanart.png')
addonUserDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
utilityPath = xbmc.translatePath('special://home/addons/'+addonID+'/resources/NetfliXBMC_Utility.exe')
sendKeysPath = xbmc.translatePath('special://home/addons/'+addonID+'/resources/NetfliXBMC_SendKeys.exe')
fakeVidPath = xbmc.translatePath('special://home/addons/'+addonID+'/resources/fakeVid.mp4')
downloadScript = xbmc.translatePath('special://home/addons/'+addonID+'/download.py')
searchHistoryFolder = os.path.join(addonUserDataFolder, "history")
cacheFolder = os.path.join(addonUserDataFolder, "cache")
cacheFolderCoversTMDB = os.path.join(cacheFolder, "covers")
cacheFolderFanartTMDB = os.path.join(cacheFolder, "fanart")
libraryFolder = xbmc.translatePath(addon.getSetting("libraryPath"))
libraryFolderMovies = os.path.join(libraryFolder, "Movies")
libraryFolderTV = os.path.join(libraryFolder, "TV")
cookieFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/cookies")
dontUseKiosk = addon.getSetting("dontUseKiosk") == "true"
browseTvShows = addon.getSetting("browseTvShows") == "true"
singleProfile = addon.getSetting("singleProfile") == "true"
showProfiles = addon.getSetting("showProfiles") == "true"
forceView = addon.getSetting("forceView") == "true"
useUtility = addon.getSetting("useUtility") == "true"
remoteControl = addon.getSetting("remoteControl") == "true"
updateDB = addon.getSetting("updateDB") == "true"
useTMDb = addon.getSetting("useTMDb") == "true"
username = addon.getSetting("username")
password = addon.getSetting("password")
viewIdVideos = addon.getSetting("viewIdVideos")
viewIdEpisodes = addon.getSetting("viewIdEpisodesNew")
viewIdActivity = addon.getSetting("viewIdActivity")
winBrowser = int(addon.getSetting("winBrowserNew"))
language = addon.getSetting("language")
auth = addon.getSetting("auth")
if len(language.split("-"))>1:
    country = language.split("-")[1]

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
userAgent = "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:32.0) Gecko/20100101 Firefox/32.0"
opener.addheaders = [('User-agent', userAgent)]

if not os.path.isdir(addonUserDataFolder):
    os.mkdir(addonUserDataFolder)
if not os.path.isdir(cacheFolder):
    os.mkdir(cacheFolder)
if not os.path.isdir(cacheFolderCoversTMDB):
    os.mkdir(cacheFolderCoversTMDB)
if not os.path.isdir(cacheFolderFanartTMDB):
    os.mkdir(cacheFolderFanartTMDB)
if not os.path.isdir(libraryFolder):
    xbmcvfs.mkdir(libraryFolder)
if not os.path.isdir(libraryFolderMovies):
    xbmcvfs.mkdir(libraryFolderMovies)
if not os.path.isdir(libraryFolderTV):
    xbmcvfs.mkdir(libraryFolderTV)
if os.path.exists(cookieFile):
    cj.load(cookieFile)

while (username == "" or password == ""):
    addon.openSettings()
    username = addon.getSetting("username")
    password = addon.getSetting("password")

if not addon.getSetting("html5MessageShown"):
    dialog = xbmcgui.Dialog()
    ok = dialog.ok('IMPORTANT!', 'NetfliXBMC >=1.3.0 only supports the new Netflix HTML5 User Interface! The only browsers working with HTML5 DRM playback for now are Chrome>=37 (Win/OSX/Linux) and IExplorer>=11 (Win8.1 only). Make sure you have the latest version installed and check your Netflix settings. Using Silverlight may still partially work, but its not supported anymore. The HTML5 Player is also much faster, supports 1080p and gives you a smoother playback (especially on Linux). See forum.xbmc.org for more info...')
    addon.setSetting("html5MessageShown", "true")

    
def index():
    if login():
        addDir(translation(30011), "", 'main', "", "movie")
        addDir(translation(30012), "", 'main', "", "tv")
        addDir(translation(30143), "", 'wiHome', "", "both")
        xbmcplugin.endOfDirectory(pluginhandle)


def main(type):
    addDir(translation(30002), urlMain+"/MyList?leid=595&link=seeall", 'listVideos', "", type)
    addDir(translation(30010), "", 'listViewingActivity', "", type)
    addDir(translation(30003), urlMain+"/WiRecentAdditionsGallery?nRR=releaseDate&nRT=all&pn=1&np=1&actionMethod=json", 'listVideos', "", type)
    if type=="tv":
        addDir(translation(30005), urlMain+"/WiGenre?agid=83", 'listVideos', "", type)
        addDir(translation(30007), "", 'listTvGenres', "", type)
    else:
        addDir(translation(30007), "WiGenre", 'listGenres', "", type)
    addDir(translation(30009), "KidsAltGenre", 'listGenres', "", type)
    addDir(translation(30008), "", 'search', "", type)
    xbmcplugin.endOfDirectory(pluginhandle)


def wiHome(type):
    if not singleProfile:
        setProfile()
    content = opener.open(urlMain+"/WiHome").read()
    match1 = re.compile('<div class="mrow(.+?)"><div class="hd clearfix"><h3> (.+?)</h3></div><div class="bd clearfix"><div class="slider triangleBtns " id="(.+?)"', re.DOTALL).findall(content)
    match2 = re.compile('class="hd clearfix"><h3><a href="(.+?)">(.+?)<', re.DOTALL).findall(content)
    for temp, title, sliderID in match1:
        if not "hide-completely" in temp:
            addDir(title.strip(), sliderID, 'listSliderVideos', "", type)
    for url, title in match2:
        if "WiAltGenre" in url or "WiSimilarsByViewType" in url or "WiRecentAdditionsGallery" in url:
            addDir(title.strip(), url, 'listVideos', "", type)
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideos(url, type):
    pDialog = xbmcgui.DialogProgress()
    pDialog.create('NetfliXBMC', translation(30142)+"...")
    if not singleProfile:
        setProfile()
    xbmcplugin.setContent(pluginhandle, "movies")
    content = opener.open(url).read()
    if not 'id="page-LOGIN"' in content:
        if singleProfile and 'id="page-ProfilesGate"' in content:
            forceChooseProfile()
        else:
            if '<div id="queue"' in content:
                content = content[content.find('<div id="queue"'):]
            content = content.replace("\\t","").replace("\\n", "").replace("\\", "")
            match1 = re.compile('<span id="dbs(.+?)_.+?alt=".+?"', re.DOTALL).findall(content)
            match2 = re.compile('<span class="title.*?"><a id="b(.+?)_', re.DOTALL).findall(content)
            match3 = re.compile('<a href="http://dvd.netflix.com/WiPlayer\?movieid=(.+?)&', re.DOTALL).findall(content)
            match4 = re.compile('<a class="playHover" href=".+?WiPlayer\?movieid=(.+?)&', re.DOTALL).findall(content)
            match5 = re.compile('"boxart":".+?","titleId":(.+?),', re.DOTALL).findall(content)
            if match1:
                match = match1
            elif match2:
                match = match2
            elif match3:
                match = match3
            elif match4:
                match = match4
            elif match5:
                match = match5
            i = 1
            for videoID in match:
                pDialog.update(i*100/len(match), translation(30142)+"...")
                listVideo(videoID, "", "", False, False, type)
                i+=1
            match1 = re.compile('&pn=(.+?)&', re.DOTALL).findall(url)
            match2 = re.compile('&from=(.+?)&', re.DOTALL).findall(url)
            matchApiRoot = re.compile('"API_ROOT":"(.+?)"', re.DOTALL).findall(content)
            matchApiBase = re.compile('"API_BASE_URL":"(.+?)"', re.DOTALL).findall(content)
            matchIdentifier = re.compile('"BUILD_IDENTIFIER":"(.+?)"', re.DOTALL).findall(content)
            if "agid=" in url and matchApiRoot and matchApiBase and matchIdentifier:
                genreID = url[url.find("agid=")+5:]
                addDir(translation(30001), matchApiRoot[0]+matchApiBase[0]+"/"+matchIdentifier[0]+"/wigenre?genreId="+genreID+"&full=false&from=51&to=100&_retry=0", 'listVideos', "", type)
            elif match1:
                currentPage = match1[0]
                nextPage = str(int(currentPage)+1)
                addDir(translation(30001), url.replace("&pn="+currentPage+"&", "&pn="+nextPage+"&"), 'listVideos', "", type)
            elif match2:
                currentFrom = match2[0]
                nextFrom = str(int(currentFrom)+50)
                currentTo = str(int(currentFrom)+49)
                nextTo = str(int(currentFrom)+99)
                addDir(translation(30001), url.replace("&from="+currentFrom+"&", "&from="+nextFrom+"&").replace("&to="+currentTo+"&", "&to="+nextTo+"&"), 'listVideos', "", type)
            if forceView:
                xbmc.executebuiltin('Container.SetViewMode('+viewIdVideos+')')
            xbmcplugin.endOfDirectory(pluginhandle)
    else:
        deleteCookies()
        xbmc.executebuiltin('XBMC.Notification(NetfliXBMC:,'+str(translation(30127))+',15000,'+icon+')')


def listSliderVideos(sliderID, type):
    pDialog = xbmcgui.DialogProgress()
    pDialog.create('NetfliXBMC', translation(30142)+"...")
    if not singleProfile:
        setProfile()
    xbmcplugin.setContent(pluginhandle, "movies")
    content = opener.open(urlMain+"/WiHome").read()
    if not 'id="page-LOGIN"' in content:
        if singleProfile and 'id="page-ProfilesGate"' in content:
            forceChooseProfile()
        else:
            content = content.replace("\\t","").replace("\\n", "").replace("\\", "")
            contentMain = content
            content = content[content.find('id="'+sliderID+'"'):]
            content = content[:content.find('class="ft"')]
            match = re.compile('<span id="dbs(.+?)_', re.DOTALL).findall(content)
            i = 1
            for videoID in match:
                listVideo(videoID, "", "", False, False, type)
                i+=1
            spl = contentMain.split('"remainderHTML":')
            for i in range(1, len(spl), 1):
                entry = spl[i]
                entry = entry[:entry.find('"rowId":')]
                if '"domId":"'+sliderID+'"' in entry:
                    match = re.compile('<span id="dbs(.+?)_', re.DOTALL).findall(entry)
                    i = 1
                    for videoID in match:
                        pDialog.update(i*100/(len(match)+10), translation(30142)+"...")
                        listVideo(videoID, "", "", False, False, type)
                        i+=1
            if forceView:
                xbmc.executebuiltin('Container.SetViewMode('+viewIdVideos+')')
            xbmcplugin.endOfDirectory(pluginhandle)
    else:
        deleteCookies()
        xbmc.executebuiltin('XBMC.Notification(NetfliXBMC:,'+str(translation(30127))+',15000,'+icon+')')


def listSearchVideos(url, type):
    pDialog = xbmcgui.DialogProgress()
    pDialog.create('NetfliXBMC', translation(30142)+"...")
    if not singleProfile:
        setProfile()
    xbmcplugin.setContent(pluginhandle, "movies")
    content = opener.open(url).read()
    content = json.loads(content)
    i = 1
    if "galleryVideos" in content:
        for item in content["galleryVideos"]["items"]:
            pDialog.update(i*100/len(content["galleryVideos"]["items"]), translation(30142)+"...")
            listVideo(str(item["id"]), "", "", False, False, type)
            i+=1
        if forceView:
            xbmc.executebuiltin('Container.SetViewMode('+viewIdVideos+')')
        xbmcplugin.endOfDirectory(pluginhandle)
    else:
        xbmc.executebuiltin('XBMC.Notification(NetfliXBMC:,'+str(translation(30146))+',5000,'+icon+')')


def listVideo(videoID, title, thumbUrl, tvshowIsEpisode, hideMovies, type):
    videoDetails = getVideoInfo(videoID)
    match = re.compile('<span class="title.*?>(.+?)<', re.DOTALL).findall(videoDetails)
    if not title:
        title = match[0].strip()
    year = ""
    match = re.compile('<span class="year.*?>(.+?)<', re.DOTALL).findall(videoDetails)
    if match:
        year = match[0]
    if not thumbUrl:
        match = re.compile('src="(.+?)"', re.DOTALL).findall(videoDetails)
        thumbUrl = match[0].replace("/webp/","/images/").replace(".webp",".jpg")
    match = re.compile('<span class="mpaaRating.*?>(.+?)<', re.DOTALL).findall(videoDetails)
    mpaa = ""
    if match:
        mpaa = match[0]
    match = re.compile('<span class="duration.*?>(.+?)<', re.DOTALL).findall(videoDetails)
    duration = ""
    if match:
        duration = match[0].lower()
    if duration.split(' ')[-1] in ["minutes", "minutos", "minuter", "minutter", "minuuttia", "minuten"]:
        videoType = "movie"
        videoTypeTemp = videoType
        duration = duration.split(" ")[0]
    else:
        videoTypeTemp = "tv"
        if tvshowIsEpisode:
            videoType = "episode"
            year = ""
        else:
            videoType = "tvshow"
        duration = ""
    if useTMDb:
        yearTemp = year
        titleTemp = title
        if " - " in titleTemp:
            titleTemp = titleTemp[titleTemp.find(" - ")+3:]
        if ": " in titleTemp:
            titleTemp = titleTemp[:titleTemp.find(": ")]
        if "-" in yearTemp:
            yearTemp = yearTemp.split("-")[0]
        filename = (''.join(c for c in unicode(videoID, 'utf-8') if c not in '/\\:?"*|<>')).strip()+".jpg"
        filenameNone = (''.join(c for c in unicode(videoID, 'utf-8') if c not in '/\\:?"*|<>')).strip()+".none"
        coverFile = os.path.join(cacheFolderCoversTMDB, filename)
        coverFileNone = os.path.join(cacheFolderCoversTMDB, filenameNone)
        if not os.path.exists(coverFile) and not os.path.exists(coverFileNone):
            xbmc.executebuiltin('XBMC.RunScript('+downloadScript+', '+urllib.quote_plus(videoTypeTemp)+', '+urllib.quote_plus(videoID)+', '+urllib.quote_plus(titleTemp)+', '+urllib.quote_plus(yearTemp)+')')
    match = re.compile('src=".+?">.*?<.*?>(.+?)<', re.DOTALL).findall(videoDetails)
    desc = ""
    if match:
        desc = match[0].replace("&amp;", "&")
    match = re.compile('Director:</dt><dd>(.+?)<', re.DOTALL).findall(videoDetails)
    director = ""
    if match:
        director = match[0].strip()
    match = re.compile('<span class="genre.*?>(.+?)<', re.DOTALL).findall(videoDetails)
    genre = ""
    if match:
        genre = match[0]
    match = re.compile('<span class="rating.*?>(.+?)<', re.DOTALL).findall(videoDetails)
    rating = ""
    if rating:
        rating = match[0]
    title = title.replace("&amp;", "&")
    nextMode = "playVideoMain"
    if browseTvShows and videoType == "tvshow":
        nextMode = "listSeasons"
    added = False
    if "/MyList" in url and videoTypeTemp==type:
        addVideoDirR(title, videoID, nextMode, thumbUrl, videoType, desc, duration, year, mpaa, director, genre, rating)
        added = True
    elif videoType == "movie" and hideMovies:
        pass
    elif videoTypeTemp==type or type=="both":
        addVideoDir(title, videoID, nextMode, thumbUrl, videoType, desc, duration, year, mpaa, director, genre, rating)
        added = True
    return added


def listGenres(type, videoType):
    if not singleProfile:
        setProfile()
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    content = opener.open(urlMain+"/WiHome").read()
    match = re.compile('/'+type+'\\?agid=(.+?)">(.+?)<', re.DOTALL).findall(content)
    for genreID, title in match:
        if not genreID=="83":
            if type=="KidsAltGenre":
                addDir(title, urlMain+"/"+type+"?agid="+genreID+"&pn=1&np=1&actionMethod=json", 'listVideos', "", videoType)
            else:
                addDir(title, urlMain+"/"+type+"?agid="+genreID, 'listVideos', "", videoType)
    xbmcplugin.endOfDirectory(pluginhandle)


def listTvGenres(videoType):
    if not singleProfile:
        setProfile()
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    content = opener.open(urlMain+"/WiGenre?agid=83").read()
    content = content[content.find('id="subGenres_menu"'):]
    content = content[:content.find('</div>')]
    match = re.compile('<li ><a href=".+?/WiGenre\\?agid=(.+?)&.+?"><span>(.+?)<', re.DOTALL).findall(content)
    for genreID, title in match:
        addDir(title, urlMain+"/WiGenre?agid="+genreID, 'listVideos', "", videoType)
    xbmcplugin.endOfDirectory(pluginhandle)


def listSeasons(seriesName, seriesID, thumb):
    content = getSeriesInfo(seriesID)
    content = json.loads(content)
    seasons = []
    for item in content["episodes"]:
        if item[0]["season"] not in seasons:
            seasons.append(item[0]["season"])
    for season in seasons:
        addSeasonDir("Season "+str(season), str(season), 'listEpisodes', thumb, seriesName, seriesID)
    xbmcplugin.endOfDirectory(pluginhandle)


def listEpisodes(seriesID, season):
    xbmcplugin.setContent(pluginhandle, "episodes")
    content = getSeriesInfo(seriesID)
    content = json.loads(content)
    for test in content["episodes"]:
        for item in test:
            episodeSeason = str(item["season"])
            if episodeSeason == season:
                episodeID = str(item["episodeId"])
                episodeNr = str(item["episode"])
                episodeTitle = item["title"].encode('utf-8')
                duration = item["runtime"]
                bookmarkPosition = item["bookmarkPosition"]
                playcount=0
                if (float(bookmarkPosition)/float(duration))>=0.9:
                    playcount=1
                desc = item["synopsis"].encode('utf-8')
                try:
                    thumb = item["stills"][0]["url"]
                except:
                    thumb = ""
                addEpisodeDir(episodeTitle, episodeID, 'playVideoMain', thumb, desc, str(duration), season, episodeNr, seriesID, playcount)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIdEpisodes+')')
    xbmcplugin.endOfDirectory(pluginhandle)


def listViewingActivity(type):
    pDialog = xbmcgui.DialogProgress()
    pDialog.create('NetfliXBMC', translation(30142)+"...")
    if not singleProfile:
        setProfile()
    xbmcplugin.setContent(pluginhandle, "movies")
    content = opener.open(urlMain+"/WiViewingActivity").read()
    count = 0
    videoIDs = []
    spl = content.split('<li data-series=')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        pDialog.update((count+1)*100/len(spl), translation(30142)+"...")
        matchId1 = re.compile('"(.*?)"', re.DOTALL).findall(entry)
        matchId2 = re.compile('data-movieid="(.*?)"', re.DOTALL).findall(entry)
        if matchId1[0]:
            videoID = matchId1[0]
        elif matchId2[0]:
            videoID = matchId2[0]
        match = re.compile('class="col date nowrap">(.+?)<', re.DOTALL).findall(entry)
        date = match[0]
        matchTitle1 = re.compile('class="seriestitle">(.+?)</a>', re.DOTALL).findall(entry)
        matchTitle2 = re.compile('class="col title">.+?>(.+?)<', re.DOTALL).findall(entry)
        if matchId1[0]:
            title = matchTitle1[0].replace("&amp;", "&").replace("&quot;", '"').replace("</span>", "")
        elif matchId2[0]:
            title = matchTitle2[0]
        title = date+" - "+title
        if videoID not in videoIDs:
            videoIDs.append(videoID)
            added = listVideo(videoID, title, "", False, False, type)
            if added:
                count += 1
            if count == 40:
                break
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIdActivity+')')
    xbmcplugin.endOfDirectory(pluginhandle)


def getVideoInfo(videoID):
    cacheFile = os.path.join(cacheFolder, videoID+".cache")
    if os.path.exists(cacheFile):
        fh = xbmcvfs.File(cacheFile, 'r')
        content = fh.read()
        fh.close()
    else:
        content = opener.open(urlMain+"/JSON/BOB?movieid="+videoID).read()
        fh = xbmcvfs.File(cacheFile, 'w')
        fh.write(content)
        fh.close()
    return content.replace("\\t","").replace("\\n", "").replace("\\", "")


def getSeriesInfo(seriesID):
    cacheFile = os.path.join(cacheFolder, seriesID+"_episodes.cache")
    if os.path.exists(cacheFile) and (time.time()-os.path.getmtime(cacheFile) < 60*5):
        fh = xbmcvfs.File(cacheFile, 'r')
        content = fh.read()
        fh.close()
    else:
        url = "http://api-global.netflix.com/desktop/odp/episodes?languages="+language+"&forceEpisodes=true&routing=redirect&video="+seriesID+"&country="+country
        content = opener.open(url).read()
        fh = xbmcvfs.File(cacheFile, 'w')
        fh.write(content)
        fh.close()
    return content


def addMyListToLibrary():
    if not singleProfile:
        setProfile()
    content = opener.open(urlMain+"/MyList?leid=595&link=seeall").read()
    if not 'id="page-LOGIN"' in content:
        if singleProfile and 'id="page-ProfilesGate"' in content:
            forceChooseProfile()
        else:
            if '<div id="queue"' in content:
                content = content[content.find('<div id="queue"'):]
            content = content.replace("\\t","").replace("\\n", "").replace("\\", "")
            match1 = re.compile('<span id="dbs(.+?)_.+?alt=".+?"', re.DOTALL).findall(content)
            match2 = re.compile('<span class="title.*?"><a id="b(.+?)_', re.DOTALL).findall(content)
            match3 = re.compile('<a href="http://dvd.netflix.com/WiPlayer\?movieid=(.+?)&', re.DOTALL).findall(content)
            match4 = re.compile('<a class="playHover" href=".+?WiPlayer\?movieid=(.+?)&', re.DOTALL).findall(content)
            match5 = re.compile('"boxart":".+?","titleId":(.+?),', re.DOTALL).findall(content)
            if match1:
                match = match1
            elif match2:
                match = match2
            elif match3:
                match = match3
            elif match4:
                match = match4
            elif match5:
                match = match5
            for videoID in match:
                videoDetails = getVideoInfo(videoID)
                match = re.compile('<span class="title ".*?>(.+?)<\/span>', re.DOTALL).findall(videoDetails)
                title = match[0].strip()
                title = title.replace("&amp;", "&")
                match = re.compile('<span class="year".*?>(.+?)<\/span>', re.DOTALL).findall(videoDetails)
                year = ""
                if match:
                    year = match[0]
                match = re.compile('<span class="duration.*?".*?>(.+?)<\/span>', re.DOTALL).findall(videoDetails)
                duration = ""
                if match:
                    duration = match[0].lower()
                if "minutes" in duration:
                    try:
                        if year:
                            title = title+" ("+year+")"
                        addMovieToLibrary(videoID, title, False)
                    except:
                        pass
                else:
                    try:
                        addSeriesToLibrary(videoID, title, "", False)
                    except:
                        pass
            if updateDB:
                xbmc.executebuiltin('UpdateLibrary(video)')


def playVideo(id):
    playVideoMain(id)
    xbmc.sleep(5000) 
    listitem = xbmcgui.ListItem(path=fakeVidPath)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
    xbmc.PlayList(xbmc.PLAYLIST_VIDEO).clear()
      

def playVideoMain(id):
    xbmc.Player().stop()
    if singleProfile:
        url = urlMain+"/WiPlayer?movieid="+id
    else:
        token = ""
        if addon.getSetting("profile"):
            token = addon.getSetting("profile")
        url = "https://www.netflix.com/SwitchProfile?tkn="+token+"&nextpage="+urllib.quote_plus(urlMain+"/WiPlayer?movieid="+id)
    kiosk = "yes"
    if dontUseKiosk:
        kiosk = "no"
    if osOsx:
        xbmc.executebuiltin("RunPlugin(plugin://plugin.program.chrome.launcher/?url="+urllib.quote_plus(url)+"&mode=showSite&kiosk="+kiosk+")")
        try:
            xbmc.sleep(5000)
            subprocess.Popen('cliclick c:500,500', shell=True)
            subprocess.Popen('cliclick kp:arrow-up', shell=True)
            xbmc.sleep(5000)
            subprocess.Popen('cliclick c:500,500', shell=True)
            subprocess.Popen('cliclick kp:arrow-up', shell=True)
            xbmc.sleep(5000)
            subprocess.Popen('cliclick c:500,500', shell=True)
            subprocess.Popen('cliclick kp:arrow-up', shell=True)
        except:
            pass
    elif osLinux:
        xbmc.executebuiltin("RunPlugin(plugin://plugin.program.chrome.launcher/?url="+urllib.quote_plus(url)+"&mode=showSite&kiosk="+kiosk+")")
        try:
            xbmc.sleep(5000)
            subprocess.Popen('xdotool mousemove 9999 9999', shell=True)
            xbmc.sleep(5000)
            subprocess.Popen('xdotool mousemove 9999 9999', shell=True)
            xbmc.sleep(5000)
            subprocess.Popen('xdotool mousemove 9999 9999', shell=True)
        except:
            pass
    elif osWin:
        if winBrowser == 1:
            path = 'C:\\Program Files\\Internet Explorer\\iexplore.exe'
            path64 = 'C:\\Program Files (x86)\\Internet Explorer\\iexplore.exe'
            if os.path.exists(path):
                subprocess.Popen('"'+path+'" -k "'+url+'"', shell=False)
            elif os.path.exists(path64):
                subprocess.Popen('"'+path64+'" -k "'+url+'"', shell=False)
        else:
            xbmc.executebuiltin("RunPlugin(plugin://plugin.program.chrome.launcher/?url="+urllib.quote_plus(url)+"&mode=showSite&kiosk="+kiosk+")")
        if useUtility:
            subprocess.Popen('"'+utilityPath+'"', shell=False)
    if remoteControl:
        myWindow = window('window.xml', addon.getAddonInfo('path'), 'default',)
        myWindow.doModal()
        

def configureUtility():
    if osWin:
        subprocess.Popen('"'+utilityPath+'"'+' config=yes', shell=False)


def deleteCookies():
    if os.path.exists(cookieFile):
        os.remove(cookieFile)
        xbmc.executebuiltin('XBMC.Notification(NetfliXBMC:,Cookies have been deleted!,5000,'+icon+')')


def deleteCache():
    if os.path.exists(cacheFolder):
        try:
            shutil.rmtree(cacheFolder)
            xbmc.executebuiltin('XBMC.Notification(NetfliXBMC:,Cache has been deleted!,5000,'+icon+')')
        except:
            pass


def resetAddon():
    dialog = xbmcgui.Dialog()
    if dialog.yesno("NetfliXBMC:", "Really reset the addon?"):
      if os.path.exists(addonUserDataFolder):
          try:
              shutil.rmtree(addonUserDataFolder)
              xbmc.executebuiltin('XBMC.Notification(NetfliXBMC:,Addon has been reset!,5000,'+icon+')')
          except:
              pass


def search(type):
    keyboard = xbmc.Keyboard('', translation(30008))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText().replace(" ", "+")
        listSearchVideos("http://api-global.netflix.com/desktop/search/instantsearch?esn=www&term="+search_string+"&locale="+language+"&country="+country+"&authURL="+auth+"&_retry=0&routing=redirect", type)


def addToQueue(id):
    opener.open(urlMain+"/AddToQueue?movieid="+id+"&authURL="+auth)
    xbmc.executebuiltin('XBMC.Notification(NetfliXBMC:,'+str(translation(30144))+',3000,'+icon+')')


def removeFromQueue(id):
    opener.open(urlMain+"/QueueDelete?movieid="+id+"&authURL="+auth)
    xbmc.executebuiltin('XBMC.Notification(NetfliXBMC:,'+str(translation(30145))+',3000,'+icon+')')
    xbmc.executebuiltin("Container.Refresh")


def login():
    content = opener.open(urlMain+"/Login").read()
    match = re.compile('"LOCALE":"(.+?)"', re.DOTALL).findall(content)
    if match and not addon.getSetting("language"):
        addon.setSetting("language", match[0])
    if not "Sorry, Netflix is not available in your country yet." in content and not "Sorry, Netflix hasn't come to this part of the world yet" in content:
        match = re.compile('id="signout".+?authURL=(.+?)"', re.DOTALL).findall(content)
        if match:
            addon.setSetting("auth", match[0])
        if 'id="page-LOGIN"' in content:
            match = re.compile('name="authURL" value="(.+?)"', re.DOTALL).findall(content)
            authUrl = match[0]
            addon.setSetting("auth", authUrl)
            content = opener.open("https://signup.netflix.com/Login", "authURL="+urllib.quote_plus(authUrl)+"&email="+urllib.quote_plus(username)+"&password="+urllib.quote_plus(password)+"&RememberMe=on").read()
            match = re.compile('"LOCALE":"(.+?)"', re.DOTALL).findall(content)
            if match and not addon.getSetting("language"):
                addon.setSetting("language", match[0])
            cj.save(cookieFile)
        if not addon.getSetting("profile") and not singleProfile:
            chooseProfile()
        elif not singleProfile and showProfiles:
            chooseProfile()
        return True
    else:
        xbmc.executebuiltin('XBMC.Notification(NetfliXBMC:,'+str(translation(30126))+',10000,'+icon+')')
        return False


def setProfile():
    token = addon.getSetting("profile")
    opener.open("https://www.netflix.com/ProfilesGate?nextpage=http%3A%2F%2Fwww.netflix.com%2FDefault")
    opener.open("https://api-global.netflix.com/desktop/account/profiles/switch?switchProfileGuid="+token)
    cj.save(cookieFile)


def chooseProfile():
    content = opener.open("https://www.netflix.com/ProfilesGate?nextpage=http%3A%2F%2Fwww.netflix.com%2FDefault").read()
    match = re.compile('"profileName":"(.+?)".+?token":"(.+?)"', re.DOTALL).findall(content)
    profiles = []
    tokens = []
    for p, t in match:
        profiles.append(p)
        tokens.append(t)
    dialog = xbmcgui.Dialog()
    nr = dialog.select(translation(30113), profiles)
    if nr >= 0:
        token = tokens[nr]
        # Profile selection isn't remembered, so it has to be executed before every requests (setProfile)
        # If you know a solution for this, please let me know
        # opener.open("https://api-global.netflix.com/desktop/account/profiles/switch?switchProfileGuid="+token)
        addon.setSetting("profile", token)
        cj.save(cookieFile)


def forceChooseProfile():
    addon.setSetting("singleProfile", "false")
    xbmc.executebuiltin('XBMC.Notification(NetfliXBMC:,'+str(translation(30111))+',5000,'+icon+')')
    chooseProfile()


def addMovieToLibrary(movieID, title, singleUpdate=True):
    movieFolderName = (''.join(c for c in unicode(title, 'utf-8') if c not in '/\\:?"*|<>')).strip(' .')
    dir = os.path.join(libraryFolderMovies, movieFolderName)
    if not os.path.isdir(dir):
        xbmcvfs.mkdir(dir)
        fh = xbmcvfs.File(os.path.join(dir, "movie.strm"), 'w')
        fh.write("plugin://plugin.video.netflixbmc/?mode=playVideo&url="+movieID)
        fh.close()
    if updateDB and singleUpdate:
        xbmc.executebuiltin('UpdateLibrary(video)')


def addSeriesToLibrary(seriesID, seriesTitle, season, singleUpdate=True):
    seriesFolderName = (''.join(c for c in unicode(seriesTitle, 'utf-8') if c not in '/\\:?"*|<>')).strip(' .')
    seriesDir = os.path.join(libraryFolderTV, seriesFolderName)
    if not os.path.isdir(seriesDir):
        xbmcvfs.mkdir(seriesDir)
    content = getSeriesInfo(seriesID)
    content = json.loads(content)
    for test in content["episodes"]:
        for item in test:
            episodeSeason = str(item["season"])
            seasonCheck = True
            if season:
                seasonCheck = episodeSeason == season
            if seasonCheck:
                seasonDir = os.path.join(seriesDir, "Season "+episodeSeason)
                if not os.path.isdir(seasonDir):
                    xbmcvfs.mkdir(seasonDir)
                episodeID = str(item["episodeId"])
                episodeNr = str(item["episode"])
                episodeTitle = item["title"].encode('utf-8')
                if len(episodeNr) == 1:
                    episodeNr = "0"+episodeNr
                seasonNr = episodeSeason
                if len(seasonNr) == 1:
                    seasonNr = "0"+seasonNr
                filename = "S"+seasonNr+"E"+episodeNr+" - "+episodeTitle+".strm"
                filename = (''.join(c for c in unicode(filename, 'utf-8') if c not in '/\\:?"*|<>')).strip(' .')
                fh = xbmcvfs.File(os.path.join(seasonDir, filename), 'w')
                fh.write("plugin://plugin.video.netflixbmc/?mode=playVideo&url="+episodeID)
                fh.close()
    if updateDB and singleUpdate:
        xbmc.executebuiltin('UpdateLibrary(video)')


def playTrailer(title):
    try:
        content = opener.open("http://gdata.youtube.com/feeds/api/videos?vq="+title.strip().replace(" ", "+")+"+trailer&racy=include&orderby=relevance").read()
        match = re.compile('<id>http://gdata.youtube.com/feeds/api/videos/(.+?)</id>', re.DOTALL).findall(content.split('<entry>')[1])
        xbmc.Player().play("plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=" + match[0])
    except:
        pass


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


def addDir(name, url, mode, iconimage, type=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&type="+str(type)+"&thumb="+urllib.quote_plus(iconimage)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name})
    entries = []
    if "/MyList" in url:
        entries.append((translation(30122), 'RunPlugin(plugin://plugin.video.netflixbmc/?mode=addMyListToLibrary)',))
    if not singleProfile:
        entries.append((translation(30110), 'RunPlugin(plugin://plugin.video.netflixbmc/?mode=chooseProfile)',))
    liz.setProperty("fanart_image", defaultFanart)
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addVideoDir(name, url, mode, iconimage, videoType="", desc="", duration="", year="", mpaa="", director="", genre="", rating=""):
    filename = (''.join(c for c in unicode(url, 'utf-8') if c not in '/\\:?"*|<>')).strip()+".jpg"
    coverFile = os.path.join(cacheFolderCoversTMDB, filename)
    fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
    if os.path.exists(coverFile):
        iconimage = coverFile
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&thumb="+urllib.quote_plus(iconimage)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name, "plot": desc, "duration": duration, "year": year, "mpaa": mpaa, "director": director, "genre": genre, "rating": rating})
    if os.path.exists(fanartFile):
        liz.setProperty("fanart_image", fanartFile)
    elif os.path.exists(coverFile):
        liz.setProperty("fanart_image", coverFile)
    entries = []
    if videoType == "tvshow":
        if browseTvShows:
            entries.append((translation(30121), 'Container.Update(plugin://plugin.video.netflixbmc/?mode=playVideoMain&url='+urllib.quote_plus(url)+'&thumb='+urllib.quote_plus(iconimage)+')',))
        else:
            entries.append((translation(30118), 'Container.Update(plugin://plugin.video.netflixbmc/?mode=listSeasons&url='+urllib.quote_plus(url)+'&thumb='+urllib.quote_plus(iconimage)+')',))
    if videoType != "episode":
        entries.append((translation(30134), 'RunPlugin(plugin://plugin.video.netflixbmc/?mode=playTrailer&url='+urllib.quote_plus(name)+')',))
        entries.append((translation(30114), 'RunPlugin(plugin://plugin.video.netflixbmc/?mode=addToQueue&url='+urllib.quote_plus(url)+')',))
        entries.append((translation(30140), 'Container.Update(plugin://plugin.video.netflixbmc/?mode=listVideos&url='+urllib.quote_plus(urlMain+"/WiMovie/"+url)+'&type=movie)',))
        entries.append((translation(30141), 'Container.Update(plugin://plugin.video.netflixbmc/?mode=listVideos&url='+urllib.quote_plus(urlMain+"/WiMovie/"+url)+'&type=tv)',))
    if videoType == "tvshow":
        entries.append((translation(30122), 'RunPlugin(plugin://plugin.video.netflixbmc/?mode=addSeriesToLibrary&url=&name='+urllib.quote_plus(name.strip())+'&seriesID='+urllib.quote_plus(url)+')',))
    elif videoType == "movie":
        entries.append((translation(30122), 'RunPlugin(plugin://plugin.video.netflixbmc/?mode=addMovieToLibrary&url='+urllib.quote_plus(url)+'&name='+urllib.quote_plus(name.strip()+' ('+year+')')+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addVideoDirR(name, url, mode, iconimage, videoType="", desc="", duration="", year="", mpaa="", director="", genre="", rating=""):
    filename = (''.join(c for c in unicode(url, 'utf-8') if c not in '/\\:?"*|<>')).strip()+".jpg"
    coverFile = os.path.join(cacheFolderCoversTMDB, filename)
    fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
    if os.path.exists(coverFile):
        iconimage = coverFile
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&thumb="+urllib.quote_plus(iconimage)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name, "plot": desc, "duration": duration, "year": year, "mpaa": mpaa, "director": director, "genre": genre, "rating": rating})
    if os.path.exists(fanartFile):
        liz.setProperty("fanart_image", fanartFile)
    elif os.path.exists(coverFile):
        liz.setProperty("fanart_image", coverFile)
    entries = []
    if videoType == "tvshow":
        if browseTvShows:
            entries.append((translation(30121), 'Container.Update(plugin://plugin.video.netflixbmc/?mode=playVideoMain&url='+urllib.quote_plus(url)+'&thumb='+urllib.quote_plus(iconimage)+')',))
        else:
            entries.append((translation(30118), 'Container.Update(plugin://plugin.video.netflixbmc/?mode=listSeasons&url='+urllib.quote_plus(url)+'&thumb='+urllib.quote_plus(iconimage)+')',))
    entries.append((translation(30134), 'RunPlugin(plugin://plugin.video.netflixbmc/?mode=playTrailer&url='+urllib.quote_plus(name)+')',))
    entries.append((translation(30115), 'RunPlugin(plugin://plugin.video.netflixbmc/?mode=removeFromQueue&url='+urllib.quote_plus(url)+')',))
    entries.append((translation(30140), 'Container.Update(plugin://plugin.video.netflixbmc/?mode=listVideos&url='+urllib.quote_plus(urlMain+"/WiMovie/"+url)+'&type=movie)',))
    entries.append((translation(30141), 'Container.Update(plugin://plugin.video.netflixbmc/?mode=listVideos&url='+urllib.quote_plus(urlMain+"/WiMovie/"+url)+'&type=tv)',))
    if videoType == "tvshow":
        entries.append((translation(30122), 'RunPlugin(plugin://plugin.video.netflixbmc/?mode=addSeriesToLibrary&url=&name='+str(name.strip())+'&seriesID='+str(url)+')',))
    elif videoType == "movie":
        entries.append((translation(30122), 'RunPlugin(plugin://plugin.video.netflixbmc/?mode=addMovieToLibrary&url='+urllib.quote_plus(url)+'&name='+str(name.strip()+' ('+year+')')+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addSeasonDir(name, url, mode, iconimage, seriesName, seriesID):
    filename = (''.join(c for c in unicode(seriesID, 'utf-8') if c not in '/\\:?"*|<>')).strip()+".jpg"
    fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
    coverFile = os.path.join(cacheFolderCoversTMDB, filename)
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&seriesID="+urllib.quote_plus(seriesID)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name})
    if os.path.exists(fanartFile):
        liz.setProperty("fanart_image", fanartFile)
    elif os.path.exists(coverFile):
        liz.setProperty("fanart_image", coverFile)
    entries = []
    entries.append((translation(30122), 'RunPlugin(plugin://plugin.video.netflixbmc/?mode=addSeriesToLibrary&url='+urllib.quote_plus(url)+'&name='+str(seriesName.strip())+'&seriesID='+str(seriesID)+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addEpisodeDir(name, url, mode, iconimage, desc="", duration="", season="", episodeNr="", seriesID="", playcount=""):
    filename = (''.join(c for c in unicode(seriesID, 'utf-8') if c not in '/\\:?"*|<>')).strip()+".jpg"
    fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
    coverFile = os.path.join(cacheFolderCoversTMDB, filename)
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name, "plot": desc, "duration": duration, "season": season, "episode": episodeNr, "playcount": playcount})
    if os.path.exists(fanartFile):
        liz.setProperty("fanart_image", fanartFile)
    elif os.path.exists(coverFile):
        liz.setProperty("fanart_image", coverFile)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


class window(xbmcgui.WindowXMLDialog):
    def onAction(self, action):
        ACTION_SELECT_ITEM = 7
        ACTION_PARENT_DIR = 9
        ACTION_PREVIOUS_MENU = 10
        ACTION_STOP = 13
        ACTION_SHOW_INFO = 11
        ACTION_SHOW_GUI = 18
        ACTION_MOVE_LEFT = 1
        ACTION_MOVE_RIGHT = 2
        ACTION_MOVE_UP = 3
        ACTION_MOVE_DOWN = 4
        KEY_BUTTON_BACK = 275
        if osWin:
            proc = subprocess.Popen('WMIC PROCESS get Caption', shell=True, stdout=subprocess.PIPE)
            procAll = ""
            for line in proc.stdout:
                procAll+=line
            if "chrome.exe" in procAll:
                if action in [ACTION_SHOW_INFO, ACTION_SHOW_GUI, ACTION_STOP, ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, KEY_BUTTON_BACK]:
                    subprocess.Popen('"'+sendKeysPath+'"'+' sendKey=Close', shell=False)
                    self.close()
                elif action==ACTION_SELECT_ITEM:
                    subprocess.Popen('"'+sendKeysPath+'"'+' sendKey=PlayPause', shell=False)
                elif action==ACTION_MOVE_LEFT:
                    subprocess.Popen('"'+sendKeysPath+'"'+' sendKey=SeekLeft', shell=False)
                elif action==ACTION_MOVE_RIGHT:
                    subprocess.Popen('"'+sendKeysPath+'"'+' sendKey=SeekRight', shell=False)
                elif action==ACTION_MOVE_UP:
                    subprocess.Popen('"'+sendKeysPath+'"'+' sendKey=VolumeUp', shell=False)
                elif action==ACTION_MOVE_DOWN:
                    subprocess.Popen('"'+sendKeysPath+'"'+' sendKey=VolumeDown', shell=False)
            else:
                self.close()
        elif osLinux:
            proc = subprocess.Popen('/bin/ps ax', shell=True, stdout=subprocess.PIPE)
            procAll = ""
            for line in proc.stdout:
                procAll+=line
            if "chrome" in procAll or "chromium" in procAll:
                if action in [ACTION_SHOW_INFO, ACTION_SHOW_GUI, ACTION_STOP, ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, KEY_BUTTON_BACK]:
                    subprocess.Popen('xdotool key alt+F4', shell=True)
                    self.close()
                elif action==ACTION_SELECT_ITEM:
                    subprocess.Popen('xdotool key Return', shell=True)
                elif action==ACTION_MOVE_LEFT:
                    subprocess.Popen('xdotool key Left', shell=True)
                elif action==ACTION_MOVE_RIGHT:
                    subprocess.Popen('xdotool key Right', shell=True)
                elif action==ACTION_MOVE_UP:
                    subprocess.Popen('xdotool key Up', shell=True)
                elif action==ACTION_MOVE_DOWN:
                    subprocess.Popen('xdotool key Down', shell=True)
            else:
                self.close()
        elif osOSX:
            proc = subprocess.Popen('/bin/ps ax', shell=True, stdout=subprocess.PIPE)
            procAll = ""
            for line in proc.stdout:
                procAll+=line
            if "chrome" in procAll:
                if action in [ACTION_SHOW_INFO, ACTION_SHOW_GUI, ACTION_STOP, ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, KEY_BUTTON_BACK]:
                    subprocess.Popen('cliclick kd:alt', shell=True)
                    subprocess.Popen('cliclick kp:f4', shell=True)
                    self.close()
                elif action==ACTION_SELECT_ITEM:
                    subprocess.Popen('cliclick kp:return', shell=True)
                elif action==ACTION_MOVE_LEFT:
                    subprocess.Popen('cliclick kp:arrow-left', shell=True)
                elif action==ACTION_MOVE_RIGHT:
                    subprocess.Popen('cliclick kp:arrow-right', shell=True)
                elif action==ACTION_MOVE_UP:
                    subprocess.Popen('cliclick kp:arrow-up', shell=True)
                elif action==ACTION_MOVE_DOWN:
                    subprocess.Popen('cliclick kp:arrow-down', shell=True)
            else:
                self.close()


params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))
name = urllib.unquote_plus(params.get('name', ''))
season = urllib.unquote_plus(params.get('season', ''))
seriesID = urllib.unquote_plus(params.get('seriesID', ''))
type = urllib.unquote_plus(params.get('type', ''))

if mode == 'main':
    main(type)
elif mode == 'wiHome':
    wiHome(type)
elif mode == 'listVideos':
    listVideos(url, type)
elif mode == 'listSliderVideos':
    listSliderVideos(url, type)
elif mode == 'listSearchVideos':
    listSearchVideos(url, type)
elif mode == 'addToQueue':
    addToQueue(url)
elif mode == 'removeFromQueue':
    removeFromQueue(url)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'playVideoMain':
    playVideoMain(url)
elif mode == 'search':
    search(type)
elif mode == 'login':
    login()
elif mode == 'chooseProfile':
    chooseProfile()
elif mode == 'listGenres':
    listGenres(url, type)
elif mode == 'listTvGenres':
    listTvGenres(type)
elif mode == 'listViewingActivity':
    listViewingActivity(type)
elif mode == 'listSeasons':
    listSeasons(name, url, thumb)
elif mode == 'listEpisodes':
    listEpisodes(seriesID, url)
elif mode == 'configureUtility':
    configureUtility()
elif mode == 'deleteCookies':
    deleteCookies()
elif mode == 'deleteCache':
    deleteCache()
elif mode == 'resetAddon':
    resetAddon()
elif mode == 'playTrailer':
    playTrailer(url)
elif mode == 'addMyListToLibrary':
    addMyListToLibrary()
elif mode == 'addMovieToLibrary':
    addMovieToLibrary(url, name)
elif mode == 'addSeriesToLibrary':
    addSeriesToLibrary(seriesID, name, url)
else:
    index()
