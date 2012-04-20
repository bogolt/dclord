import wx
import main_frame
import config

if __name__ == '__main__':
	app = wx.App()
	app.SetAppName('dcLord')
	config.loadAll()
	
	frame = main_frame.DcFrame(None)
	frame.Show(True)
	app.MainLoop()
