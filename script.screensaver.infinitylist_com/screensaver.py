#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcaddon
import urllib
import urllib2
import re


class XBMCPlayer(xbmc.Player):
    def onPlayBackStopped(self):
        xbmc.sleep(exitDelay)
        myWindow.close()
        if playbackInterrupted:
            xbmc.sleep(500)
            xbmc.Player().play(currentUrl)
            xbmc.Player().seekTime(currentPosition-jumpBack)
            xbmc.Player().pause()
        else:
            xbmc.Player().stop()
        self.close()

    def onPlayBackEnded(self):
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        pos = playlist.getposition()
        if pos == len(playlist)-1:
            xbmc.sleep(5000)
            myWindow.close()
            if playbackInterrupted:
                xbmc.sleep(500)
                xbmc.Player().play(currentUrl)
                xbmc.Player().seekTime(currentPosition-jumpBack)
                xbmc.Player().pause()
            else:
                xbmc.Player().stop()
            self.close()


class window(xbmcgui.WindowXMLDialog):
    def onInit(self):
        try:
            addVideos()
            addVideos()
        except:
            pass
        if playlist:
            myPlayer.play(playlist)
        else:
            xbmc.executebuiltin('XBMC.Notification(Video Screensaver:,'+translation(30004)+'!,5000)')
            myPlayer.stop()
            myWindow.close()
            myPlayer.close()

    def onAction(self, action):
        ACTION_STOP = 13
        ACTION_PREVIOUS_MENU = 10
        if action in [ACTION_PREVIOUS_MENU, ACTION_STOP]:
            myPlayer.stop()

addon = xbmcaddon.Addon()
xbox = xbmc.getCondVisibility("System.Platform.xbox")
urlMain = "http://www.infinitylist.com"
jumpBack = int(addon.getSetting("jumpBack"))
genre = addon.getSetting("genre")
genre = ["ALL", "bike", "climb", "extra", "motor", "parkour", "skate", "sky", "snow", "water"][int(genre)]
exitDelay = int(addon.getSetting("exitDelay"))
myWindow = window('window.xml', addon.getAddonInfo('path'), 'default',)
myPlayer = XBMCPlayer()
playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
playlist.clear()
playbackInterrupted = False
currentUrl = ""
currentPosition = 0
if xbmc.Player().isPlaying():
    currentUrl = xbmc.Player().getPlayingFile()
    currentPosition = xbmc.Player().getTime()
    xbmc.Player().stop()
    xbmc.sleep(1000)
    playbackInterrupted = True


def addVideos():
    if genre == "ALL":
        url = urlMain+"/shuffle/?burnt_inline_load=true"
    else:
        url = urlMain+"/"+genre+"/shuffle/?burnt_inline_load=true"
    content = getUrl(url)
    spl = content.split('<div id="videoPost-')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<a href=".+?">(.+?)</a>', re.DOTALL).findall(entry)
        title = cleanTitle(match[0])
        matchYoutube = re.compile('data-youtube-video-i-d="(.+?)"', re.DOTALL).findall(entry)
        matchVimeo = re.compile('data-vimeo-video-i-d="(.+?)"', re.DOTALL).findall(entry)
        matchYoutube2 = re.compile('http://www.youtube.com/embed/(.+?)\\?', re.DOTALL).findall(entry)
        matchVimeo2 = re.compile('http://player.vimeo.com/video/(.+?)\\?', re.DOTALL).findall(entry)
        url = ""
        if matchYoutube:
            url = getYoutubeUrl(matchYoutube[0])
        elif matchVimeo:
            url = getVimeoUrl(matchVimeo[0])
        elif matchYoutube2:
            url = getYoutubeUrl(matchYoutube2[0])
        elif matchVimeo2:
            url = getVimeoUrl(matchVimeo2[0])
        if url:
            listitem = xbmcgui.ListItem(title)
            playlist.add(url, listitem)


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


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#038;", "&").replace("&#039;", "\\").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
    title = title.replace("&#8211;", "-").replace("&#8220;", "-").replace("&#8221;", "-").replace("&#8217;", "'").replace("&#8216;", "‘")
    title = title.strip()
    return title


def getUrl(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0')
    req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    req.add_header('Accept-Language', 'de-de,de;q=0.8,en-us;q=0.5,en;q=0.3')
    req.add_header('Accept-Encoding', 'deflate')
    response = urllib2.urlopen(req)
    content = response.read()
    response.close()
    return content


param = ""
if len(sys.argv)>1:
    param = urllib.unquote_plus(sys.argv[1])
if param=="tv_mode":
    addVideos()
    addVideos()
    xbmc.Player().play(playlist)
else:
    myWindow.doModal()
