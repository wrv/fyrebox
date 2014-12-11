import log_client
from db import *
from auth import check_token
import hashlib
import random
import time


##
# createdir(dirname, username, token)
#
# dirname - the encrypted name of the directory we want to create
# username - username of the person
# token - the token of the person
#
# Checks the token, creates a new entry in the file database
# responds with a success/failure based on if the directory already exists
#
def createdir(dirname, parentdir, username, token):
	if not check_token(username, token):
		return False

	#setup of the databases
	userdb = user_setup()
	user = userdb.query(User).filter(User.name == username).first()
	filedb = file_setup()
	permdb = permission_setup()

	#get a reference to the parent directory we're working in
	parent_dir = filedb.query(File).filter(File.filename == parentdir).first()
	if parent_dir:
		parent_id = parent_dir.id
	else:
		parent_id = 0

	#generate the dir_id from various variables
	dir_id = hashlib.sha256(username + token + dirname + parentdir + str(time.time())+ str(random.random())).hexdigest()
	#create the directory
	newdir = File(identifier=dir_id, filename=dirname, parent_id=parent_id, owner_id=user.id, content="", directory=True)
	filedb.add(newdir)
	filedb.commit()
	
	#create the permissions for the file
	newperm = Permission_Assoc(user_id=user.id, file_id=newdir.id, perm_type=True)

	
	permdb.add(newperm)
	permdb.commit()

	return dir_id

##
# deletedir(dirname, username, token)
#
# dirname - the encrypted name of the dir we want to delete
# username - username of the person
# token - the token of the person
#
# Checks the token, checks write permission on dir and all files inside
# of folder. Remove corresponding dir. Respond with success/failure.
#
def deletedir(dirid, dirname, username, token):
	if not check_token(username, token):
		return False
	#check permissions
	userdb = user_setup()
	user = userdb.query(User).filter(User.name == username).first()

	filedb = file_setup()
	directory = filedb.query(File).filter(File.identifier == dirid).first()
	
	permdb = permission_setup()
	if directory:
		permission = permdb.query(Permission_Assoc).get((user.id, directory.id))

		if permission:
			if permfile.perm_type: #if they have write permissions
				directory.delete()
				filedb.commit()
				return True
	return False

##
# readdir(dirname, username, token)
#
# dirname - the encrypted name of the dir we want to read
# username - username of the person
# token - the token of the person
#
# Checks the token, check read permission on dir. For every file
# in the directory, send the name of the directory. Send json data
# of {op: readdir, dirname=[file names name], perm=(username, E_pk(key))}
#
def readdir(dirid, dirname, username, token):
	pass

##
# renamedir(oldName, newName, username, token)
#
# oldName - the encrypted name of the dir we want to rename
# newName - the new encrypted title we want to give a dir
# username - username of the person
# token - the token of the person
#
# Checks the token, check write permissions, overwrite dirname, respond 
# success or failure
#
def renamedir(dirid, dirname, username, token):
	pass

##
# permdir(dirname, perms, username, token)
#
# dirname - the encrypted name of the dir we want to change permissions on
# perms - a tuple of user, permission, and secret key
# username - username of the person
# token - the token of the person
#
# Checks the token, check that username is the correct owner, add the
# encrypted key into the permissions database for the directory
#
def permdir(dirid, dirname, perms, username, token):
	pass
