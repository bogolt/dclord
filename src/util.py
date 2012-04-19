import gzip
import os
import os.path

def unpack(path_in, path_out):
	f = gzip.open(path_in, 'rb')
	with open(path_out, 'wb') as out:
		out.write(f.read())
	f.close()

def assureDirExist(d):
	if os.path.exists(d):
		return
	os.makedirs(d)
