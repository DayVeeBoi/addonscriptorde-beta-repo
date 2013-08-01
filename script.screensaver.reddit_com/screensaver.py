#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcaddon
import urllib
import urllib2
import re
import random


class window(xbmcgui.WindowXMLDialog):
    def onInit(self):
        addVideos()
        xbmc.Player().play(playlist)

    def onAction(self, action):
        ACTION_STOP = 13
        ACTION_PREVIOUS_MENU = 10
        if action in [ACTION_PREVIOUS_MENU, ACTION_STOP]:
            xbmc.Player().stop()
            xbmc.sleep(1000)
            xbmc.Player().stop()
            if isPlaying:
                xbmc.sleep(500)
                xbmc.Player().play(currentUrl)
                xbmc.Player().seekTime(currentPosition-jumpBack)
                xbmc.Player().pause()
            xbmc.sleep(500)
            self.close()

addon = xbmcaddon.Addon()
opener = urllib2.build_opener()
xbox = xbmc.getCondVisibility("System.Platform.xbox")
jumpBack = int(addon.getSetting("jumpBack"))
type = int(addon.getSetting("type"))
type = ["hot","day","week","month"][int(type)]
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
    entries = []
    if type=="hot":
        url = "http://www.reddit.com/r/videos/hot/.json?limit=100"
    else:
        url = "http://www.reddit.com/r/videos/top/.json?limit=100&t="+type
    content = opener.open(url).read()
    spl = content.split('"content"')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('"title": "(.+?)"', re.DOTALL).findall(entry)
        title = match[0]
        matchYoutube = re.compile('"url": "http://www.youtube.com/watch\\?v=(.+?)"', re.DOTALL).findall(entry)
        matchVimeo = re.compile('"url": "http://vimeo.com/(.+?)"', re.DOTALL).findall(entry)
        url = ""
        if matchYoutube:
            url = getYoutubeUrl(matchYoutube[0])
        elif matchVimeo:
            url = getVimeoUrl(matchVimeo[0].replace("#", ""))
        if url:
            entries.append([title, url])
    random.shuffle(entries)
    for title, url in entries:
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


param = ""
if len(sys.argv)>1:
    param = urllib.unquote_plus(sys.argv[1])
if param=="tv_mode":
    addVideos()
    xbmc.Player().play(playlist)
else:
    myWindow = window('window.xml', addon.getAddonInfo('path'), 'default',)
    myWindow.doModal()
