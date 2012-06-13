import wx
import wx.lib.newevent

#src-data, dest_file
DataDownload, EVT_DATA_DOWNLOAD = wx.lib.newevent.NewEvent()
MapUpdate, EVT_MAP_UPDATE = wx.lib.newevent.NewEvent()
UserSelect, EVT_USER_SELECT = wx.lib.newevent.NewEvent()
