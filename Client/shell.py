import cmd
import sys

class FyreBoxShell(cmd.Cmd):
    intro  = 'Welcome to the fyrebox shell.   Type help or ? to list commands.\n'
    prompt = 'fyrebox> '
    undoc_header = 'Alias commands'
    doc_header = 'Commands (type help <command> for more information)'
    MIN_FILENAME_LEN = 5

    #def __init__(self, *args, **kwargs):
        ##super(FyreBoxShell, self).__init__()
        #self.initialize_connections()

    def initialize_connections(self):
        self.initialize_file_server_connection()
        self.initialize_file_server_connection()

    def initialize_file_server_connection(self):
        'Ran during __init__. Attempts to connect to file server'
        context = SSL.Context(SSL.SSLv23_METHOD)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect(('localhost', 10023))
        #sslSocket = socket.ssl(s)
        #response = sslSocket.read()
        self.server_socket = socket.ssl(s) # socket to file server

    def initialize_cloud_server_connection(self):
        'Ran during __init__. Attempts to connect to cloud server'
        context = SSL.Context(SSL.SSLv23_METHOD)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect(('localhost', 10023))
        #sslSocket = socket.ssl(s)
        #response = sslSocket.read()
        self.server_socket = socket.ssl(s) # socket to file server
    
    def do_create(self, arg):
        'Create a new file: CREATE <filename>'
        if len(arg) < self.MIN_FILENAME_LEN:
            self.print_error("ERROR. Usage CREATE <filename>. Make sure filename is at "
                    "least %d charachters long" % (self.MIN_FILENAME_LEN))
            return
        self.print_success("File created")
        pass

    def do_quit(self, arg):
        'Exit from the fyrebox shell: QUIT'
        sys.stdout.write("\n") # new line 
        sys.exit(0)

    def do_rm(self, arg):
        'Remove a file: RM'
        pass

    def do_perm(self, arg):
        'Get file permissions: PERM'
        pass

    def do_rename(self, arg):
        'Rename a file: RENAME'
        pass

    def do_write(self, arg):
        'Write file: WRITE'
        pass

    def register(self, arg):
        'Register with fyrebox: REGISTER'
        pass

    def login(self, arg):
        'Login to fyrebox: LOGIN'
        pass

    def print_error(self, msg):
        "Prints red message with a newline at the end"
        sys.stderr.write('\033[93m'+msg+'\033[0m\n')

    def print_success(self, msg):
        "Prints green message with a newline at the end"
        sys.stdout.write('\033[92m'+msg+'\033[0m\n')

    #------- alias functions for better usability -------

    def do_EOF(self, arg):
        self.do_quit(arg)
    
    def do_exit(self, arg):
        self.do_quit(arg)

    def do_bye(self, arg):
        self.do_quit(arg)

    def do_ren(self, arg):
        self.do_rename(arg)

    def do_remove(self, arg):
        self.do_rm(arg)


if __name__ == '__main__':
    FyreBoxShell().cmdloop() # loop forever
