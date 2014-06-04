import xbmc, xbmcgui, xbmcaddon

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'service.resume_livetv'
addon = xbmcaddon.Addon(id=addonID)

autoPvr=addon.getSetting("autoPvr")=="true"
autoDuration=addon.getSetting("autoDuration")=="true"
autoDurationDelay=int(addon.getSetting("autoDurationDelay"))

class PlayerEvents(xbmc.Player):
    currentVideoUrl = ""
    currentVideoTitle = ""
    currentVideoThumb = ""
    def onPlayBackStarted(self):
        xbmc.sleep(100)
        playingFile = xbmc.getInfoLabel('Player.Filenameandpath')
        playingTitle = xbmc.getInfoLabel('Player.Title')
        playingThumb = xbmc.getInfoLabel('Player.Art(thumb)')
        if playingFile!=self.currentVideoUrl:
            if (autoPvr and playingFile.startswith("pvr://")) or (autoDuration and int(self.getTotalTime())<=autoDurationDelay):
                self.currentVideoUrl = playingFile
                self.currentVideoTitle = playingTitle
                self.currentVideoThumb = playingThumb
            elif self.currentVideoUrl:
                playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                listitem = xbmcgui.ListItem(self.currentVideoTitle, thumbnailImage=self.currentVideoThumb)
                playlist.add(self.currentVideoUrl, listitem)


player=PlayerEvents()
while (not xbmc.abortRequested):
    xbmc.sleep(500)
