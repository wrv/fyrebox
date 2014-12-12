import logging
from datetime import *

#initalizes the file for the log
def main():
	logging.basicConfig(filename='events.log',level=logging.DEBUG)
	#log('testing the logger')


def log(source, msg):
	time =  datetime.now().isoformat(' ')
	logging.info(source + ' >> ' + msg + ' -- %s' % (time))



#start logging
#if __name__ == '__main__':
#    main()