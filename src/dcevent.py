import wx
import wx.lib.newevent

ObjectFocus, EVT_OBJECT_FOCUS = wx.lib.newevent.NewEvent()

Report, EVT_REPORT = wx.lib.newevent.NewEvent()

LoaderEvent, EVT_LOADER = wx.lib.newevent.NewEvent()

SetMapPosEvent, EVT_SET_MAP_POS = wx.lib.newevent.NewEvent()

RequestActionPerform,EVT_REQUEST_ACTION_PERFORM = wx.lib.newevent.NewEvent()
SelectUnit,EVT_SELECT_UNIT = wx.lib.newevent.NewEvent()
