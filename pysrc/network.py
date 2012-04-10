import logging
import httplib

log = logging.getLogger('dclord')

def http_load(host, url):
	conn = httplib.HTTPConnection(host)
	conn.request('GET',url)
	r = conn.getresponse()
	if r.status != 200:
		log.error('Cannot fetch url %s %s'%(host, url))
		return False

	return r.read()
