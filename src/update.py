import network
import threading
import os
import sys

class Update(threading.Thread):
	def __init__(self, cb, conf):
		threading.Thread.__init__(self)
		self.cb = cb
		self.conf = conf
		
		#self.start()
		
	def run(self):
		cf = self.conf.s['update']
		hash_str = network.http_load(cf['host'], cf['url_binary_hash'])
		
		
		print 'current version string %s'%(hash_str,)


#u = Update(1,2,3)

print 'file is %s'%(__file__,)
print 'argv0 is %s'%(sys.argv[0],)
print 'path is %s'%(os.getcwd(),)
