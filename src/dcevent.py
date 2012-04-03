import wx
import wx.lib.newevent

ObjectFocus, EVT_OBJECT_FOCUS = wx.lib.newevent.NewEvent()

Report, EVT_REPORT = wx.lib.newevent.NewEvent()

LoaderEvent, EVT_LOADER = wx.lib.newevent.NewEvent()

SetMapPosEvent, EVT_SET_MAP_POS = wx.lib.newevent.NewEvent()
