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
	
	resp = {}
	#setup of the databases
	userdb = user_setup()
	user = userdb.query(User).filter(User.name == username).first()
	filedb = file_setup()
	permdb = permission_setup()

	#get a reference to the parent directory we're working in
	parent_dir = filedb.query(File).filter(File.filename == dirname).first()
	if parent_dir:
		parent_id = parent_dir.id
	else:
		parent_id = 0

	#generate the fileID from various variables
	fileID = hashlib.sha256(username + token + filename + dirname + str(time.time())+ str(random.random())).hexdigest()
	#create the file
	newfile = File(identifier=fileID, filename=filename, parent_id=parent_id, owner_id=user.id, content="", directory=False)
	filedb.add(newfile)
	filedb.commit()
	
	#create the permissions for the file
	newperm = Permission_Assoc(user_id=user.id, file_id=newfile.id, perm_type=True)

	
	permdb.add(newperm)
	permdb.commit()

	resp["message"] = "success"
	resp["file_id"] = fileID

	return resp

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

	resp = {}
	userdb = user_setup()
	user = userdb.query(User).filter(User.name == username).first()

	filedb = file_setup()
	file = filedb.query(File).filter(File.identifier == fileid).first()
	
	if file.filename != filename:
		resp["new_filename"] = file.filename

	permdb = permission_setup()
	if file:
		permission = permdb.query(Permission_Assoc).get((user.id, file.id))

		if permission:
			if permfile.perm_type: #if they have write permissions
				file.delete()
				filedb.commit()
				resp["message"] = "success"
				return resp
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

	resp = {}
	userdb = user_setup()
	user = userdb.query(User).filter(User.name == username).first()
	filedb = file_setup()

	file = filedb.query(File).filter(File.identifier == fileid).first()

	if file.filename != filename:
		resp["new_filename"] = file.filename

	permdb = permission_setup()
	if file: 
		
		permfile = permdb.query(Permission_Assoc).get((user.id, file.id))

		# if in the permissions database they have the permission to read
		if permfile:
			resp["content"] = file.content
			resp["message"] = "success"
			return resp

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

	resp = {}
	#check permission
	userdb = user_setup()
	user = userdb.query(User).filter(User.name == username).first()
	filedb = file_setup()
	file = filedb.query(File).filter(File.identifier == fileid).first()

	if file.filename != filename:
		resp["new_filename"] = file.filename

	permdb = permission_setup()
	if file:
		permfile = permdb.query(Permission_Assoc).get((user.id, file.id))

		if permfile.perm_type:
			file.content = content
			filedb.commit()
			resp["message"] = "success"
			return resp

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

	resp = {}
	userdb = user_setup()
	user = userdb.query(User).filter(User.name == username).first()
	filedb = file_setup()
	file = filedb.query(File).filter(File.identifier == fileid).first()


	permdb = permission_setup()
	if file:
		permfile = permdb.query(Permission_Assoc).get((user.id, file.id))
		if permfile.perm_type:
			if filedb.query(File).filter(File.filename == newfilename).first():
				return False
			else:
				file.filename = newfilename
				filedb.commit()
				resp["message"] = "success"
				return resp

	return False

##
# perm(filename, perms, username, token)
#
# filename - the encrypted name of the file we want to change permissions to
# perms - (bolean value, other username)
# username - username of the person
# token - the token of the person
#
# Checks the token, check that username is the correct owner, add the
# encrypted key into the permissions database for the user
#
def perm(fileid, filename, perms, username, token):
	if not check_token(username, token):
		return False

	resp = {}
	userdb = user_setup()
	owner = userdb.query(User).filter(User.name == username).first()
	other_user = userdb.query(User).filter(User.name == perms[1]).first()
	filedb = file_setup()
	file = filedb.query(File).filter(File.identifier == fileid).first()
	
	if file.filename != filename:
		resp["new_filename"] = file.filename


	permdb = permission_setup()
	if file:
		if file.owner_id == owner.id:
			permission = Permission_Assoc(user_id=other_user.id, file_id=file.id, perm_type=perms[0])
			permdb.add(permission)
			permdb.commit()
			resp["message"] = "success"
			return resp

	return False


