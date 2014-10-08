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
itunesShowSubGenres = addon.getSetting("itunesShowSubGenres") == "true"
itunesForceCountry = addon.getSetting("itunesForceCountry") == "true"
itunesCountry = addon.getSetting("itunesCountry")
spotifyForceCountry = addon.getSetting("spotifyForceCountry") == "true"
spotifyCountry = addon.getSetting("spotifyCountry")
userAgent = "Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0"
opener.addheaders = [('User-Agent', userAgent)]
urlMain = "http://www.billboard.com"
if itunesForceCountry and itunesCountry:
    iTunesRegion = itunesCountry
else:
    iTunesRegion = region
if spotifyForceCountry and spotifyCountry:
    spotifyRegion = spotifyCountry
else:
    spotifyRegion = region

if not os.path.isdir(addonUserDataFolder):
    os.mkdir(addonUserDataFolder)
if not cacheDir.startswith(('smb://', 'nfs://', 'upnp://', 'ftp://')) and not os.path.isdir(cacheDir):
    os.mkdir(cacheDir)


def index():
    addDir(translation(30002), "", "billboardMain", "")
    addDir(translation(30043), "", "itunesMain", "")
    addDir(translation(30044), "", "spotifyMain", "")
    xbmcplugin.endOfDirectory(pluginhandle)


def spotifyMain():
    addDir(translation(30041), "http://api.tunigo.com/v3/space/toplists?region="+spotifyRegion+"&page=0&per_page=50&platform=web", "listSpotifyPlaylists", "")
    addDir(translation(30042), "http://api.tunigo.com/v3/space/featured-playlists?region="+spotifyRegion+"&page=0&per_page=50&dt="+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M").replace(":","%3A")+"%3A00&platform=web", "listSpotifyPlaylists", "")
    addDir(translation(30006), "http://api.tunigo.com/v3/space/genres?region="+spotifyRegion+"&per_page=1000&platform=web", "listSpotifyGenres", "")
    xbmcplugin.endOfDirectory(pluginhandle)


def itunesMain():
    content = cache("https://itunes.apple.com/"+iTunesRegion+"/genre/music/id34", 30)
    content = content[content.find('id="genre-nav"'):]
    content = content[:content.find('</div>')]
    match=re.compile('<li><a href="https://itunes.apple.com/.+?/genre/.+?/id(.+?)"(.+?)title=".+?">(.+?)<', re.DOTALL).findall(content)
    title = "All Genres"
    if itunesShowSubGenres:
        title = '[B]'+title+'[/B]'
    addAutoPlayDir(title, "0", "listItunesVideos", "", "", "browse")
    for genreID, type, title in match:
        title = cleanTitle(title)
        if 'class="top-level-genre"' in type:
            if itunesShowSubGenres:
                title = '[B]'+title+'[/B]'
            addAutoPlayDir(title, genreID, "listItunesVideos", "", "", "browse")
        elif itunesShowSubGenres:
            title = '   '+title
            addAutoPlayDir(title, genreID, "listItunesVideos", "", "", "browse")
    xbmcplugin.endOfDirectory(pluginhandle)


def billboardMain():
    addAutoPlayDir(translation(30005), urlMain+"/rss/charts/hot-100", "listBillboardCharts", "", "", "browse")
    addAutoPlayDir("Trending 140", "Top 140 in Trending", "listBillboardChartsNew", "", "", "browse")
    addAutoPlayDir("Last 24 Hours", "Top 140 in Overall", "listBillboardChartsNew", "", "", "browse")
    addDir(translation(30006), "genre", "listBillboardChartsTypes", "", "", "browse")
    addDir(translation(30007), "country", "listBillboardChartsTypes", "", "", "browse")
    addDir(translation(30008), "other", "listBillboardChartsTypes", "", "", "browse")
    xbmcplugin.endOfDirectory(pluginhandle)


def listBillboardChartsTypes(type):
    if type=="genre":
        addAutoPlayDir(translation(30009), urlMain+"/rss/charts/pop-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30010), urlMain+"/rss/charts/rock-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30011), urlMain+"/rss/charts/alternative-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30012), urlMain+"/rss/charts/r-b-hip-hop-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30013), urlMain+"/rss/charts/r-and-b-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30014), urlMain+"/rss/charts/rap-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30015), urlMain+"/rss/charts/country-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30016), urlMain+"/rss/charts/latin-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30017), urlMain+"/rss/charts/jazz-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30018), urlMain+"/rss/charts/dance-club-play-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30019), urlMain+"/rss/charts/dance-electronic-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30020), urlMain+"/rss/charts/heatseekers-songs", "listBillboardCharts", "", "", "browse")
    elif type=="country":
        addAutoPlayDir(translation(30021), urlMain+"/rss/charts/canadian-hot-100", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30022), urlMain+"/rss/charts/k-pop-hot-100", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30023), urlMain+"/rss/charts/japan-hot-100", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30024), urlMain+"/rss/charts/germany-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30025), urlMain+"/rss/charts/france-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30026), urlMain+"/rss/charts/united-kingdom-songs", "listBillboardCharts", "", "", "browse")
    elif type=="other":
        addAutoPlayDir(translation(30028), urlMain+"/rss/charts/radio-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30029), urlMain+"/rss/charts/digital-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30030), urlMain+"/rss/charts/streaming-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30031), urlMain+"/rss/charts/on-demand-songs", "listBillboardCharts", "", "", "browse")
    xbmcplugin.endOfDirectory(pluginhandle)


def listSpotifyGenres(url):
    content = cache(url, 30)
    content = json.loads(content)
    for item in content['items']:
        genreID = item['genre']['templateName']
        try:
            thumb = item['genre']['iconImageUrl']
        except:
            thumb = ""
        title = item['genre']['name'].encode('utf-8')
        if title.strip().lower()!="top lists":
            addDir(title, "http://api.tunigo.com/v3/space/"+genreID+"?region="+spotifyRegion+"&page=0&per_page=50&platform=web", "listSpotifyPlaylists", thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIDGenres+')')


def listSpotifyPlaylists(url):
    content = cache(url, 1)
    content = json.loads(content)
    for item in content['items']:
        uri = item['playlist']['uri'].encode('utf-8')
        try:
            thumb = "http://d3rt1990lpmkn.cloudfront.net/300/"+item['playlist']['image']
        except:
            thumb = ""
        title = item['playlist']['title'].encode('utf-8')
        description = item['playlist']['description'].encode('utf-8')
        addAutoPlayDir(title, uri, "listSpotifyVideos", thumb, description, "browse")
    match=re.compile('page=(.+?)&per_page=(.+?)&', re.DOTALL).findall(url)
    currentPage = int(match[0][0])
    perPage = int(match[0][1])
    nextPage = currentPage+1
    if nextPage*perPage<content['totalItems']:
        addDir(translation(30001), url.replace("page="+str(currentPage),"page="+str(nextPage)), "listSpotifyPlaylists", "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIDPlaylists+')')


def listSpotifyVideos(type, url, limit):
    if type=="play":
        musicVideos = []
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
    content = cache("https://embed.spotify.com/?uri="+url, 1)
    spl=content.split('music-paused item')
    pos = 1
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
        if type=="browse":
            addLink(title, title.replace(" - ", " "), "playYTByTitle", thumb)
        else:
            if xbox:
                url = "plugin://video/Youtube Music/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=autoPlayYTByTitle"
            else:
                url = "plugin://"+addonID+"/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=autoPlayYTByTitle"
            musicVideos.append([title, url, thumb])
            if limit and int(limit)==pos:
                break
            pos+=1
    if type=="browse":
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceView:
            xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')
    else:
        random.shuffle(musicVideos)
        for title, url, thumb in musicVideos:
            listitem = xbmcgui.ListItem(title, thumbnailImage=thumb)
            playlist.add(url, listitem)
        xbmc.Player().play(playlist)


def listItunesVideos(type, genreID, limit):
    if type=="play":
        musicVideos = []
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
    url = "https://itunes.apple.com/"+region+"/rss/topsongs/limit=100"
    if genreID!="0":
        url += "/genre="+genreID
    url += "/explicit=true/xml"
    content = cache(url, 1)
    spl=content.split('<entry>')
    pos = 1
    for i in range(1,len(spl),1):
        entry=spl[i]
        match=re.compile('<im:artist href=".*?">(.+?)</im:artist>', re.DOTALL).findall(entry)
        artist=match[0]
        match=re.compile('<im:name>(.+?)</im:name>', re.DOTALL).findall(entry)
        videoTitle=match[0]
        if " (" in videoTitle:
            videoTitle=videoTitle[:videoTitle.rfind(" (")]
        title=cleanTitle(artist+" - "+videoTitle)
        match=re.compile('<im:image height="170">(.+?)</im:image>', re.DOTALL).findall(entry)
        thumb=match[0].replace("170x170-75.jpg","400x400-75.jpg")
        filtered = False
        for entry2 in blacklist:
            if entry2.strip().lower() and entry2.strip().lower() in title.lower():
                filtered = True
        if filtered:
            continue
        if type=="browse":
            addLink(title, title.replace(" - ", " "), "playYTByTitle", thumb)
        else:
            if xbox:
                url = "plugin://video/Youtube Music/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=autoPlayYTByTitle"
            else:
                url = "plugin://"+addonID+"/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=autoPlayYTByTitle"
            musicVideos.append([title, url, thumb])
            if limit and int(limit)==pos:
                break
            pos+=1
    if type=="browse":
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceView:
            xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')
    else:
        random.shuffle(musicVideos)
        for title, url, thumb in musicVideos:
            listitem = xbmcgui.ListItem(title, thumbnailImage=thumb)
            playlist.add(url, listitem)
        xbmc.Player().play(playlist)

        
def listBillboardCharts(type, url, limit):
    if type=="play":
        musicVideos = []
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
    content = cache(url, 1)
    match = re.compile('<item>.+?<artist>(.+?)</artist>.+?<chart_item_title>(.+?)</chart_item_title>', re.DOTALL).findall(content)
    pos = 1
    for artist, title in match:
        title = cleanTitle(artist+" - "+title[title.find(":")+1:]).replace("Featuring", "Feat.")
        if type=="browse":
            addLink(title, title.replace(" - ", " "), "playYTByTitle", "")
        else:
            if xbox:
                url = "plugin://video/Youtube Music/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=autoPlayYTByTitle"
            else:
                url = "plugin://"+addonID+"/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=autoPlayYTByTitle"
            musicVideos.append([title, url, ""])
            if limit and int(limit)==pos:
                break
            pos+=1
    if type=="browse":
        xbmcplugin.endOfDirectory(pluginhandle)
    else:
        random.shuffle(musicVideos)
        for title, url, thumb in musicVideos:
            listitem = xbmcgui.ListItem(title, thumbnailImage=thumb)
            playlist.add(url, listitem)
        xbmc.Player().play(playlist)


def listBillboardChartsNew(type, url, limit):
    if type=="play":
        musicVideos = []
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
    content = opener.open("http://realtime.billboard.com/").read()
    content = content[content.find("<h1>"+url+"</h1>"):]
    content = content[:content.find("</table>")]
    match = re.compile('<tr>.*?<td>(.+?)</td>.*?<td><a href=".*?">(.+?)</a></td>.*?<td>(.+?)</td>.*?<td>(.+?)</td>.*?</tr>', re.DOTALL).findall(content)
    pos = 1
    for nr, artist, title, rating in match:
        if "(" in title:
            title = title[:title.find("(")].strip()
        title = cleanTitle(artist+" - "+title).replace("Featuring", "Feat.")
        if type=="browse":
            addLink(title, title.replace(" - ", " "), "playYTByTitle", "")
        else:
            if xbox:
                url = "plugin://video/Youtube Music/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=autoPlayYTByTitle"
            else:
                url = "plugin://"+addonID+"/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=autoPlayYTByTitle"
            musicVideos.append([title, url, ""])
            if limit and int(limit)==pos:
                break
            pos+=1
    if type=="browse":
        xbmcplugin.endOfDirectory(pluginhandle)
    else:
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
    except:
        pass


def autoPlayYTByTitle(title):
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


def queueVideo(url, name):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name)
    playlist.add(url, listitem)        


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
    liz = xbmcgui.ListItem(name, iconImage="DefaultAudio.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.setProperty('IsPlayable', 'true')
    entries = []
    entries.append((translation(30004), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+urllib.quote_plus(name)+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok

def addDir(name, url, mode, iconimage="", description="", type="", limit=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&type="+str(type)+"&limit="+str(limit)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultMusicVideos.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

def addAutoPlayDir(name, url, mode, iconimage="", description="", type="", limit=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&type="+str(type)+"&limit="+str(limit)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultMusicVideos.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
    entries = []
    entries.append(("Autoplay All", 'RunPlugin(plugin://'+addonID+'/?mode='+str(mode)+'&url='+urllib.quote_plus(url)+'&type=play&limit=)',))
    entries.append(("Autoplay Top10", 'RunPlugin(plugin://'+addonID+'/?mode='+str(mode)+'&url='+urllib.quote_plus(url)+'&type=play&limit=10)',))
    entries.append(("Autoplay Top20", 'RunPlugin(plugin://'+addonID+'/?mode='+str(mode)+'&url='+urllib.quote_plus(url)+'&type=play&limit=20)',))
    entries.append(("Autoplay Top30", 'RunPlugin(plugin://'+addonID+'/?mode='+str(mode)+'&url='+urllib.quote_plus(url)+'&type=play&limit=30)',))
    entries.append(("Autoplay Top40", 'RunPlugin(plugin://'+addonID+'/?mode='+str(mode)+'&url='+urllib.quote_plus(url)+'&type=play&limit=40)',))
    entries.append(("Autoplay Top50", 'RunPlugin(plugin://'+addonID+'/?mode='+str(mode)+'&url='+urllib.quote_plus(url)+'&type=play&limit=50)',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
type = urllib.unquote_plus(params.get('type', ''))
limit = urllib.unquote_plus(params.get('limit', ''))
chartTitle = urllib.unquote_plus(params.get('chartTitle', ''))

if mode == 'playYTByTitle':
    playYTByTitle(url)
elif mode == 'autoPlayYTByTitle':
    autoPlayYTByTitle(url)
elif mode == 'spotifyMain':
    spotifyMain()
elif mode == 'itunesMain':
    itunesMain()
elif mode == 'billboardMain':
    billboardMain()
elif mode == 'listSpotifyGenres':
    listSpotifyGenres(url)
elif mode == 'listSpotifyPlaylists':
    listSpotifyPlaylists(url)
elif mode == 'listSpotifyVideos':
    listSpotifyVideos(type, url, limit)
elif mode == 'playSpotifyVideos':
    playSpotifyVideos(url)
elif mode == 'listItunesVideos':
    listItunesVideos(type, url, limit)
elif mode == 'playItunesVideos':
    playItunesVideos(url)
elif mode == 'listBillboardCharts':
    listBillboardCharts(type, url, limit)
elif mode == 'listBillboardChartsNew':
    listBillboardChartsNew(type, url, limit)
elif mode == 'listBillboardChartsTypes':
    listBillboardChartsTypes(url)
elif mode == 'queueVideo':
    queueVideo(url, name)
else:
    index()
