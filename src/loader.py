import wx
import httplib
from threading import Thread
import urllib
import os.path
import event
import logging
import config
import unicodedata 

log = logging.getLogger('dclord')

class AsyncLoader(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.args = []
		
	def run(self):
		log.info('async loader started')
		tmp_args, self.args = self.args, []
		for arg in tmp_args:
			self.query(arg)
		if tmp_args:
			wx.PostEvent(tmp_args[0]['cb'], event.DataDownload(attr1=None, attr2=None))
		
	def query(self, args):
		key = args['key']
		cb = args['cb']
		log.info('async-loader executing query %s'%(args,))
		conn = httplib.HTTPConnection(args['host'])
		conn.set_debuglevel(int(config.options['network']['debug']))
		conn.request(args['query_type'], args['query'], args['opts'])
		r = conn.getresponse()
		if r.status != 200:
			wx.PostEvent(cb, event.DataDownload(attr1=key, attr2=None))
			return False

		log.info('req, ok, reading body')
		out = args['outpath']
		with open(out,'wb') as f:
			f.write(r.read())

		log.info('response read, closing connection')
		#don't forget to close http connection
		conn.close()
		wx.PostEvent(cb, event.DataDownload(attr1=key, attr2=out))
		return True
	
	def getDcData(self, cb, login, data_type, out_dir, custom_opts = None):
		srv_dir = 'perform_x_actions' if custom_opts else 'empire_info'
		query = '/frames/%s/on/%s/asxml/'%(srv_dir, data_type,)
		opts = 'login=%s&pwd=%s&action=login'%(urllib.quote(login.encode('utf-8')),urllib.quote((config.users[login]['password']).encode('utf-8')))
		if custom_opts:
			opts += '&xactions=%s'%(custom_opts,)
		
		# work around sax parser bug with inability to read unicode file names ( cyrillic for example ) 
		# see http://bugs.python.org/issue11159
		name = '%s_%s.xml.gz'%(login.encode('ascii', 'ignore'), data_type)	
		args = {'host':config.options['network']['host'], 'cb':cb, 'query_type':'POST', 'query':query, 'opts':opts, 'key':login, 'outpath':os.path.join(out_dir, name)}
		
		self.args.append(args)
		
	def getUserInfo(self, cb, login, out_dir = None):
		d = os.path.join(wx.GetTempDir(), 'raw_data') if not out_dir else out_dir
		self.getDcData(cb, login, 'all', d)
		if bool(config.options['data']['load_known_planets']):
			self.getDcData(cb, login, 'known_planets', d)
		
	def sendActions(self, cb, login, actions, out_dir):
		d = os.path.join(wx.GetTempDir(), 'raw_data') if not out_dir else out_dir
		self.getDcData(cb, login, data_type='1', out_dir=d, custom_opts = actions)
	
	def recvFile(self, q, out):		
		self.queueQuery(query=q, opts=None, query_type='GET', outpath=out)	
	
	def queueQuery(self, *opts, **kvo):
		self.args.append(kvo)
