#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import re
import os
import xbmcplugin
import xbmcgui
import xbmcaddon
import random

addon = xbmcaddon.Addon()
pluginhandle = int(sys.argv[1])
opener = urllib2.build_opener()
addonID = 'script.screensaver.filmstarts_de'
addonUserDataFolder=xbmc.translatePath("special://profile/addon_data/"+addonID)
playedFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/played")
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0')]
trailerType = ["aktuell_im_kino", "bald_im_kino"]
baseUrl = "http://www.filmstarts.de"
if not os.path.isdir(addonUserDataFolder):
  os.mkdir(addonUserDataFolder)


def playRandomVideo():
    type = trailerType[random.randint(0, 1)]
    page = str(random.randint(1, 3))
    content = opener.open("http://www.filmstarts.de/trailer/"+type+".html?page="+page+"&sort_order=0&version=1").read()
    match = re.compile('<img src=\'(.+?)\' alt=".+?" title=".+?" />\n</span>\n</div>\n<div class="contenzone">\n<div class="titlebar">\n<a class="link" href="(.+?)">\n<span class=\'bold\'>(.+?)</span>', re.DOTALL).findall(content)
    pos = random.randint(0, len(match)-1)
    thumb = get_better_thumb(match[pos][0])
    url = match[pos][1]
    title = match[pos][2]
    fileContent = ""
    if os.path.exists(playedFile):
        fh=open(playedFile, 'r')
        fileContent = fh.read()
        fh.close()
    count = 0
    while url in fileContent and count<len(match):
        count += 1
        pos = random.randint(0, len(match)-1)
        thumb = get_better_thumb(match[pos][0])
        url = match[pos][1]
        title = match[pos][2]
    content = opener.open(baseUrl+url).read()
    match = re.compile('"html5PathHD":"(.*?)"', re.DOTALL).findall(content)
    finalUrl = ""
    if match[0]:
        finalUrl = match[0]
    else:
        match = re.compile('"refmedia":(.+?),', re.DOTALL).findall(content)
        media = match[0]
        match = re.compile('"cMovie":(.+?),', re.DOTALL).findall(content)
        ref = match[0]
        match = re.compile('"entityType":"(.+?)"', re.DOTALL).findall(content)
        typeRef = match[0]
        content = opener.open(baseUrl + '/ws/AcVisiondataV4.ashx?media='+media+'&ref='+ref+'&typeref='+typeRef).read()
        finalUrl = ""
        match = re.compile('hd_path="(.+?)"', re.DOTALL).findall(content)
        finalUrl = match[0]
    if finalUrl:
        fh=open(playedFile, 'a')
        fh.write(url+"\n")
        fh.close()
        listitem = xbmcgui.ListItem(title, path=finalUrl, thumbnailImage=thumb)
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def get_better_thumb(thumb_url):
    thumb_url = '/'.join([
        p for p in thumb_url.split('/')
        if not p[0:2] in ('r_', 'c_', 'cx', 'b_', 'o_')
    ])
    return thumb_url.replace("/medias/", "/r_300_400/medias/")


playRandomVideo()
