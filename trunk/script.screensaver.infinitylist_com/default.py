#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcaddon
import urllib2
import re


class window(xbmcgui.WindowXMLDialog):
    def onInit(self):
        addVideos()
        addVideos()
        xbmc.Player().play(playlist)

    def onAction(self, action):
        ACTION_STOP = 13
        ACTION_PREVIOUS_MENU = 10
        if action in [ACTION_PREVIOUS_MENU, ACTION_STOP]:
            xbmc.Player().stop()
            self.close()
            xbmc.sleep(1000)
            xbmc.Player().stop()
            if isPlaying:
                xbmc.sleep(500)
                xbmc.Player().play(currentUrl)
                xbmc.Player().seekTime(currentPosition-jumpBack)
                xbmc.Player().pause()

addon = xbmcaddon.Addon()
xbox = xbmc.getCondVisibility("System.Platform.xbox")
urlMain = "http://www.infinitylist.com"
jumpBack = int(addon.getSetting("jumpBack"))
genre = addon.getSetting("genre")
genre = ["ALL", "bike", "climb", "extra", "motor", "parkour", "skate", "sky", "snow", "water"][int(genre)]
playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
playlist.clear()
isPlaying = False
currentUrl = ""
currentPosition = 0
if xbmc.Player().isPlaying():
    isPlaying = True
    currentUrl = xbmc.Player().getPlayingFile()
    currentPosition = xbmc.Player().getTime()
    xbmc.Player().stop()


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


def playYoutubeVideo(id):
    listItem = xbmcgui.ListItem(path=getYoutubeUrl(id))
    xbmcplugin.setResolvedUrl(pluginhandle, True, listItem)


def playVimeoVideo(id):
    listItem = xbmcgui.ListItem(path=getVimeoUrl(id))
    xbmcplugin.setResolvedUrl(pluginhandle, True, listItem)


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


myWindow = window('window.xml', addon.getAddonInfo('path'), 'default',)
myWindow.doModal()
