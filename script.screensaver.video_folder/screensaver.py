#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcaddon
import urllib
import urllib2
import re
import os
import random


class window(xbmcgui.WindowXMLDialog):
    def onInit(self):
        addVideos()
        if playlist:
            xbmc.Player().play(playlist)
        else:
            xbmc.executebuiltin('XBMC.Notification(Video Screensaver:,'+translation(30003)+'!,5000)')
            xbmc.Player().stop()
            self.close()

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
addonID = "script.screensaver.video_folder"
translation = addon.getLocalizedString

while (not os.path.exists(xbmc.translatePath("special://profile/addon_data/"+addonID+"/settings.xml"))) or addon.getSetting("videoDir")=="":
    addon.openSettings()

jumpBack = int(addon.getSetting("jumpBack"))
videoDir = addon.getSetting("videoDir")

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
    for root, dirs, files in os.walk(videoDir):
        for filename in files:
            if filename.endswith(('.mkv', '.avi', '.mp4', '.wmv', '.flv', '.mpg', '.mov')):
                entries.append(os.path.join(root, filename))
    random.shuffle(entries)
    for file in entries:
        playlist.add(file)

myWindow = window('window.xml', addon.getAddonInfo('path'), 'default',)
myWindow.doModal()
