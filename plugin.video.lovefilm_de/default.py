#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import re
import sys
import xbmcplugin
import xbmcaddon
import xbmcgui
import subprocess

socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
addonId = 'plugin.video.lovefilm_de'
addon = xbmcaddon.Addon(id=addonId)
translation = addon.getLocalizedString
baseUrl = "http://www.lovefilm.de"
lfPlayerPath = xbmc.translatePath("special://home/addons/"+addonId+"/LovefilmPlayer.exe")
useCoverAsFanart = addon.getSetting("useCoverAsFanart") == "true"
player = addon.getSetting("player")


def index():
    addDir(translation(30002), "", "listMovies", "")
    addDir(translation(30003), "", "listTvShows", "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listMovies(url):
    addDir(translation(30004), baseUrl+"/c/video-on-demand/filme/p1/?v=l&r=50", 'listVideos', "")
    addDir(translation(30005), baseUrl+"/c/p1/?facet-2=collection_id|2171&v=l&r=50", 'listVideos', "")
    addDir(translation(30006), baseUrl+"/c/video-on-demand/filme/", "listGenres", "")
    addDir(translation(30007), baseUrl+"/c/video-on-demand/filme-sammlungen", "listCollections", "")
    addDir(translation(30008), "movies", "search", "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listTvShows(url):
    addDir(translation(30009), baseUrl+"/c/video-on-demand/fernsehfilme/p1/?v=l&r=50", 'listVideos', "")
    addDir(translation(30010), baseUrl+"/c/p1/?facet-2=collection_id|2730&v=l&r=50", 'listVideos', "")
    addDir(translation(30006), baseUrl+"/c/video-on-demand/fernsehfilme/", "listGenres", "")
    addDir(translation(30007), baseUrl+"/c/video-on-demand/tv-sammlungen", "listCollections", "")
    addDir(translation(30008), "tvshows", "search", "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listGenres(url):
    content = getUrl(url)
    content = content[content.find('<h3>Genre</h3>'):]
    content = content[:content.find('</li></ul></div>')]
    match = re.compile('<a href="(.+?)" title="(.+?)"><span class="facet_link">.+?</span> <span class="facet_results  ">(.+?)</span></a>', re.DOTALL).findall(content)
    urlNext = ""
    for url, title, nr in match:
        title = cleanTitle(title)
        addDir(title + nr, url+"?v=l&r=50", 'listVideos', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listCollections(url):
    content = getUrl(url)
    content = content[content.find('<div class="collection_items"'):]
    content = content[:content.find('<div class="page-footer bermuda-footer">')]
    match = re.compile('<a href="(.+?)">.+?<img src="(.+?)" width=".+?" height=".+?" />.+?<h3>(.+?)</h3>', re.DOTALL).findall(content)
    urlNext = ""
    for url, thumb, title in match:
        title = cleanTitle(title)
        addDir(title, url+"&v=l&r=50", 'listVideos', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideos(url):
    content = getUrl(url)
    if '<div class="core_info_snb' in content:
        splitStr = '<div class="core_info_snb'
    elif 'class="compact_info_snb' in content:
        splitStr = 'class="compact_info_snb'
    spl = content.split(splitStr)
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = match[0]
        match = re.compile('data-product_name="(.+?)"', re.DOTALL).findall(entry)
        match2 = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
        if match:
            title = match[0]
        elif match2:
            title = match2[0]
        title = cleanTitle(title)
        match = re.compile('<div class="synopsis "><p>(.+?)<', re.DOTALL).findall(entry)
        desc = match[0]
        match = re.compile('<span class="release_decade">(.+?)</span>', re.DOTALL).findall(entry)
        year = match[0].strip()
        match = re.compile('data-current_rating="(.+?)"', re.DOTALL).findall(entry)
        rating = ""
        if match:
            rating = match[0] + " / 5"
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = match[0].replace("_UX140_CR0,0,140", "_UX500").replace("_UR140,105", "_UX500").replace("_UR77,109", "_UX500")
        if rating:
          desc = "Year: "+year+"\nRating: "+rating+"\n"+desc
        else:
          desc = "Year: "+year+"\n"+desc
        if baseUrl+"/tv/" in url:
            addDir(title, url, 'listEpisodes', thumb, desc)
        else:
            if player=="0":
                addDir(title, url, 'playVideoBrowser', thumb, desc)
            elif player=="1":
                addDir(title, url, 'playVideoPlayer', thumb, desc)
    content = content[content.find('<span class="page_selected">'):]
    content = content[:content.find('</ul>')]
    match = re.compile('<a href="(.+?)"  >(.+?)</a>', re.DOTALL).findall(content)
    urlNext = ""
    for url, title in match:
        if "chste" in title:
            urlNext = url
    if urlNext:
        addDir(translation(30001), urlNext+"?v=l&r=50", "listVideos", "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listEpisodes(url):
    content = getUrl(url)
    content = content[content.find('<div class="list_episodes">'):]
    content = content[:content.find('</ul>')]
    matchFirst = re.compile('<span class="episode_link">(.+?)</span>', re.DOTALL).findall(content)
    match = re.compile('<a class="episode_link" href="(.+?)">(.+?)</a>', re.DOTALL).findall(content)
    urlNext = ""
    addDir(matchFirst[0], url, 'playVideo', "")
    for url, title in match:
        if player=="0":
            addDir(title, url, 'playVideoBrowser', "")
        elif player=="1":
            addDir(title, url, 'playVideoPlayer', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def search(type):
    keyboard = xbmc.Keyboard('', translation(30008))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText().replace(" ", "+")
        if type == "movies":
            listVideos(baseUrl+"/c/video-on-demand/filme/?q="+search_string+"&v=l&r=50")
        if type == "tvshows":
            listVideos(baseUrl+"/c/video-on-demand/fernsehfilme/?q="+search_string+"&v=l&r=50")


def playVideoPlayer(url):
    xbmc.Player().stop()
    subprocess.Popen(lfPlayerPath+' '+url, shell=False)


def playVideoBrowser(url):
    xbmc.Player().stop()
    xbmc.executebuiltin('RunPlugin(plugin://plugin.program.webbrowser/?url='+urllib.quote_plus(url)+'&mode=showSite)')


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#038;", "&").replace("&#39;", "'")
    title = title.replace("&#039;", "'").replace("&#8211;", "-").replace("&#8220;", "-").replace("&#8221;", "-").replace("&#8217;", "'")
    title = title.replace("&quot;", "\"").replace("&uuml;", "ü").replace("&auml;", "ä").replace("&ouml;", "ö")
    title = title.strip()
    return title


def getUrl(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:19.0) Gecko/20100101 Firefox/19.0')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addDir(name, url, mode, iconimage, desc=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    if useCoverAsFanart:
      liz.setProperty("fanart_image", iconimage)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))

if mode == 'listVideos':
    listVideos(url)
elif mode == 'listMovies':
    listMovies(url)
elif mode == 'listGenres':
    listGenres(url)
elif mode == 'listCollections':
    listCollections(url)
elif mode == 'listEpisodes':
    listEpisodes(url)
elif mode == 'listTvShows':
    listTvShows(url)
elif mode == 'playVideoPlayer':
    playVideoPlayer(url)
elif mode == 'playVideoBrowser':
    playVideoBrowser(url)
elif mode == 'search':
    search(url)
else:
    index()
