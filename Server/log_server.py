import rpclib
import sys
import logger
import auth

class LogRpcServer(rpclib.RpcServer):
    
    def rpc_log(self, msg, username, token):
    	logger.log(msg)




(_, dummy_fyreboxld_fd, sockpath) = sys.argv

s = LogRpcServer()
s.run_sockpath_fork(sockpath)

