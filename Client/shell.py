#! /usr/bin/env python
import cmd
import sys
import getpass
import traceback
from client import Client
from settings import CLIENT_DEBUG as DEBUG


class FyreBoxShell(cmd.Cmd):
    intro = """
                                                                                                    
   ;kkkkkkkk,  okk.    dkk .kkkkkkkkkkkkc  ckkkkkkkk..WWWWWWWWWWW:   lWWWWWWWWWWWl  0WW.    KWN     
   ;kkl'''''.  oOk.    dkk  :kkd''''':kkl  ckkc'''''  :WMW::::0MM:   lMMO:::::OMMl  KMM.    XMW     
   ;kkc.....   oOk.    dkk  .kko.....;kkl  ckO:.....   NMN''''kMMo.  lMMd     dMMl  OMMx:',oWMK     
   ;kkkkkkkk;  oOk.    dkk  .kkkkkkkkkkkl  ckkkkkkkk.  NMMMMMMMMMMK  lMMd     dMMl   ,0MMMMMK;      
   ;kkc.....   oOkdddddkkk  .kko...dkkl.   ckO;.....   NMN.....'MMK  lMMd     dMMl  0MMd,.'lWMN     
   ;kk:        ,;;;;;;;xkk  .kkl    okkc   ckkl;;;;;   NMWllllloMMK  lMM0lllll0MMl  KMM.    XMW     
   ,xx;                xkd  .xxc     lkkl  :xxxxxxxx.  KXXXXXXXXXXO  cXXXXXXXXXXXc  OXX.    0XK     
                     .dkd             ckx.                                                          
                    .xko               .                                                            
                     ';                                                                             
                                                                                                    

    """
    prompt = 'fyrebox> '
    undoc_header = 'Alias commands'
    doc_header = 'Commands (type help <command> for more information)'
    MIN_FILENAME_LEN = 2
    SPECIAL_COMMANDS = ['?', 'help', 'eof', 'exit', 'quit']
    logged_in = False

    def __init__(self, *args, **kwargs):
        cmd.Cmd.__init__(self,*args, **kwargs)
        try:
            self.client = Client()
        except Exception as e:
            if DEBUG:
                print e
            self.print_error(
                    "Sorry. Failed to connect to server."
                    "" + str(e)
                    )
            sys.exit(1)

    
    def do_create(self, arg):
        'Create a new file: CREATE <filename>'
        if len(arg) < self.MIN_FILENAME_LEN:
            self.print_error("ERROR. Usage CREATE <filename>. Make sure filename is at "
                    "least %d charachters long" % (self.MIN_FILENAME_LEN))
            return
        try:
            self.client.create(arg)
            self.print_success("Create successful.")
        except:
            traceback.print_exc()
            self.print_error("Create failed. Please retry.")

    def do_quit(self, arg):
        'Exit from the fyrebox shell: QUIT'
        sys.stdout.write("\n") # new line 
        sys.exit(0)

    def do_ls(self, arg):
        'List files'
        contents = self.client.read_dir(self.client.current_directory)
        print contents

    def do_rm(self, arg):
        'Remove a file: RM'
        if len(arg) < self.MIN_FILENAME_LEN:
            self.print_error("ERROR. Usage RM <filename>. Make sure filename is at least %d charachters long" % (self.MIN_FILENAME_LEN))
            return
        try:
            self.client.delete(arg)
            self.print_success("Rm successful.")
        except Exception as e:
            if DEBUG:
                print e
            self.print_error("Rm failed. Please retry.")
        
    def do_perm(self, arg):
        'Get file permissions: PERM'
        pass

    def do_rename(self, old_file_name):
        'Rename a file: RENAME'
        new_file_name = self.prompt_get('file_name')
        try:
            self.client.rename(old_file_name.strip(), new_file_name.strip())
            self.print_success("Rename successful.")
        except:
            self.print_error("Rename failed. Please retry.") 
    def do_write(self, filename):
        'Write file: WRITE <filename>'
        if not filename:
            filename = self.prompt_get('filename')
        if len(filename.split())> 1:
            self.print_error("ERROR. Usage WRITE <filename>."
                    " Do not include content.")
            return
        filename = filename.strip()
        content = self.prompt_get('content')
        try:
            self.client.write(filename, content)
            self.print_success("Content successfully written.")
        except:
            traceback.print_exc()
            self.print_error("Sorry. Writing content failed. "
                    "Please retry")

    def do_read(self, filename):
        'Read file: READ <filename>'
        if not filename:
            filename = self.prompt_get('filename')
        if len(filename.split())> 1:
            self.print_error("ERROR. Usage READ <filename>.")
            return
        filename = filename.strip()
        try:
            results = self.client.read(filename)
            self.print_success( "CONTENT : \n"
                                "============"
                    )
            print results['content']
        except:
            traceback.print_exc()
            self.print_error("Sorry. Reading content failed. "
                    "Please retry")

    def do_register(self, username):
        'Register with fyrebox: REGISTER <username>'
        if not username:
            username = self.prompt_get('username')

        if len(username.split())> 1:
            self.print_error("ERROR. Usage REGISTER <username>."
                    " Do not include password.")
            return
        username = username.strip()
        password = self.prompt_get_password()

        try:
            self.client.register(username, password)
            self.print_success('User with username: ' + username + ""
                " successfully registered. ")
            # registration automatically logs in
            self.logged_in = True
            self.prompt = str(self.client.username) + '@fyrebox> '
        except Exception as e:
            if DEBUG:
                print e
            self.print_error('An error occurred. Please retry')


    def do_login(self, username):
        'Login to fyrebox: LOGIN <username>'

        if len(username) < 1:
            username = self.prompt_get('username')

        if len(username.split())> 1:
            self.print_error("ERROR. Usage LOGIN <username>."
                    " Do not include password.")
            return

        username = username.strip()
        password = self.prompt_get_password()

        try:
            self.client.login(username, password)
            self.print_success('User with username: ' + username + ""
                " successfully logged in. ")
            self.logged_in = True
            self.prompt = str(self.client.username) + '@fyrebox> '
        except Exception as e:
            self.print_error('An error occurred. Please retry')

    def do_mkdir(self, arg):
        'Create a directory'
        if len(arg) < self.MIN_FILENAME_LEN:
            self.print_error("ERROR. Usage MKDIR <dirname>. Make sure dirname is at "
                    "least %d charachters long" % (self.MIN_FILENAME_LEN))
            return
        try:
            self.client.create_dir(arg)
            self.print_success("Create successful.")
        except:
            if DEBUG: traceback.print_exc()
            self.print_error("Create failed. Please retry.")


    #----- util functions -----
    def prompt_get(self, param):
        data = None
        while not data:
            data = raw_input(param + ' : ')
        return data

    def prompt_get_password(self):
        password = None
        while not password:
            password = getpass.getpass()
        return password

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
