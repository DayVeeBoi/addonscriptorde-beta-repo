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
import subprocess
import xbmcplugin
import xbmcgui
import xbmcaddon

socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')
cj = cookielib.MozillaCookieJar()
urlMain = "http://movies.netflix.com"
osWin = xbmc.getCondVisibility('system.platform.windows')
osLinux = xbmc.getCondVisibility('system.platform.linux')
osOsx = xbmc.getCondVisibility('system.platform.osx')
addonUserDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
utilityPath = xbmc.translatePath('special://home/addons/'+addonID+'/resources/NetfliXBMC_Utility.exe')
searchHistoryFolder=os.path.join(addonUserDataFolder, "history")
cacheFolder = os.path.join(addonUserDataFolder, "cache")
libraryFolder = xbmc.translatePath("special://profile/addon_data/"+addonID+"/library")
libraryFolderMovies = xbmc.translatePath("special://profile/addon_data/"+addonID+"/library/Movies")
libraryFolderTV = xbmc.translatePath("special://profile/addon_data/"+addonID+"/library/TV")
cookieFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/cookies")
profileFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/profile")
authFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/authUrl")
localeFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/locale")
updateDB=addon.getSetting("updateDB")=="true"
browseTvShows=addon.getSetting("browseTvShows")=="true"
singleProfile=addon.getSetting("singleProfile")=="true"
showProfiles=addon.getSetting("showProfiles")=="true"
forceView=addon.getSetting("forceView")=="true"
useUtility=addon.getSetting("useUtility")=="true"
username=addon.getSetting("username")
password=addon.getSetting("password")
viewIdVideos=addon.getSetting("viewIdVideos")
viewIdEpisodes=addon.getSetting("viewIdEpisodes")
osxBrowser=int(addon.getSetting("osxBrowser"))
language = ""
country = ""
if os.path.exists(localeFile):
    fh = open(localeFile, 'r')
    language = fh.read()
    fh.close()
    country = language.split("-")[1]
auth=""

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
userAgent = "Mozilla/5.0 (Windows NT 5.1; rv:25.0) Gecko/20100101 Firefox/25.0"
opener.addheaders = [('User-agent', userAgent)]

if not os.path.isdir(addonUserDataFolder):
    os.mkdir(addonUserDataFolder)
if not os.path.isdir(cacheFolder):
    os.mkdir(cacheFolder)
if not os.path.isdir(libraryFolder):
    os.mkdir(libraryFolder)
if not os.path.isdir(libraryFolderMovies):
    os.mkdir(libraryFolderMovies)
if not os.path.isdir(libraryFolderTV):
    os.mkdir(libraryFolderTV)
if os.path.exists(cookieFile):
    cj.load(cookieFile)
if os.path.exists(authFile):
    fh = open(authFile, 'r')
    auth = fh.read()
    fh.close()

while (username=="" or password==""):
    addon.openSettings()
    username=addon.getSetting("username")
    password=addon.getSetting("password")


def index():
    login()
    addDir(translation(30002), urlMain+"/MyList?leid=595&link=seeall", 'listVideos', "")
    addDir(translation(30003), urlMain+"/WiRecentAdditionsGallery?nRR=releaseDate&nRT=all&pn=1&np=1&actionMethod=json", 'listVideos', "")
    addDir(translation(30004), urlMain+"/WiHD?dev=PC&pn=1&np=1&actionMethod=json", 'listVideos', "")
    addDir(translation(30005), urlMain+"/WiGenre?agid=83&pn=1&np=1&actionMethod=json", 'listVideos', "")
    addDir(translation(30007), "WiGenre", 'listGenres', "")
    addDir(translation(30006), urlMain+"/WiGenre?agid=6839&pn=1&np=1&actionMethod=json", 'listVideos', "")
    addDir(translation(30009), "KidsAltGenre", 'listGenres', "")
    addDir(translation(30008), "", 'search', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideos(url):
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
            content = content.replace("\\n","").replace("\\","")
            match1 = re.compile('<span id="dbs(.+?)_.+?alt=".+?" src="(.+?)">', re.DOTALL).findall(content)
            match2 = re.compile('<span class="title "><a id="b(.+?)_', re.DOTALL).findall(content)
            if match1:
                for videoID, thumbUrl in match1:
                    listVideo(videoID, thumbUrl)
            elif match2:
                for videoID in match2:
                    listVideo(videoID, "")
            match = re.compile('&pn=(.+?)&', re.DOTALL).findall(url)
            if match:
                currentPage = match[0]
                nextPage = str(int(currentPage)+1)
                addDir(translation(30001), url.replace("&pn="+currentPage+"&","&pn="+nextPage+"&"), 'listVideos', "")
            if forceView:
                xbmc.executebuiltin('Container.SetViewMode('+viewIdVideos+')')
            xbmcplugin.endOfDirectory(pluginhandle)
    else:
        deleteCookies()
        xbmc.executebuiltin('XBMC.Notification(Info:,'+str(translation(30126))+',5000)')


def listVideo(videoID, thumbUrl):
    videoDetails = getVideoInfo(videoID).replace("\\n","").replace("\\","")
    match = re.compile('<span class="title ">(.+?)<\/span>', re.DOTALL).findall(videoDetails)
    title = match[0]
    match = re.compile('<span class="year">(.+?)<\/span>', re.DOTALL).findall(videoDetails)
    year = match[0]
    if not thumbUrl:
        match = re.compile('src="(.+?)"', re.DOTALL).findall(videoDetails)
        thumbUrl = match[0]
        #Modifying the id won't always work, please let me know if you know a better way
        #thumbID = str(int(thumbUrl.split("/")[-1].split(".")[0])+3)
    match = re.compile('<span class="mpaaRating.+?">(.+?)<\/span>', re.DOTALL).findall(videoDetails)
    mpaa = ""
    if match:
        mpaa = match[0]
    match = re.compile('<span class="duration">(.+?)<\/span>', re.DOTALL).findall(videoDetails)
    duration = match[0]
    if "Season" in duration or "Series" in duration or "Episodes" in duration or "Collections" in duration:
        videoType = "tv"
        duration = ""
    else:
        videoType = "movie"
        duration = duration.split(" ")[0]
    match = re.compile('src=".+?">.+?<\/span>(.+?)<', re.DOTALL).findall(videoDetails)
    desc = match[0].replace("&amp;","&")
    match = re.compile('Director:</dt><dd>(.+?)<', re.DOTALL).findall(videoDetails)
    director = ""
    if match:
        director = match[0].strip()
    match = re.compile('<span class="genre">(.+?)</span>', re.DOTALL).findall(videoDetails)
    genre = match[0]
    match = re.compile('<span class="rating">(.+?)</span>', re.DOTALL).findall(videoDetails)
    rating = "Rating: "+match[0]
    title = title.replace("&amp;","&")
    nextMode = "playVideo"
    if browseTvShows and videoType=="tv":
        nextMode = "listSeasons"
    if "/MyList" in url:
        addVideoDirR(title, videoID, nextMode, thumbUrl, videoType, rating+"\n\n"+desc, duration, year, mpaa, director, genre)
    else:
        addVideoDir(title, videoID, nextMode, thumbUrl, videoType, rating+"\n\n"+desc, duration, year, mpaa, director, genre)


def listGenres(type):
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    content = opener.open(urlMain+"/WiHome").read()
    match = re.compile('/'+type+'\\?agid=(.+?)">(.+?)</a></li>', re.DOTALL).findall(content)
    for genreID, title in match:
        addDir(title, urlMain+"/"+type+"?agid="+genreID+"&pn=1&np=1&actionMethod=json", 'listVideos', "")
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
    xbmcplugin.setContent(pluginhandle, "tvshows")
    content = getSeriesInfo(seriesID)
    content = json.loads(content)
    for test in content["episodes"]:
        for item in test:
            episodeSeason = str(item["season"])
            if episodeSeason==season:
                episodeID = str(item["episodeId"])
                episodeNr = str(item["episode"])
                episodeTitle = item["title"].encode('utf-8')
                duration = str(item["runtime"])
                desc = item["synopsis"].encode('utf-8')
                thumb = item["stills"][0]["url"]
                addEpisodeDir(episodeTitle, episodeID, 'playVideo', thumb, desc, duration, episodeNr)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIdEpisodes+')')
    xbmcplugin.endOfDirectory(pluginhandle)


def getVideoInfo(videoID):
    cacheFile = os.path.join(cacheFolder, videoID+".cache")
    if os.path.exists(cacheFile):
        fh = open(cacheFile, 'r')
        content = fh.read()
        fh.close()
    else:
        content = opener.open(urlMain+"/JSON/BOB?movieid="+videoID).read()
        fh = open(cacheFile, 'w')
        fh.write(content)
        fh.close()
    return content


def getSeriesInfo(seriesID):
    cacheFile = os.path.join(cacheFolder, seriesID+"_episodes.cache")
    if os.path.exists(cacheFile) and (time.time()-os.path.getmtime(cacheFile) < 60*5):
        fh = open(cacheFile, 'r')
        content = fh.read()
        fh.close()
    else:
        content = opener.open("http://api-global.netflix.com/desktop/odp/episodes?languages="+language+"&forceEpisodes=true&routing=redirect&video="+seriesID+"&country="+country).read()
        fh = open(cacheFile, 'w')
        fh.write(content)
        fh.close()
    return content


def playVideo(id):
    xbmc.Player().stop()
    if singleProfile:
        url = "http://movies.netflix.com/WiPlayer?movieid="+id
    else:
        token = ""
        if os.path.exists(profileFile):
            fh = open(profileFile, 'r')
            token = fh.read()
            fh.close()
        url = "https://movies.netflix.com/SwitchProfile?tkn="+token+"&nextpage="+urllib.quote_plus("http://movies.netflix.com/WiPlayer?movieid="+id)
    if osOsx and osxBrowser==1:
        subprocess.Popen('open -a "/Applications/Safari.app/" '+url, shell=True)
    else:
        xbmc.executebuiltin("RunPlugin(plugin://plugin.program.chrome.launcher/?url="+urllib.quote_plus(url)+"&mode=showSite)")
    if osWin:
        subprocess.Popen(utilityPath, shell=False)


def configureUtility():
    if osWin:
        subprocess.Popen(utilityPath+" yes", shell=False)
    elif osLinux:
        subprocess.Popen('wine "'+utilityPath+'" yes', shell=True)


def deleteCookies():
    if os.path.exists(cookieFile):
        os.remove(cookieFile)


def search():
    keyboard = xbmc.Keyboard('', translation(30008))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText().replace(" ", "+")
        listVideos(urlMain+"/WiSearch?v1="+search_string)


def addToQueue(id):
    opener.open("http://movies.netflix.com/AddToQueue?movieid="+id+"&authURL="+auth)


def removeFromQueue(id):
    opener.open("http://movies.netflix.com/QueueDelete?movieid="+id+"&authURL="+auth)
    xbmc.executebuiltin("Container.Refresh")


def login():
    content = opener.open("http://movies.netflix.com/").read()
    if not "Sorry, Netflix is not available in your country yet." in content and not "Sorry, Netflix hasn't come to this part of the world yet" in content:
        match = re.compile('id="signout".+?authURL=(.+?)"', re.DOTALL).findall(content)
        if match:
            fh = open(authFile, 'w')
            fh.write(match[0])
            fh.close()
        match = re.compile('"LOCALE":"(.+?)"', re.DOTALL).findall(content)
        localeT = match[0]
        fh = open(localeFile, 'w')
        fh.write(localeT)
        fh.close()
        if 'id="page-LOGIN"' in content:
            match = re.compile('name="authURL" value="(.+?)"', re.DOTALL).findall(content)
            authUrl = match[0]
            fh = open(authFile, 'w')
            fh.write(authUrl)
            fh.close()
            opener.open("https://signup.netflix.com/Login", "authURL="+authUrl+"&email="+username+"&password="+password+"&RememberMe=on")
            cj.save(cookieFile)
        if not os.path.exists(profileFile) and not singleProfile:
            chooseProfile()
        elif not singleProfile and showProfiles:
            chooseProfile()
    else:
        xbmc.executebuiltin('XBMC.Notification(Info:,'+str(translation(30126))+',5000)')


def setProfile():
    fh = open(profileFile, 'r')
    token = fh.read()
    fh.close()
    opener.open("https://movies.netflix.com/ProfilesGate?nextpage=http%3A%2F%2Fmovies.netflix.com%2FDefault")
    opener.open("https://api-global.netflix.com/desktop/account/profiles/switch?switchProfileGuid="+token)


def chooseProfile():
    content = opener.open("https://movies.netflix.com/ProfilesGate?nextpage=http%3A%2F%2Fmovies.netflix.com%2FDefault").read()
    match = re.compile('"profileName":"(.+?)".+?token":"(.+?)"', re.DOTALL).findall(content)
    profiles = []
    tokens = []
    for p, t in match:
        profiles.append(p)
        tokens.append(t)
    dialog = xbmcgui.Dialog()
    nr=dialog.select(translation(30113), profiles)
    if nr>=0:
      token=tokens[nr]
      #Profile selection isn't remembered, so it has to be executed before every requests (setProfile)
      #If you know a solution for this, please let me know
      #opener.open("https://api-global.netflix.com/desktop/account/profiles/switch?switchProfileGuid="+token)
      fh = open(profileFile, 'w')
      fh.write(token)
      fh.close()
      cj.save(cookieFile)


def forceChooseProfile():
    addon.setSetting("singleProfile", "false")
    xbmc.executebuiltin('XBMC.Notification(Info:,'+str(translation(30111))+',5000)')
    chooseProfile()


def addMovieToLibrary(movieID, title):
    movieFolderName = (''.join(c for c in unicode(title, 'utf-8') if c not in '/\\:?"*|<>')).strip()
    dir = os.path.join(libraryFolderMovies, movieFolderName)
    if not os.path.isdir(dir):
        os.mkdir(dir)
        fh = open(os.path.join(dir, "movie.strm"), 'w')
        fh.write("plugin://plugin.video.netflixbmc/?mode=playVideo&url="+movieID)
        fh.close()
    if updateDB:
        xbmc.executebuiltin('UpdateLibrary(video)')


def addSeriesToLibrary(seriesID, seriesTitle, season):
    seriesFolderName = (''.join(c for c in unicode(seriesTitle, 'utf-8') if c not in '/\\:?"*|<>')).strip()
    seriesDir = os.path.join(libraryFolderTV, seriesFolderName)
    if not os.path.isdir(seriesDir):
        os.mkdir(seriesDir)
    content = getSeriesInfo(seriesID)
    content = json.loads(content)  
    for test in content["episodes"]:
        for item in test:
            episodeSeason = str(item["season"])
            seasonCheck = True
            if season:
                seasonCheck = episodeSeason==season
            if seasonCheck:
                seasonDir = os.path.join(seriesDir, "Season "+episodeSeason)
                if not os.path.isdir(seasonDir):
                    os.mkdir(seasonDir)
                episodeID = str(item["episodeId"])
                episodeNr = str(item["episode"])
                episodeTitle = item["title"].encode('utf-8')
                if len(episodeNr)==1:
                    episodeNr = "0"+episodeNr
                seasonNr = episodeSeason
                if len(seasonNr)==1:
                    seasonNr = "0"+seasonNr
                filename = "S"+seasonNr+"E"+episodeNr+" - "+episodeTitle+".strm"
                filename = (''.join(c for c in unicode(filename, 'utf-8') if c not in '/\\:?"*|<>')).strip()
                fh = open(os.path.join(seasonDir, filename), 'w')
                fh.write("plugin://plugin.video.netflixbmc/?mode=playVideo&url="+episodeID)
                fh.close()
    if updateDB:
        xbmc.executebuiltin('UpdateLibrary(video)')


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


def addDir(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&thumb="+str(iconimage)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name})
    entries = []
    if not singleProfile:
        entries.append((translation(30110), 'RunPlugin(plugin://plugin.video.netflixbmc/?mode=chooseProfile)',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addVideoDir(name, url, mode, iconimage, videoType="", desc="", duration="", year="", mpaa="", director="", genre=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+str(name)+"&thumb="+urllib.quote_plus(iconimage)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name, "plot": desc, "duration": duration, "year": year, "mpaa": mpaa, "director": director, "genre": genre})
    entries = []
    entries.append((translation(30114), 'RunPlugin(plugin://plugin.video.netflixbmc/?mode=addToQueue&url='+urllib.quote_plus(url)+')',))
    if videoType=="tv":
        entries.append((translation(30122), 'RunPlugin(plugin://plugin.video.netflixbmc/?mode=addSeriesToLibrary&url=&name='+str(name)+'&seriesID='+str(url)+')',))
        if browseTvShows:
            entries.append((translation(30121), 'Container.Update(plugin://plugin.video.netflixbmc/?mode=playVideo&url='+urllib.quote_plus(url)+'&thumb='+urllib.quote_plus(iconimage)+')',))
        else:
            entries.append((translation(30118), 'Container.Update(plugin://plugin.video.netflixbmc/?mode=listSeasons&url='+urllib.quote_plus(url)+'&thumb='+urllib.quote_plus(iconimage)+')',))
    elif videoType=="movie":
        entries.append((translation(30122), 'RunPlugin(plugin://plugin.video.netflixbmc/?mode=addMovieToLibrary&url='+urllib.quote_plus(url)+'&name='+str(name+' ('+year+')')+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addVideoDirR(name, url, mode, iconimage, videoType="", desc="", duration="", year="", mpaa="", director="", genre=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+str(name)+"&thumb="+urllib.quote_plus(iconimage)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name, "plot": desc, "duration": duration, "year": year, "mpaa": mpaa, "director": director, "genre": genre})
    entries = []
    entries.append((translation(30115), 'RunPlugin(plugin://plugin.video.netflixbmc/?mode=removeFromQueue&url='+urllib.quote_plus(url)+')',))
    if videoType=="tv":
        entries.append((translation(30122), 'RunPlugin(plugin://plugin.video.netflixbmc/?mode=addSeriesToLibrary&url=&name='+str(name)+'&seriesID='+str(url)+')',))
        if browseTvShows:
            entries.append((translation(30121), 'Container.Update(plugin://plugin.video.netflixbmc/?mode=playVideo&url='+urllib.quote_plus(url)+'&thumb='+urllib.quote_plus(iconimage)+')',))
        else:
            entries.append((translation(30118), 'Container.Update(plugin://plugin.video.netflixbmc/?mode=listSeasons&url='+urllib.quote_plus(url)+'&thumb='+urllib.quote_plus(iconimage)+')',))
    elif videoType=="movie":
        entries.append((translation(30122), 'RunPlugin(plugin://plugin.video.netflixbmc/?mode=addMovieToLibrary&url='+urllib.quote_plus(url)+'&name='+str(name+' ('+year+')')+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addSeasonDir(name, url, mode, iconimage, seriesName, seriesID):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&seriesID="+str(seriesID)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name})
    entries = []
    entries.append((translation(30122), 'RunPlugin(plugin://plugin.video.netflixbmc/?mode=addSeriesToLibrary&url='+urllib.quote_plus(url)+'&name='+str(seriesName)+'&seriesID='+str(seriesID)+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addEpisodeDir(name, url, mode, iconimage, desc="", duration="", episodeNr=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name, "plot": desc, "duration": duration, "episode": episodeNr})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))
name = urllib.unquote_plus(params.get('name', ''))
season = urllib.unquote_plus(params.get('season', ''))
seriesID = urllib.unquote_plus(params.get('seriesID', ''))

if mode == 'listQueue':
    listQueue()
elif mode == 'listVideos':
    listVideos(url)
elif mode == 'addToQueue':
    addToQueue(url)
elif mode == 'removeFromQueue':
    removeFromQueue(url)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'search':
    search()
elif mode == 'login':
    login()
elif mode == 'chooseProfile':
    chooseProfile()
elif mode == 'listGenres':
    listGenres(url)
elif mode == 'listSeasons':
    listSeasons(name, url, thumb)
elif mode == 'listEpisodes':
    listEpisodes(seriesID, url)
elif mode == 'configureUtility':
    configureUtility()
elif mode == 'deleteCookies':
    deleteCookies()
elif mode == 'addMovieToLibrary':
    addMovieToLibrary(url, name)
elif mode == 'addSeriesToLibrary':
    addSeriesToLibrary(seriesID, name, url)
else:
    index()
