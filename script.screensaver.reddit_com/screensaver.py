#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcaddon
import urllib
import urllib2
import re
import random


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
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0')]
xbox = xbmc.getCondVisibility("System.Platform.xbox")
jumpBack = int(addon.getSetting("jumpBack"))
type = int(addon.getSetting("type"))
type = ["hot","day","week","month"][int(type)]
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
    try:
        addVideos()
    except:
        pass
    if playlist:
        xbmc.Player().play(playlist)
    else:
        xbmc.executebuiltin('XBMC.Notification(Video Screensaver:,'+translation(30004)+'!,5000)')
else:
    myWindow.doModal()
