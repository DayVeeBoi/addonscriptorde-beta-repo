#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmcaddon,xbmcplugin,xbmcgui,urllib,sys,re,os

addon = xbmcaddon.Addon()
pluginhandle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
iconARD=xbmc.translatePath('special://home/addons/'+addonID+'/iconARD.png')
iconArte=xbmc.translatePath('special://home/addons/'+addonID+'/iconArte.png')
iconATV=xbmc.translatePath('special://home/addons/'+addonID+'/iconATV.png')
iconDMAX=xbmc.translatePath('special://home/addons/'+addonID+'/iconDMAX.png')
iconEuroNews=xbmc.translatePath('special://home/addons/'+addonID+'/iconEuroNews.png')
iconMTV=xbmc.translatePath('special://home/addons/'+addonID+'/iconMTV.png')
iconMySpass=xbmc.translatePath('special://home/addons/'+addonID+'/iconMySpass.png')
iconN24=xbmc.translatePath('special://home/addons/'+addonID+'/iconN24.png')
iconNOW=xbmc.translatePath('special://home/addons/'+addonID+'/iconNOW.png')
iconSouthPark=xbmc.translatePath('special://home/addons/'+addonID+'/iconSouthPark.png')
iconSpiegelTV=xbmc.translatePath('special://home/addons/'+addonID+'/iconSpiegelTV.png')
iconVEVOTV=xbmc.translatePath('special://home/addons/'+addonID+'/iconVEVOTV.png')
iconWeltDerWunder=xbmc.translatePath('special://home/addons/'+addonID+'/iconWeltDerWunder.png')
iconZDF=xbmc.translatePath('special://home/addons/'+addonID+'/iconZDF.png')
iconTele5=xbmc.translatePath('special://home/addons/'+addonID+'/iconTele5.png')
site1=addon.getSetting("site1")=="true"
site2=addon.getSetting("site2")=="true"
site3=addon.getSetting("site3")=="true"
site4=addon.getSetting("site4")=="true"
site5=addon.getSetting("site5")=="true"
site6=addon.getSetting("site6")=="true"
site7=addon.getSetting("site7")=="true"
site8=addon.getSetting("site8")=="true"
site9=addon.getSetting("site9")=="true"
site10=addon.getSetting("site10")=="true"
site11=addon.getSetting("site11")=="true"
site12=addon.getSetting("site12")=="true"
site13=addon.getSetting("site13")=="true"
site14=addon.getSetting("site14")=="true"
site15=addon.getSetting("site15")=="true"
site16=addon.getSetting("site16")=="true"
site17=addon.getSetting("site17")=="true"
site18=addon.getSetting("site18")=="true"
site19=addon.getSetting("site19")=="true"
site22=addon.getSetting("site22")=="true"
site23=addon.getSetting("site23")=="true"

def index():
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    if site1:
        addDir("ARD","plugin://plugin.video.ardmediathek_de",iconARD)
    if site2:
        addDir("Arte","plugin://plugin.video.arte_tv",iconArte)
    if site3:
        addDir("ATV","plugin://plugin.video.atv_at",iconATV)
    if site4:
        addDir("DMAX","plugin://plugin.video.dmax_de",iconDMAX)
    if site5:
        addDir("Euronews","plugin://plugin.video.euronews_com",iconEuroNews)
    if site6:
        addDir("MTV","plugin://plugin.video.mtv_de/?mode=listShows&url=http%3a%2f%2fwww.mtv.de%2fshows%2falle",iconMTV)
    if site7:
        addDir("MySpass","plugin://plugin.video.myspass_de",iconMySpass)
    if site8:
        addDir("N24","plugin://plugin.video.n24_de",iconN24)
    if site13:
        addDir("South Park","plugin://plugin.video.southpark_de",iconSouthPark)
    if site14:
        addDir("Spiegel TV","plugin://plugin.video.spiegel_tv",iconSpiegelTV)
    if site16:
        addDir("VEVO TV","plugin://plugin.video.vevo_tv",iconVEVOTV)
    if site18:
        addDir("Welt der Wunder","plugin://plugin.video.welt_der_wunder",iconWeltDerWunder)
    if site19:
        addDir("ZDF","plugin://plugin.video.zdf_de_lite",iconZDF)
    if site22:
        addDir("Tele 5","plugin://plugin.video.tele5_de",iconTele5)
    if site23:
        addDir("NOW","plugin://plugin.video.rtl_now", iconNOW)
    xbmcplugin.endOfDirectory(pluginhandle)


def addDir(name,url,iconimage):
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz,isFolder=True)
    return ok


def translation(id):
    return addon.getLocalizedString(id).encode('utf-8')


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict

index()
