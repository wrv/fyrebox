import log_client
from db import *
from auth import check_token
import hashlib
import random
import time


##
# create(filename, username, token)
#
# filename - the encrypted name of the file we want to create
# username - username of the person
# token - the token of the person
#
# Checks the token, creates a new entry in the file database
# responds with a success/failure based on if the file already exists
#
def create(filename, dirname, username, token):
	#token checking for verification
	if not check_token(username, token):
		return False
	
	#setup of the databases
	filedb = file_setup()
	permdb = permission_setup()
	directorydb = directory_setup()

	#get a reference to the parent directory we're working in
	parent_dir = directorydb.query(Directory).get(dirname)

	#generate the fileID from various variables
	fileID = hashlib.sha256(username + token + filename + dirname + str(time.time())+ str(random.random())).hexdigest()
	#create the file
	newfile = File(fileID, username, filename, "", parent_dir.id)

	#create the permissions for the file
	newperm = Permission(None, True, username, fileID)

	filedb.add(newfile)
	filedb.commit()
	permdb.add(newperm)
	permdb.commit()

	return fileID

##
# delete(filename, username, token)
#
# filename - the encrypted name of the file we want to delete
# username - username of the person
# token - the token of the person
#
# Checks the token, checks write permission on file and all files inside
# of folder. Remove corresponding file. Respond with success/failure.
#
def delete(fileid, filename, username, token):
	if not check_token(username, token):
		return False
	#check permissions
	permdb = permission_setup()
	permfile = permdb.query(Permission).get(filename)

	if username in permfile.users_write:
		filedb = file_setup()
		delfile = db.query(File).get(filename)
		#if file does not exist assume it's already deleted
		if not delfile:
			return True

		filedb.remove(delfile)
		filedb.commit()
		return True
	return False

##
# read(filename, username, token)
#
# filename - the encrypted name of the file we want to read
# username - username of the person
# token - the token of the person
#
# Checks the token, check read permission on file. Send json data
# of {op: read, filename=name, content=content, perm=(username, E_pk(key))}
#
def read(fileid, filename, username, token):
	if not check_token(username, token):
		return False

	#check permission
	permdb = permission_setup()
	permfile = permdb.query(Permission).get(filename)

	if username in permfile.users_read:
		filedb = file_setup()
		datfile = db.query(File).get(filename)
		#if file exists return its contents
		if datfile:
			return datfile.content

	return False



##
# write(filename, content, username, token)
#
# filename - the encrypted name of the file we want to write to
# username - username of the person
# token - the token of the person
#
# Checks the token, check write permission on file, overwrite content with
# new content, respond with success/failure
#
def write(fileid, filename, content, username, token):
	if not check_token(username, token):
		return False

	#check permission
	permdb = permission_setup()
	permfile = permdb.query(Permission).get(filename)

	if username in permfile.users_write:
		filedb = file_setup()
		datfile = db.query(File).get(filename)
		#if file exists return its contents
		if datfile:
			datfile.content = content
			return True

	return False

##
# rename(oldname, newName, username, token)
#
# oldName - the encrypted name of the file we want to rename
# newName - the new encrypted title we want to give a file
# username - username of the person
# token - the token of the person
#
# Checks the token, check write permissions, overwrite filename, respond 
# success or failure
#
def rename(fileid, newfilename, username, token):
	if not check_token(username, token):
		return False

##
# perm(filename, perms, username, token)
#
# filename - the encrypted name of the file we want to change permissions to
# perms - a tuple of user, permission, and secret key
# username - username of the person
# token - the token of the person
#
# Checks the token, check that username is the correct owner, add the
# encrypted key into the permissions database for the user
#
def perm(fileid, filename, perms, username, token):
	if not check_token(username, token):
		return False
