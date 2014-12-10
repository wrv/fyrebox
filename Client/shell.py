import cmd
import sys

from client import login

class FyreBoxShell(cmd.Cmd):
    intro  = 'Welcome to the fyrebox shell.   Type help or ? to list commands.\n'
    prompt = 'fyrebox> '
    undoc_header = 'Alias commands'
    doc_header = 'Commands (type help <command> for more information)'
    MIN_FILENAME_LEN = 5
    SPECIAL_COMMANDS = ['?', 'help', 'eof', 'exit', 'quit']
    logged_in = False

    def __init__(self, *args, **kwargs):
        cmd.Cmd.__init__(self,*args, **kwargs)
        self.initialize_connections()

    def initialize_connections(self):
        #self.initialize_file_server_connection()
        #self.initialize_file_server_connection()
        pass

    #def initialize_file_server_connection(self):
        #'Ran during __init__. Attempts to connect to file server'
        #context = SSL.Context(SSL.SSLv23_METHOD)
        #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #s.connect(('localhost', 10023))
        ##sslSocket = socket.ssl(s)
        ##response = sslSocket.read()
        #self.server_socket = socket.ssl(s) # socket to file server

    #def initialize_cloud_server_connection(self):
        #'Ran during __init__. Attempts to connect to cloud server'
        #context = SSL.Context(SSL.SSLv23_METHOD)
        #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #s.connect(('localhost', 10023))
        ##sslSocket = socket.ssl(s)
        ##response = sslSocket.read()
        #self.server_socket = socket.ssl(s) # socket to file server
    
    def do_create(self, arg):
        'Create a new file: CREATE <filename>'
        if len(arg) < self.MIN_FILENAME_LEN:
            self.print_error("ERROR. Usage CREATE <filename>. Make sure filename is at "
                    "least %d charachters long" % (self.MIN_FILENAME_LEN))
            return
        self.print_success("File created")

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

    def do_register(self, arg):
        'Register with fyrebox: REGISTER'
        pass

    def do_login(self, arg):
        'Login to fyrebox: LOGIN'
        pass

    def print_error(self, msg):
        "Prints red message with a newline at the end"
        sys.stderr.write('\033[91m'+msg+'\033[0m \n')

    def print_success(self, msg):
        "Prints green message with a newline at the end"
        sys.stdout.write('\033[92m'+msg+'\033[0m \n')

    #------- hook functions ---------
    def emptyline(self):
        # do nothing
        pass

    def precmd(self, line):
        if not self.logged_in:
            command  = line.lower()
            # check if command is special
            if any([command.startswith(x) for x in self.SPECIAL_COMMANDS]):
                #return line
                return cmd.Cmd.precmd(self, line)

            if all([x not in command  for x in ['login', 'register']]):
                self.print_error(
                        "Please login or register to continue. Type ? for help")
                return '' # clear command to force login

        return cmd.Cmd.precmd(self, line)

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