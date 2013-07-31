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
urlMain = "http://trailers.apple.com"
jumpBack = int(addon.getSetting("jumpBack"))
g_action = addon.getSetting("g_action") == "true"
g_comedy = addon.getSetting("g_comedy") == "true"
g_docu = addon.getSetting("g_docu") == "true"
g_drama = addon.getSetting("g_drama") == "true"
g_family = addon.getSetting("g_family") == "true"
g_fantasy = addon.getSetting("g_fantasy") == "true"
g_foreign = addon.getSetting("g_foreign") == "true"
g_horror = addon.getSetting("g_horror") == "true"
g_musical = addon.getSetting("g_musical") == "true"
g_romance = addon.getSetting("g_romance") == "true"
g_scifi = addon.getSetting("g_scifi") == "true"
g_thriller = addon.getSetting("g_thriller") == "true"
opener = urllib2.build_opener()
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


def genreCheck(genres):
    passed = True
    if not g_action:
        if "Action and Adventure" in genres:
            passed = False
    if not g_comedy:
        if "Comedy" in genres:
            passed = False
    if not g_docu:
        if "Documentary" in genres:
            passed = False
    if not g_drama:
        if "Drama" in genres:
            passed = False
    if not g_family:
        if "Family" in genres:
            passed = False
    if not g_fantasy:
        if "Fantasy" in genres:
            passed = False
    if not g_foreign:
        if "Foreign" in genres:
            passed = False
    if not g_horror:
        if "Horror" in genres:
            passed = False
    if not g_musical:
        if "Musical" in genres:
            passed = False
    if not g_romance:
        if "Romance" in genres:
            passed = False
    if not g_scifi:
        if "Science Fiction" in genres:
            passed = False
    if not g_thriller:
        if "Thriller" in genres:
            passed = False
    return passed


def addVideos():
    entries = []
    content = opener.open(urlMain+"/trailers/home/feeds/studios.json").read()
    spl = content.split('"title"')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('"(.+?)"', re.DOTALL).findall(entry)
        title = match[0]
        match = re.compile('"genre":(.+?),', re.DOTALL).findall(entry)
        genres = match[0]
        match = re.compile('"poster":"(.+?)"', re.DOTALL).findall(entry)
        thumb = urlMain+match[0].replace("poster.jpg", "poster-xlarge.jpg")
        match = re.compile('"url":"(.+?)","type":"(.+?)"', re.DOTALL).findall(entry)
        for url, type in match:
            urlTemp = urlMain+url+"includes/"+type.replace('-', '').replace(' ', '').lower()+"/extralarge.html"
            url = "plugin://script.screensaver.apple_itunes_trailer/?url="+urllib.quote_plus(urlTemp)
            if genreCheck(genres) and "International Trailer -" not in type and "Announcement -" not in type:
                entries.append([title+" - "+type, url, thumb])
    random.shuffle(entries)
    for title, url, thumb in entries:
        listitem = xbmcgui.ListItem(title, thumbnailImage=thumb)
        playlist.add(url, listitem)

myWindow = window('window.xml', addon.getAddonInfo('path'), 'default',)
myWindow.doModal()
