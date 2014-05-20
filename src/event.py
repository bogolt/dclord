import wx
import wx.lib.newevent

#src-data, dest_file
DataDownload, EVT_DATA_DOWNLOAD = wx.lib.newevent.NewEvent()
MapUpdate, EVT_MAP_UPDATE = wx.lib.newevent.NewEvent()
UserSelect, EVT_USER_SELECT = wx.lib.newevent.NewEvent()
ActionsReply, EVT_ACTIONS_REPLY = wx.lib.newevent.NewEvent()
SelectObject, EVT_SELECT_OBJECT = wx.lib.newevent.NewEvent()
TurnSelected, EVT_TURN_SELECTED = wx.lib.newevent.NewEvent()
LogAppend, EVT_LOG_APPEND = wx.lib.newevent.NewEvent()
JumpFleet, EVT_FLEET_JUMP = wx.lib.newevent.NewEvent()
BuildUnit, EVT_BUILD_UNIT = wx.lib.newevent.NewEvent()
