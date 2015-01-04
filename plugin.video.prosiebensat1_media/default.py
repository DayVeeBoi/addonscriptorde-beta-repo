#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import sys
import re
import os
import json
import xbmcplugin
import xbmcaddon
import xbmcgui

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = "plugin.video.prosiebensat1_media"
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
useThumb = addon.getSetting("useThumb") == "true"
forceViewMode = addon.getSetting("forceViewNew") == "true"
viewIDVideos = str(addon.getSetting("viewIDVideos"))
viewIDShows = str(addon.getSetting("viewIDShows"))
addonDir = xbmc.translatePath(addon.getAddonInfo('path'))
addonUserDataFolder = xbmc.translatePath(addon.getAddonInfo('profile'))
cacheDir = os.path.join(addonUserDataFolder, "cache")
channelFavsFile = os.path.join(addonUserDataFolder, addonID+".favourites")
defaultFanart = os.path.join(addonDir ,'fanart.png')
icon = os.path.join(addonDir ,'icon.png')
iconPro7 = os.path.join(addonDir ,'iconPro7.png')
iconSat1 = os.path.join(addonDir ,'iconSat1.png')
iconKabel1 = os.path.join(addonDir ,'iconKabel1.png')
iconSixx = os.path.join(addonDir ,'iconSixx.png')
iconMaxx = os.path.join(addonDir ,'iconMaxx.png')
iconGold = os.path.join(addonDir ,'iconGold.png')
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0')]
mainUrl = "http://contentapi.sim-technik.de"

if not os.path.isdir(addonUserDataFolder):
    os.mkdir(addonUserDataFolder)
if not os.path.isdir(cacheDir):
    os.mkdir(cacheDir)


def index():
    addDir(translation(30006), "", 'listShowsFavs', '', '')
    addDir(translation(30012), "pro7", "channelMain", iconPro7)
    addDir(translation(30013), "sat1", "channelMain", iconSat1)
    addDir(translation(30014), "kabel1", "channelMain", iconKabel1)
    addDir(translation(30015), "sixx", "channelMain", iconSixx)
    addDir(translation(30016), "prosiebenmaxx", "channelMain", iconMaxx)
    addDir(translation(30017), "sat1gold", "channelMain", iconGold)
    addDir(translation(30005), "", "search", thumb)
    xbmcplugin.endOfDirectory(pluginhandle)


def channelMain(channel, thumb):
    addDir(translation(30007), mainUrl+"/mega-app/v2/"+channel+"/tablet/homepage", "listVideos", thumb, "", "Aktuelle ganze Folgen")
    addDir(translation(30008), mainUrl+"/mega-app/v2/"+channel+"/tablet/homepage", "listVideos", thumb, "", "Neueste Clips")
    addDir(translation(30009), mainUrl+"/mega-app/v2/"+channel+"/tablet/format", "listShows", thumb, "", "Aktuell")
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideos(url, type, thumb):
    content = opener.open(url).read()
    content = json.loads(content)
    try:
        fanart = content["screen"]["screen_objects"][0]["image_url"]
        fh = open(os.path.join(cacheDir, content["screen"]["id"].replace(":","#")), 'w')
        fh.write(fanart)
        fh.close()
    except:
        fanart = ""
    for videoType in content["screen"]["screen_objects"]:
        try:
            vt=videoType["title"]
        except:
            vt=""
        if type=="Ganze Folgen" and vt!=type:
            try:
                count=videoType["total_count"]
            except:
                count=0
            if count>0:
                addDir(vt, mainUrl+"/mega-app/v2/"+content["screen"]["id"].split(":")[0]+"/tablet/format/show/"+content["screen"]["id"], "listVideos", thumb, fanart, vt)
    for videoType in content["screen"]["screen_objects"]:
        try:
            try:
                vt=videoType["title"]
            except:
                vt=""
            if vt==type or (type=="" and vt in ["Ganze Folgen", "Highlights"]):
                for item in videoType["screen_objects"]:
                    title = item["video_title"].encode('utf-8')
                    titleMain = item["format_title"].encode('utf-8')
                    if titleMain:
                        title = titleMain+" - "+title
                    try:
                        desc = item["publishing_date"].encode('utf-8')
                        descTemp = desc.split(" ")[0]
                        descTemp = descTemp[:descTemp.rfind(".")]
                        title = descTemp+" - "+title
                    except:
                        desc = ""
                    try:
                        showID = item["format_id"]
                        cacheFile = os.path.join(cacheDir, showID.replace(":","#"))
                        if os.path.exists(cacheFile):
                            fh = open(cacheFile, 'r')
                            fanart = fh.read()
                            fh.close()
                        else:
                            fanart = ""
                    except:
                        fanart = ""
                    try:
                        duration = str(item["duration"])
                        duration = duration.split(".")[0]
                    except:
                        duration = ""
                    videoID = str(item["id"])
                    thumb = item["image_url"].replace("mega_app_420x236","mega_app_1280x720")
                    addLink(title, videoID, "playVideo", thumb, fanart, desc, duration)
        except:
            pass
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')


def listVideosFavs(url):
    content = opener.open(url).read()
    content = json.loads(content)
    for item in content["screen_objects"]:
        title = item["video_title"].encode('utf-8')
        titleMain = item["format_title"].encode('utf-8')
        if titleMain:
            title = titleMain+" - "+title
        try:
            desc = item["publishing_date"].encode('utf-8')
            descTemp = desc.split(" ")[0]
            descTemp = descTemp[:descTemp.rfind(".")]
            title = descTemp+" - "+title
            desc = desc+"\n"+item["description"].encode('utf-8')
        except:
            desc = ""
        try:
            showID = item["format_id"]
            cacheFile = os.path.join(cacheDir, showID.replace(":","#"))
            if os.path.exists(cacheFile):
                fh = open(cacheFile, 'r')
                fanart = fh.read()
                fh.close()
            else:
                fanart = ""
        except:
            fanart = ""
        try:
            duration = str(item["duration"])
            duration = duration.split(".")[0]
        except:
            duration = ""
        videoID = str(item["id"])
        thumb = item["image_url"].replace("mega_app_566x318","mega_app_1280x720")
        addLink(title, videoID, "playVideo", thumb, fanart, desc, duration)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')


def listShows(url, type):
    content = opener.open(url).read()
    content = json.loads(content)
    for item in content["screen"]["screen_objects"]:
        title = item["title"].encode('utf-8')
        showID = str(item["id"])
        cacheFile = os.path.join(cacheDir, showID.replace(":","#"))
        if os.path.exists(cacheFile):
            fh = open(cacheFile, 'r')
            fanart = fh.read()
            fh.close()
        else:
            fanart = ""
        thumb = item["image_url"].replace("mega_app_420x236","mega_app_1280x720")
        addShowDir(title, mainUrl+"/mega-app/v2/"+showID.split(":")[0]+"/tablet/format/show/"+showID, "listVideos", thumb, fanart, "Ganze Folgen", showID)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewIDShows+')')


def playVideo(videoID):
    content = opener.open("http://vas.sim-technik.de/video/video.json?clipid="+videoID+"&method=4").read()
    content = json.loads(content)
    listitem = xbmcgui.ListItem(path=content["VideoURL"])
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def queueVideo(url, name, thumb):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name, thumbnailImage=thumb)
    playlist.add(url, listitem)


def search(thumb):
    keyboard = xbmc.Keyboard('', translation(30005))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText().replace(" ", "+")
        listVideos(mainUrl+"/mega-app/v2/tablet/search?query="+search_string, "", thumb)


def listShowsFavs():
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    if os.path.exists(channelFavsFile):
        fh = open(channelFavsFile, 'r')
        all_lines = fh.readlines()
        ids = ""
        for line in all_lines:
            url = line[line.find("###URL###=")+10:]
            url = url[:url.find("#")]
            ids += url+","
        if ids:
            ids = ids[:-1]
            addDir("- Neue Folgen", mainUrl+"/mega-app/v2/tablet/videos/favourites?ids=["+ids+"]", "listVideosFavs", "")
        for line in all_lines:
            title = line[line.find("###TITLE###=")+12:]
            title = title[:title.find("#")]
            url = line[line.find("###URL###=")+10:]
            url = url[:url.find("#")]
            showID = urllib.unquote_plus(url)
            cacheFile = os.path.join(cacheDir, showID.replace(":","#"))
            if os.path.exists(cacheFile):
                fh = open(cacheFile, 'r')
                fanart = fh.read()
                fh.close()
            else:
                fanart = ""
            thumb = line[line.find("###THUMB###=")+12:]
            thumb = thumb[:thumb.find("#")]
            addShowFavDir(urllib.unquote_plus(title), mainUrl+"/mega-app/v2/"+showID.split(":")[0]+"/tablet/format/show/"+showID, "listVideos", urllib.unquote_plus(thumb), fanart, "Ganze Folgen", showID)
        fh.close()
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewIDShows+')')


def favs(param):
    mode = param[param.find("###MODE###=")+11:]
    mode = mode[:mode.find("###")]
    channelEntry = param[param.find("###TITLE###="):]
    if mode == "ADD":
        if os.path.exists(channelFavsFile):
            fh = open(channelFavsFile, 'r')
            content = fh.read()
            fh.close()
            if content.find(channelEntry) == -1:
                fh = open(channelFavsFile, 'a')
                fh.write(channelEntry+"\n")
                fh.close()
        else:
            fh = open(channelFavsFile, 'a')
            fh.write(channelEntry+"\n")
            fh.close()
    elif mode == "REMOVE":
        refresh = param[param.find("###REFRESH###=")+14:]
        refresh = refresh[:refresh.find("#")]
        fh = open(channelFavsFile, 'r')
        content = fh.read()
        fh.close()
        entry = content[content.find(channelEntry):]
        fh = open(channelFavsFile, 'w')
        fh.write(content.replace(channelEntry+"\n", ""))
        fh.close()
        if refresh == "TRUE":
            xbmc.executebuiltin("Container.Refresh")


def translation(id):
    return addon.getLocalizedString(id).encode('utf-8')


def getPluginUrl(pluginID):
    plugin = xbmcaddon.Addon(id=pluginID)
    if xbmc.getCondVisibility("System.Platform.xbox"):
        return "plugin://video/"+plugin.getAddonInfo('name')
    else:
        return "plugin://"+plugin.getAddonInfo('id')


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addLink(name, url, mode, iconimage, fanart="", desc="", duration=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    liz.setProperty('IsPlayable', 'true')
    if duration:
        liz.addStreamInfo('video', {'duration': int(duration)})
    if fanart and not useThumb:
        liz.setProperty("fanart_image", fanart)
    else:
        liz.setProperty("fanart_image", iconimage)
    liz.addContextMenuItems([(translation(30002), 'RunPlugin('+getPluginUrl(addonID)+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+urllib.quote_plus(name)+'&thumb='+urllib.quote_plus(iconimage)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage, fanart="", type=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&thumb="+urllib.quote_plus(iconimage)+"&type="+urllib.quote_plus(type)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    if fanart:
        liz.setProperty("fanart_image", fanart)
    else:
        liz.setProperty("fanart_image", defaultFanart)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addShowDir(name, url, mode, iconimage, fanart="", type="", showID=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&thumb="+urllib.quote_plus(iconimage)+"&type="+urllib.quote_plus(type)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    if fanart:
        liz.setProperty("fanart_image", fanart)
    else:
        liz.setProperty("fanart_image", defaultFanart)
    playListInfos = "###MODE###=ADD###TITLE###="+urllib.quote_plus(name)+"###URL###="+urllib.quote_plus(showID)+"###THUMB###="+urllib.quote_plus(iconimage)+"###END###"
    liz.addContextMenuItems([(translation(30003), 'RunPlugin(plugin://'+addonID+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addShowFavDir(name, url, mode, iconimage, fanart="", type="", showID=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&thumb="+urllib.quote_plus(iconimage)+"&type="+urllib.quote_plus(type)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    if fanart:
        liz.setProperty("fanart_image", fanart)
    else:
        liz.setProperty("fanart_image", defaultFanart)
    playListInfos = "###MODE###=REMOVE###REFRESH###=TRUE###TITLE###="+urllib.quote_plus(name)+"###URL###="+urllib.quote_plus(showID)+"###THUMB###="+urllib.quote_plus(iconimage)+"###END###"
    liz.addContextMenuItems([(translation(30004), 'RunPlugin(plugin://'+addonID+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))
type = urllib.unquote_plus(params.get('type', ''))

if mode == 'channelMain':
    channelMain(url, thumb)
elif mode == 'listVideos':
    listVideos(url, type, thumb)
elif mode == 'listVideosFavs':
    listVideosFavs(url)
elif mode == 'listShows':
    listShows(url, type)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'queueVideo':
    queueVideo(url, name, thumb)
elif mode == 'listShowsFavs':
    listShowsFavs()
elif mode == 'favs':
    favs(url)
elif mode == 'search':
    search(thumb)
else:
    index()
