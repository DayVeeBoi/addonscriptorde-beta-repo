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
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs
import time

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.my_music_tv'
addon = xbmcaddon.Addon(id=addonID)
pluginhandle = int(sys.argv[1])
socket.setdefaulttimeout(30)
opener = urllib2.build_opener()
openerR = urllib2.build_opener()
xbox = xbmc.getCondVisibility("System.Platform.xbox")
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
addonUserDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
blacklistFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/blacklist")
playlistDir = xbmc.translatePath(addon.getSetting("playlistDir"))
channelDir = xbmc.translatePath(addon.getSetting("channelDir"))
historyDir = xbmc.translatePath(addon.getSetting("historyDir"))
cacheDir = xbmc.translatePath(addon.getSetting("cacheDir"))
plistDir = os.path.join(cacheDir, "plist")
blacklist = addon.getSetting("blacklist").split(',')
infoEnabled = addon.getSetting("showInfo") == "true"
infoType = addon.getSetting("infoType")
infoDelay = int(addon.getSetting("infoDelay"))
infoDuration = int(addon.getSetting("infoDuration"))
resolutionVevo = addon.getSetting("resolutionVevo")
resolutionVevo = ["640x360", "960x540", "1280x720", "1920x1080"][int(resolutionVevo)]
cdnVevo = addon.getSetting("cdnVevo")
cdnVevo = ["hls-aws", "hls-aka", "hls-lvl3"][int(cdnVevo)]
resolutionMuzu = addon.getSetting("resolutionMuzu")
resolutionMuzu = [360, 480, 720, 1080][int(resolutionMuzu)]
resolutionDM = addon.getSetting("resolutionDM")
resolutionDM = ["480p", "720p", "1080p"][int(resolutionDM)]
userAgent = "Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0"
opener.addheaders = [('User-Agent', userAgent)]
userAgentR = "XBMC | "+addonID+" | "+addon.getAddonInfo('version')
openerR.addheaders = [('User-Agent', userAgentR)]

if not os.path.isdir(addonUserDataFolder):
    os.mkdir(addonUserDataFolder)
if not channelDir.startswith(('smb://', 'nfs://', 'upnp://', 'ftp://')) and not os.path.isdir(channelDir):
    os.mkdir(channelDir)
if not playlistDir.startswith(('smb://', 'nfs://', 'upnp://', 'ftp://')) and not os.path.isdir(playlistDir):
    os.mkdir(playlistDir)
if not historyDir.startswith(('smb://', 'nfs://', 'upnp://', 'ftp://')) and not os.path.isdir(historyDir):
    os.mkdir(historyDir)
if not cacheDir.startswith(('smb://', 'nfs://', 'upnp://', 'ftp://')) and not os.path.isdir(cacheDir):
    os.mkdir(cacheDir)
if not plistDir.startswith(('smb://', 'nfs://', 'upnp://', 'ftp://')) and not os.path.isdir(plistDir):
    os.mkdir(plistDir)


def index():
    dirs, files = xbmcvfs.listdir(channelDir)
    if files:
        for file in files:
            fh = xbmcvfs.File(os.path.join(channelDir, file), 'r')
            content = fh.read()
            fh.close()
            match=re.compile('thumb="(.*?)"', re.DOTALL).findall(content)
            thumb=""
            if match:
                thumb=match[0]
            fileTitle = file
            if "." in fileTitle:
                fileTitle = fileTitle[:fileTitle.rfind(".")]
            addDir(fileTitle, file, 'playChannel', thumb)
    else:
        addDir(translation(30001)+"...", "", 'none', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def playChannel(filename):
    addon.setSetting("currentChannel", filename)
    historyFile = os.path.join(historyDir, filename+".history")
    fh = xbmcvfs.File(historyFile, 'r')
    historyContent = fh.read()
    fh.close()
    filename = os.path.join(channelDir, filename)
    musicVideos = []
    dupeList = []
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    fh = xbmcvfs.File(filename, 'r')
    contentMain = fh.read()
    fh.close()
    match=re.compile('shuffled="(.+?)"', re.DOTALL).findall(contentMain)
    shuffled=True
    if match:
        shuffled=match[0]=="yes"
    match=re.compile('unwatched="(.+?)"', re.DOTALL).findall(contentMain)
    unwatched=False
    if match:
        unwatched=match[0]=="yes"
    splMain=contentMain.split('<entry')
    for i in range(1,len(splMain),1):
        entry=splMain[i]
        match=re.compile('type="(.+?)"', re.DOTALL).findall(entry)
        type=match[0]
        match=re.compile('value="(.+?)"', re.DOTALL).findall(entry)
        value=match[0]
        match=re.compile('limit="(.+?)"', re.DOTALL).findall(entry)
        limit = -1
        if match:
            limit=int(match[0])
        match=re.compile('cache="(.+?)"', re.DOTALL).findall(entry)
        cacheDuration = -1
        if match:
            cacheDuration=int(match[0])
        pos = 1
        if type.lower()=="folder":
            videoDir = value
            fileTypes = ('.mkv', '.avi', '.mp4', '.wmv', '.flv', '.mpg', '.mpeg', '.mov', '.ts', '.m2ts', '.m4v', '.m2v', '.rm', '.amv', '.divx')
            if videoDir.startswith(('smb://', 'nfs://', 'upnp://', 'ftp://')):
                dirs, files = xbmcvfs.listdir(videoDir)
                for file in files:
                    if file.lower().endswith(fileTypes):
                        musicVideos.append([file, os.path.join(videoDir, file), ""])
                for dir in dirs:
                    dirs2, files = xbmcvfs.listdir(os.path.join(videoDir, dir))
                    for file in files:
                        if file.lower().endswith(fileTypes):
                            title = file[:file.rfind(".")]
                            filtered = False
                            for entry2 in blacklist:
                                if entry2.strip().lower() and entry2.strip().lower() in title.lower():
                                    filtered = True
                            if filtered:
                                continue
                            if xbox:
                                url = "plugin://video/My Music TV/?url="+urllib.quote_plus(os.path.join(videoDir, os.path.join(dir, file)))+"&mode=playUrl"
                            else:
                                url = "plugin://"+addonID+"/?url="+urllib.quote_plus(os.path.join(videoDir, os.path.join(dir, file)))+"&mode=playUrl"
                            if ((not unwatched) or unwatched and not url in historyContent) and not title in dupeList and not blacklistContains(url):
                                musicVideos.append([title, url, ""])
                                dupeList.append(title)
                            if limit==pos:
                                break
                            pos+=1
            else:
                for root, dirs, files in os.walk(videoDir):
                    for file in files:
                        if file.lower().endswith(fileTypes):
                            title = file[:file.rfind(".")]
                            filtered = False
                            for entry2 in blacklist:
                                if entry2.strip().lower() and entry2.strip().lower() in title.lower():
                                    filtered = True
                            if filtered:
                                continue
                            if xbox:
                                url = "plugin://video/My Music TV/?url="+urllib.quote_plus(os.path.join(root, file))+"&mode=playUrl"
                            else:
                                url = "plugin://"+addonID+"/?url="+urllib.quote_plus(os.path.join(root, file))+"&mode=playUrl"
                            if ((not unwatched) or unwatched and not url in historyContent) and not title in dupeList and not blacklistContains(url):
                                musicVideos.append([title, url, ""])
                                dupeList.append(title)
                            if limit==pos:
                                break
                            pos+=1
        elif type.lower()=="xsp":
            result = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": { "directory": "'+value+'", "media": "video" },  "id": 1}')
            content = json.loads(result)
            for item in content["result"]["files"]:
                title = item["label"].encode('utf-8')
                url = item["file"]
                thumb = ""
                filtered = False
                for entry2 in blacklist:
                    if entry2.strip().lower() and entry2.strip().lower() in title.lower():
                        filtered = True
                if filtered:
                    continue
                if ((not unwatched) or unwatched and not url in historyContent) and not title in dupeList and not blacklistContains(url):
                    musicVideos.append([title, url, thumb])
                    dupeList.append(title)
                if limit==pos:
                    break
                pos+=1
        elif type.lower()=="xspf":
            fh=xbmcvfs.File(os.path.join(playlistDir, value), 'r')
            content=fh.read()
            fh.close()
            spl=content.split('<track>')
            for i in range(1,len(spl),1):
                entry=spl[i]
                match=re.compile('<title>(.+?)</title>', re.DOTALL).findall(entry)
                title=match[0].replace("&quot;", "&")
                match=re.compile('<location>(.+?)</location>', re.DOTALL).findall(entry)
                url=match[0].replace("&quot;", "&")
                match=re.compile('<image>(.+?)</image>', re.DOTALL).findall(entry)
                thumb=match[0].replace("&quot;", "&")
                filtered = False
                for entry2 in blacklist:
                    if entry2.strip().lower() and entry2.strip().lower() in title.lower():
                        filtered = True
                if filtered:
                    continue
                if ((not unwatched) or unwatched and not url in historyContent) and not title in dupeList and not blacklistContains(url):
                    musicVideos.append([title, url, thumb])
                    dupeList.append(title)
                if limit==pos:
                    break
                pos+=1
        elif type.lower().startswith("vevo:"):
            vevoType = type.lower().split(":")[1]
            if vevoType=="playlist":
                if cacheDuration==-1:
                    cacheDuration=7
                content = cache("http://api.vevo.com/mobile/v2/playlist/"+value+".json", cacheDuration)
            elif vevoType=="artist":
                if cacheDuration==-1:
                    cacheDuration=30
                content = cache("http://api.vevo.com/mobile/v1/artist/"+value+"/videos.json?order=MostViewedToday&offset=0&max=200", cacheDuration)
            elif vevoType=="charts" or vevoType=="livecharts":
                if cacheDuration==-1:
                    cacheDuration=7
                vevoValues = value.split(":")
                genreValue = vevoValues[0]
                orderValue = vevoValues[1]
                genres = ""
                if genreValue != "all":
                    genres = "genres="+genreValue+"&"
                isLive = ""
                if vevoType=="livecharts":
                    isLive = "&islive=true"
                content = cache("http://api.vevo.com/mobile/v1/video/list.json?"+genres+"order="+orderValue+"&offset=0&max=200"+isLive, cacheDuration)
            content = json.loads(content)
            try:
                content = content["result"]["videos"]
            except:
                content = content["result"]
            for item in content:
                artist = item["artists_main"][0]["name"].encode('utf-8')
                title = item["title"].encode('utf-8')
                filtered = False
                for entry2 in blacklist:
                    if entry2.strip().lower() and entry2.lower() in artist.lower():
                        filtered = True
                if filtered:
                    continue
                if vevoType=="artist" and ("(Audio" in title or "(Revised" in title or "(Teaser" in title or "(Behind The Scenes" in title or "(Lyric" in title or "(VEVO LIFT" in title):
                    continue
                title = artist+" - "+title
                thumb = item["image_url"].encode('utf-8')
                if xbox:
                    url = "plugin://video/My Music TV/?url="+item["isrc"]+"&mode=playVevo"
                else:
                    url = "plugin://"+addonID+"/?url="+item["isrc"]+"&mode=playVevo"
                if ((not unwatched) or unwatched and not url in historyContent) and not title in dupeList and not blacklistContains(url):
                    musicVideos.append([title, url, thumb])
                    dupeList.append(title)
                if limit==pos:
                    break
                pos+=1
        elif type.lower().startswith("muzu:"):
            if cacheDuration==-1:
                cacheDuration=7
            muzuType = type.lower().split(":")[1]
            muzuValues = value.split(":")
            content = cache("http://www.muzu.tv/"+muzuType+"/"+muzuValues[0]+"/playlists/playlist/"+muzuValues[1]+"/", cacheDuration)
            spl=content.split('id="listItem-')
            for i in range(1,len(spl),1):
                entry=spl[i]
                match=re.compile('data-id="(.+?)"', re.DOTALL).findall(entry)
                videoID=match[0]
                match=re.compile('alt="(.+?)"', re.DOTALL).findall(entry)
                title=cleanTitle(match[0])
                match=re.compile('src="(.+?)"', re.DOTALL).findall(entry)
                thumb=match[0].replace("-thb1","-thb2")
                filtered = False
                for entry2 in blacklist:
                    if entry2.strip().lower() and entry2.lower() in artist.lower():
                        filtered = True
                if filtered:
                    continue
                if xbox:
                    url = "plugin://video/My Music TV/?url="+videoID+"&mode=playMuzu"
                else:
                    url = "plugin://"+addonID+"/?url="+videoID+"&mode=playMuzu"
                if ((not unwatched) or unwatched and not url in historyContent) and not title in dupeList and not blacklistContains(url):
                    musicVideos.append([title, url, thumb])
                    dupeList.append(title)
                if limit==pos:
                    break
                pos+=1
        elif type.lower()=="youtube":
            if cacheDuration==-1:
                cacheDuration=7
            """
            #Not usable: max 50 items
            content = cache("https://gdata.youtube.com/feeds/api/playlists/"+value+"?v=2", cacheDuration)
            match = re.compile("<media:title type='plain'>(.+?)</media:title>.+?<yt:videoid>(.+?)</yt:videoid>", re.DOTALL).findall(content)
            #Not usable: max 100 items
            content = cache("https://www.youtube.com/playlist?list="+spl[1].strip(), cacheDuration)
            match = re.compile('data-video-id="(.+?)".+?data-title="(.+?)"', re.DOTALL).findall(content)
            #Workaround to get all playlist items
            """
            content = cache("https://gdata.youtube.com/feeds/api/playlists/"+value+"?v=2", cacheDuration)
            match = re.compile("<media:title type='plain'>(.+?)</media:title>.+?<yt:videoid>(.+?)</yt:videoid>", re.DOTALL).findall(content)
            xbmc.sleep(random.randint(500,1000))
            content = cache("https://www.youtube.com/watch?v="+match[0][1]+"&list="+value, cacheDuration)
            spl=content.split('class="yt-uix-scroller-scroll-unit')
            for i in range(1,len(spl),1):
                entry=spl[i]
                match=re.compile('data-video-id="(.+?)"', re.DOTALL).findall(entry)
                youtubeID=match[0]
                match=re.compile('data-video-title="(.+?)"', re.DOTALL).findall(entry)
                title=cleanTitle(match[0])
                filtered = False
                for entry2 in blacklist:
                    if entry2.strip().lower() and entry2.strip().lower() in title.lower():
                        filtered = True
                if filtered:
                    continue
                if xbox:
                    url = "plugin://video/YouTube/?path=/root/video&action=play_video&videoid=" + youtubeID
                    url = "plugin://video/My Music TV/?url="+urllib.quote_plus(url)+"&mode=playYT"
                else:
                    url = "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=" + youtubeID
                    url = "plugin://"+addonID+"/?url="+urllib.quote_plus(url)+"&mode=playYT"
                thumb = "http://img.youtube.com/vi/"+youtubeID+"/0.jpg"
                if ((not unwatched) or unwatched and not url in historyContent) and not title in dupeList and not blacklistContains(url):
                    musicVideos.append([title, url, thumb])
                    dupeList.append(title)
                if limit==pos:
                    break
                pos+=1
        elif type.lower()=="dailymotion":
            if cacheDuration==-1:
                cacheDuration=7
            content = cache("https://api.dailymotion.com/playlist/"+value+"/videos?fields=id,thumbnail_large_url,title&limit=100", cacheDuration)
            content = json.loads(content)
            for item in content['list']:
                id = item['id']
                title = item['title'].encode('utf-8')
                filtered = False
                for entry2 in blacklist:
                    if entry2.strip().lower() and entry2.strip().lower() in title.lower():
                        filtered = True
                if filtered:
                    continue
                thumb = item['thumbnail_large_url']
                if xbox:
                    url = "plugin://video/My Music TV/?url="+id+"&mode=playDM"
                else:
                    url = "plugin://"+addonID+"/?url="+id+"&mode=playDM"
                if ((not unwatched) or unwatched and not url in historyContent) and not title in dupeList and not blacklistContains(url):
                    musicVideos.append([title, url, thumb])
                    dupeList.append(title)
                if limit==pos:
                    break
                pos+=1
        elif type.lower().startswith("reddit"):
            xbmc.sleep(2000)
            if cacheDuration==-1:
                cacheDuration=7
            redditValues = value.split(":")
            subredditValue = redditValues[0]
            sortValue = redditValues[1]
            timeValue = redditValues[2]
            content = cacheR("http://www.reddit.com/r/"+subredditValue+"/search.json?q="+urllib.quote_plus("site:youtu.be OR site:youtube.com OR site:dailymotion.com")+"&sort="+sortValue+"&restrict_sr=on&limit=100&t="+timeValue, cacheDuration)
            content = json.loads(content.replace('\\"', '\''))
            for entry in content['data']['children']:
                title = cleanTitle(entry['data']['title'].encode('utf-8'))
                thumb = ""
                try:
                    thumb = entry['data']['media']['oembed']['thumbnail_url'].encode('utf-8')
                except:
                    thumb = entry['data']['thumbnail'].encode('utf-8')
                rUrl = ""
                try:
                    rUrl = entry['data']['media']['oembed']['url']+'"'
                except:
                    rUrl = entry['data']['url']+'"'
                matchYoutube = re.compile('youtube.com/watch\\?v=(.+?)"', re.DOTALL).findall(rUrl)
                matchDailyMotion = re.compile('dailymotion.com/video/(.+?)_', re.DOTALL).findall(rUrl)
                matchDailyMotion2 = re.compile('dailymotion.com/.+?video=(.+?)', re.DOTALL).findall(rUrl)
                url = ""
                if matchYoutube:
                    if xbox:
                        url = "plugin://video/YouTube/?path=/root/video&action=play_video&videoid=" + matchYoutube[0]
                        url = "plugin://video/My Music TV/?url="+urllib.quote_plus(url)+"&mode=playYT"
                    else:
                        url = "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=" + matchYoutube[0]
                        url = "plugin://"+addonID+"/?url="+urllib.quote_plus(url)+"&mode=playYT"
                elif matchDailyMotion:
                    if xbox:
                        url = "plugin://video/My Music TV/?url="+matchDailyMotion[0]+"&mode=playDM"
                    else:
                        url = "plugin://"+addonID+"/?url="+matchDailyMotion[0]+"&mode=playDM"
                elif matchDailyMotion2:
                    if xbox:
                        url = "plugin://video/My Music TV/?url="+matchDailyMotion2[0]+"&mode=playDM"
                    else:
                        url = "plugin://"+addonID+"/?url="+matchDailyMotion2[0]+"&mode=playDM"
                filtered = False
                for entry2 in blacklist:
                    if entry2.strip().lower() and entry2.lower() in artist.lower():
                        filtered = True
                if filtered:
                    continue
                if ((not unwatched) or unwatched and not url in historyContent) and not title in dupeList and not blacklistContains(url):
                    musicVideos.append([title, url, thumb])
                    dupeList.append(title)
                if limit==pos:
                    break
                pos+=1
        elif type.lower().startswith("spotify:"):
            spotifyType = type.lower().split(":")[1]
            spotifyID = ""
            if spotifyType=="playlist":
                if cacheDuration==-1:
                    cacheDuration=7
                spotifyValues = value.split(":")
                spotifyID = "spotify:user:"+spotifyValues[0]+":playlist:"+spotifyValues[1]
                content = cache("https://embed.spotify.com/?uri="+spotifyID, cacheDuration)
            elif spotifyType=="album":
                if cacheDuration==-1:
                    cacheDuration=30
                content = cache("https://embed.spotify.com/?uri=spotify:album:"+value, cacheDuration)
            elif spotifyType=="artist":
                if cacheDuration==-1:
                    cacheDuration=30
                content = cache("https://embed.spotify.com/?uri=spotify:artist:"+value, cacheDuration)
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
                    url = "plugin://video/My Music TV/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=playYTByTitle"
                else:
                    url = "plugin://"+addonID+"/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=playYTByTitle"
                if ((not unwatched) or unwatched and not url in historyContent) and not title in dupeList and not blacklistContains(url):
                    musicVideos.append([title, url, thumb])
                    dupeList.append(title)
                if limit==pos:
                    break
                pos+=1
        elif type.lower().startswith("deezer:"):
            deezerType = type.lower().split(":")[1]
            if deezerType=="playlist":
                if cacheDuration==-1:
                    cacheDuration=7
                content = cache("http://api.deezer.com/playlist/"+value, cacheDuration)
            elif deezerType=="radio":
                if cacheDuration==-1:
                    cacheDuration=7
                content = cache("http://api.deezer.com/radio/"+value+"/tracks?limit=100", cacheDuration)
            elif deezerType=="charts":
                if cacheDuration==-1:
                    cacheDuration=7
                content = cache("http://api.deezer.com/editorial/"+value+"/charts?limit=100", cacheDuration)
            elif deezerType=="album":
                if cacheDuration==-1:
                    cacheDuration=30
                content = cache("http://api.deezer.com/album/"+value, cacheDuration)
            elif deezerType=="artist":
                if cacheDuration==-1:
                    cacheDuration=30
                content = cache("https://api.deezer.com/artist/"+value+"/top?limit=100", cacheDuration)
            content = json.loads(content)
            try:
                content = content["tracks"]["data"]
            except:
                content = content["data"]
            try:
                thumb = content["cover"]+"?size=big"
            except:
                thumb = ""
            for item in content:
                artist = item["artist"]["name"].encode('utf-8')
                title = item["title"].encode('utf-8')
                filtered = False
                for entry2 in blacklist:
                    if entry2.strip().lower() and entry2.lower() in artist.lower():
                        filtered = True
                if filtered:
                    continue
                title = artist+" - "+title
                try:
                    thumb = item["album"]["cover"]+"?size=big"
                except:
                    thumb = ""
                if xbox:
                    url = "plugin://video/My Music TV/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=playYTByTitle"
                else:
                    url = "plugin://"+addonID+"/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=playYTByTitle"
                if ((not unwatched) or unwatched and not url in historyContent) and not title in dupeList and not blacklistContains(url):
                    musicVideos.append([title, url, thumb])
                    dupeList.append(title)
                if limit==pos:
                    break
                pos+=1
        elif type.lower()=="itunes":
            if cacheDuration==-1:
                cacheDuration=7
            iTunesValues = value.split(":")
            countryID = iTunesValues[0]
            genreID = iTunesValues[1]
            url = "https://itunes.apple.com/"+countryID+"/rss/topsongs/limit=100"
            if genreID!="0":
                url += "/genre="+genreID
            url += "/explicit=true/json"
            content = cache(url, 1)
            content = json.loads(content)
            for item in content['feed']['entry']:
                artist=item['im:artist']['label'].encode('utf-8')
                videoTitle=item['im:name']['label'].encode('utf-8')
                if " (" in videoTitle:
                    videoTitle=videoTitle[:videoTitle.rfind(" (")]
                title=cleanTitle(artist+" - "+videoTitle)
                try:
                    thumb=item['im:image'][2]['label'].replace("170x170-75.jpg","400x400-75.jpg")
                except:
                    thumb=""
                filtered = False
                for entry2 in blacklist:
                    if entry2.strip().lower() and entry2.strip().lower() in title.lower():
                        filtered = True
                if filtered:
                    continue
                if xbox:
                    url = "plugin://video/My Music TV/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=playYTByTitle"
                else:
                    url = "plugin://"+addonID+"/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=playYTByTitle"
                if ((not unwatched) or unwatched and not url in historyContent) and not title in dupeList and not blacklistContains(url):
                    musicVideos.append([title, url, thumb])
                    dupeList.append(title)
                if limit==pos:
                    break
                pos+=1
    fh.close()
    if shuffled:
        random.shuffle(musicVideos)
    addToPlist(musicVideos)
    for title, url, thumb in musicVideos:
        listitem = xbmcgui.ListItem(title, thumbnailImage=thumb)
        playlist.add(url, listitem)
    if unwatched and len(playlist)==0:
        xbmcvfs.delete(historyFile)
        xbmc.executebuiltin('XBMC.Notification(Info:, All videos played in current channel. History has been resetted. Please restart your channel...,12000,'+icon+')')
    else:
        xbmc.Player().play(playlist)


def playVevo(id):
    try:
        if xbox:
            addToHistory("plugin://video/My Music TV/?url="+id+"&mode=playVevo")
        else:
            addToHistory("plugin://"+addonID+"/?url="+id+"&mode=playVevo")
        content = opener.open("http://videoplayer.vevo.com/VideoService/AuthenticateVideo?isrc="+id).read()
        content = str(json.loads(content))
        match = re.compile('<rendition name="HTTP Live Streaming" url="(.+?)"', re.DOTALL).findall(content)
        fullUrl = ""
        for url in match:
          if cdnVevo in url:
              fullUrl = url
        content = opener.open(fullUrl).read()
        match = re.compile('RESOLUTION='+resolutionVevo+'.*?\n(.+?)\n', re.DOTALL).findall(content)
        fullUrl = fullUrl[:fullUrl.rfind("/")]+"/"+match[len(match)-1].strip()
        listitem = xbmcgui.ListItem(path=fullUrl)
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
        if infoEnabled:
            showInfo()
    except:
        pass


def playMuzu(id):
    try:
        if xbox:
            addToHistory("plugin://video/My Music TV/?url="+id+"&mode=playMuzu")
        else:
            addToHistory("plugin://"+addonID+"/?url="+id+"&mode=playMuzu")
        content = opener.open("http://player.muzu.tv/player/playerInit?ai="+id).read()
        resolution = ""
        if '"v360":true' in content and 360<=resolutionMuzu:
            resolution = "360"
        if '"v480":true' in content and 480<=resolutionMuzu:
            resolution = "480"
        if '"v720":true' in content and 720<=resolutionMuzu:
            resolution = "720"
        if '"v1080":true' in content and 1080<=resolutionMuzu:
            resolution = "1080"
        content = opener.open("http://player.muzu.tv/player/requestVideo?ai="+id+"&qv="+resolution+"&viewhash=muzu").read()
        match = re.compile('"url":"(.+?)"', re.DOTALL).findall(content)
        url = match[0].replace("\\","")
        if url!="http://player.muzu.tv/player/invalidTerritory":
            listitem = xbmcgui.ListItem(path=url)
            xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
            if infoEnabled:
                showInfo()
    except:
        pass


def playDM(id):
    try:
        if xbox:
            addToHistory("plugin://video/My Music TV/?url="+id+"&mode=playDM")
        else:
            addToHistory("plugin://"+addonID+"/?url="+id+"&mode=playDM")
        content = opener.open("http://www.dailymotion.com/embed/video/"+id).read()
        if '"statusCode":410' in content or '"statusCode":403' in content:
            xbmc.executebuiltin('XBMC.Notification(Dailymotion:, Video is not available,5000)')
        else:
            matchFullHD = re.compile('"stream_h264_hd1080_url":"(.+?)"', re.DOTALL).findall(content)
            matchHD = re.compile('"stream_h264_hd_url":"(.+?)"', re.DOTALL).findall(content)
            matchHQ = re.compile('"stream_h264_hq_url":"(.+?)"', re.DOTALL).findall(content)
            matchSD = re.compile('"stream_h264_url":"(.+?)"', re.DOTALL).findall(content)
            matchLD = re.compile('"stream_h264_ld_url":"(.+?)"', re.DOTALL).findall(content)
            url = ""
            if matchFullHD and resolutionDM == "1080p":
                url = urllib.unquote_plus(matchFullHD[0]).replace("\\", "")
            elif matchHD and (resolutionDM == "720p" or resolutionDM == "1080p"):
                url = urllib.unquote_plus(matchHD[0]).replace("\\", "")
            elif matchHQ:
                url = urllib.unquote_plus(matchHQ[0]).replace("\\", "")
            elif matchSD:
                url = urllib.unquote_plus(matchSD[0]).replace("\\", "")
            elif matchLD:
                url = urllib.unquote_plus(matchLD[0]).replace("\\", "")
            listitem = xbmcgui.ListItem(path=url)
            xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
            if infoEnabled:
                showInfo()
    except:
        pass


def playYT(url):
    try:
        if xbox:
            addToHistory("plugin://video/My Music TV/?url="+urllib.quote_plus(url)+"&mode=playYT")
        else:
            addToHistory("plugin://"+addonID+"/?url="+urllib.quote_plus(url)+"&mode=playYT")
        listitem = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
        if infoEnabled:
            showInfo()
    except:
        pass


def playUrl(url):
    try:
        addToHistory(url)
        listitem = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
        if infoEnabled:
            showInfo()
    except:
        pass


def playYTByTitle(title):
    try:
        if xbox:
            addToHistory("plugin://video/My Music TV/?url="+urllib.quote_plus(title)+"&mode=playYTByTitle")
        else:
            addToHistory("plugin://"+addonID+"/?url="+urllib.quote_plus(title)+"&mode=playYTByTitle")
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
        fh = xbmcvfs.File(cacheFile, 'r')
        content = fh.read()
        fh.close()
    else:
        content = opener.open(url).read()
        fh = xbmcvfs.File(cacheFile, 'w')
        fh.write(content)
        fh.close()
    return content


def cacheR(url, duration):
    cacheFile = os.path.join(cacheDir, (''.join(c for c in unicode(url, 'utf-8') if c not in '/\\:?"*|<>')).strip())
    if os.path.exists(cacheFile) and duration!=0 and (time.time()-os.path.getmtime(cacheFile) < 60*60*24*duration):
        fh = xbmcvfs.File(cacheFile, 'r')
        content = fh.read()
        fh.close()
    else:
        content = openerR.open(url).read()
        fh = xbmcvfs.File(cacheFile, 'w')
        fh.write(content)
        fh.close()
    return content


def addToHistory(url):
    historyFile = os.path.join(historyDir, addon.getSetting("currentChannel")+".history")
    fh = xbmcvfs.File(historyFile, 'r')
    content = fh.read()
    fh.close()
    fh = xbmcvfs.File(historyFile, 'w')
    fh.write(content+url+"\n")
    fh.close()


def addToPlist(list):
    plistFile = os.path.join(plistDir, addon.getSetting("currentChannel")+".plist")
    content = ""
    for item in list:
        content+=str(item)+"\n"
    fh = xbmcvfs.File(plistFile, 'w')
    fh.write(content)
    fh.close()


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


def addToPlaylist():
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlistID = playlist.getPlayListId()
    currentPos = playlist.getposition()
    result = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Playlist.GetItems", "params": { "playlistid": '+str(playlistID)+', "properties": ["file", "thumbnail"] }, "id": 1}')
    result = json.loads(result)
    item = result["result"]["items"][currentPos]
    currentTitle = item["label"].encode('utf-8').replace("&", "&quot;")
    currentURL2 = item["file"].encode('utf-8').replace("&", "&quot;")
    currentThumb = urllib.unquote_plus(item["thumbnail"].encode('utf-8').replace("&", "&quot;").replace("image://", "").replace("/", ""))
    dirs, playlists = xbmcvfs.listdir(playlistDir)
    playlists.append("- New playlist")
    dialog = xbmcgui.Dialog()
    nr=dialog.select("Playlists", playlists)
    if nr>=0:
      entry=playlists[nr]
      if entry=="- New playlist":
          kb = xbmc.Keyboard("", "Playlist title")
          kb.doModal()
          if kb.isConfirmed():
            title=kb.getText()
            fh=xbmcvfs.File(os.path.join(playlistDir, title)+".xspf", 'w')
            fh.write("""<?xml version="1.0" encoding="UTF-8"?>
<playlist version="1" xmlns="http://xspf.org/ns/0/">
  <trackList>
    <track>
      <title>"""+currentTitle+"""</title>
      <location>"""+currentURL2+"""</location>
      <image>"""+currentThumb+"""</image>
    </track>
  </trackList>
</playlist>""")
            fh.close()
      else:
          fh=xbmcvfs.File(os.path.join(playlistDir, entry), 'r')
          content=fh.read()
          fh.close()
          fh=xbmcvfs.File(os.path.join(playlistDir, entry), 'w')
          fh.write(content.replace("</trackList>","""  <track>
      <title>"""+currentTitle+"""</title>
      <location>"""+currentURL2+"""</location>
      <image>"""+currentThumb+"""</image>
    </track>
  </trackList>"""))
          fh.close()


def addToBlacklist():
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlistID = playlist.getPlayListId()
    currentPos = playlist.getposition()
    result = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Playlist.GetItems", "params": { "playlistid": '+str(playlistID)+', "properties": ["file", "thumbnail"] }, "id": 1}')
    result = json.loads(result)
    item = result["result"]["items"][currentPos]
    fh = xbmcvfs.File(blacklistFile, 'r')
    content = fh.read()
    fh.close()
    fh = xbmcvfs.File(blacklistFile, 'w')
    fh.write(content+item["file"]+"\n")
    fh.close()
    xbmc.Player().playnext()


def blacklistContains(url):
    if os.path.exists(blacklistFile):
        fh = xbmcvfs.File(blacklistFile, 'r')
        content = fh.read()
        fh.close()
        if url in content:
            return True
        else:
            return False
    else:
        return False


def openSettings(aid):
    xbmcaddon.Addon(id=aid).openSettings()


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


def addDir(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultMusicVideos.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))

if mode == 'playChannel':
    playChannel(url)
elif mode == 'playVevo':
    playVevo(url)
elif mode == 'playMuzu':
    playMuzu(url)
elif mode == 'playDM':
    playDM(url)
elif mode == 'playYT':
    playYT(url)
elif mode == 'playUrl':
    playUrl(url)
elif mode == 'playYTByTitle':
    playYTByTitle(url)
elif mode == 'openSettings':
    openSettings(url)
elif mode == 'addToPlaylist':
    addToPlaylist()
elif mode == 'addToBlacklist':
    addToBlacklist()
elif mode == 'none':
    pass
else:
    index()
