import wx
import wx.lib.newevent

EVT_OBJECT_FOCUS = 1001

ObjectFocus, EVT_OBJECT_FOCUS = wx.lib.newevent.NewEvent()

EVT_REPORT = 1002

Report, EVT_REPORT = wx.lib.newevent.NewEvent()

EVT_LOADER = 1003

LoaderEvent, EVT_LOADER = wx.lib.newevent.NewEvent()
