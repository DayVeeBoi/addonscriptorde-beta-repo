#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmc

#Because of too frequent site changes, i now decided to simply use the youtube channel (vids on site are also hosted on youtube)
xbmc.executebuiltin('Container.Update(plugin://plugin.video.youtube.channels/?mode=listVideos&url=TagesWEBschau#1#published)')
