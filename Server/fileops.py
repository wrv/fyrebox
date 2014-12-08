import logging
from db import *
from auth import check_token

##
# create(fileName, username, token)
#
# fileName - the encrypted name of the file we want to create
# username - username of the person
# token - the token of the person
#
# Checks the token, creates a new entry in the file database
# responds with a success/failure based on if the file already exists
#
def create(fileName, username, token):
	if not check_token(username, token):
		return False
	filedb = file_setup()
	newfile = File()
	newfile.filename = fileName
	newfile.owner_id = 5

	return True

##
# delete(fileName, username, token)
#
# fileName - the encrypted name of the file we want to delete
# username - username of the person
# token - the token of the person
#
# Checks the token, checks write permission on file and all files inside
# of folder. Remove corresponding file. Respond with success/failure.
#
def delete(fileName, username, token):
	if not check_token(username, token):
		return False

##
# read(fileName, username, token)
#
# fileName - the encrypted name of the file we want to read
# username - username of the person
# token - the token of the person
#
# Checks the token, check read permission on file. Send json data
# of {op: read, filename=name, content=content, perm=(username, E_pk(key))}
#
def read(fileName, username, token):
	if not check_token(username, token):
		return False

##
# write(fileName, content, username, token)
#
# fileName - the encrypted name of the file we want to write to
# username - username of the person
# token - the token of the person
#
# Checks the token, check write permission on file, overwrite content with
# new content, respond with success/failure
#
def write(fileName, content, username, token):
	if not check_token(username, token):
		return False

##
# rename(oldname, newName, username, token)
#
# oldName - the encrypted name of the file we want to rename
# newName - the new encrypted title we want to give a file
# username - username of the person
# token - the token of the person
#
# Checks the token, check write permissions, overwrite fileName, respond 
# success or failure
#
def rename(oldName, newName, username, token):
	if not check_token(username, token):
		return False

##
# perm(fileName, perms, username, token)
#
# fileName - the encrypted name of the file we want to change permissions to
# perms - a tuple of user, permission, and secret key
# username - username of the person
# token - the token of the person
#
# Checks the token, check that username is the correct owner, add the
# encrypted key into the permissions database for the user
#
def perm(fileName, perms, username, token):
	if not check_token(username, token):
		return False
