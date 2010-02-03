import ftplib
from threading import Thread

class Update(Thread):
	def __init__(self, cb, conf, v):
		Thread.__init__(self)
		self.cb = cb
		self.conf = conf
		
		self.start()
		
	def run(self):
		cf = self.conf.s['update']
		ftp = ftplib.FTP()
		ftp.set_debuglevel(cf['debug'])
		try:
			ftp.connect(cf['host'])
			ftp.login(cf['user'], cf['password'])
			print max(ftp.nlst()) 
		except Exception, e:
			print 'update error %s'%(e,)
