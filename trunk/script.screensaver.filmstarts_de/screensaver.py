#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcaddon
import urllib
import re
import os


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


def addVideos():
    for i in range(1, 100, 1):
        playlist.add("plugin://script.screensaver.filmstarts_de/")


addon = xbmcaddon.Addon()
addonID = 'script.screensaver.filmstarts_de'
playedFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/played")
jumpBack = int(addon.getSetting("jumpBack"))
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

if os.path.exists(playedFile):
    os.remove(playedFile)

param = ""
if len(sys.argv)>1:
    param = urllib.unquote_plus(sys.argv[1])
if param=="tv_mode":
    addVideos()
    xbmc.Player().play(playlist)
else:
    myWindow = window('window.xml', addon.getAddonInfo('path'), 'default',)
    myWindow.doModal()
