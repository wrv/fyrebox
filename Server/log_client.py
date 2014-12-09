import rpclib

def log(msg, token): 
	connection = rpclib.client_connect('/logsvc/sock')
	kwarg = {}
	kwarg['msg'] = msg
	kwarg['token'] = token
	return connection.call('log', **kwarg)