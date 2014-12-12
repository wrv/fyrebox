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
	resp = {}
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

	resp["message"] = "success"
	resp["dir_id"] = dir_id

	return resp

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

	resp = {}
	#check permissions
	userdb = user_setup()
	user = userdb.query(User).filter(User.name == username).first()

	filedb = file_setup()
	directory = filedb.query(File).filter(File.identifier == dirid).first()

	if directory.filename != dirname:
		resp["new_dirname"] = directory.filename
	
	permdb = permission_setup()
	if directory:
		permission = permdb.query(Permission_Assoc).get((user.id, directory.id))

		if permission:
			if permfile.perm_type: #if they have write permissions
				#delete the files in the directory and it's contents
				delete_contents(directory, filedb, permdb)

				filedb.delete(directory)
				filedb.commit()

				permdb.query(Permission_Assoc).filter(Permmission_Assoc.file_id == directory.id).delete()
				permdb.commit()
				resp["message"] = "success"
				return resp
	return False

def delete_contents(directory, filedb, permdb):
	subcontent = filedb.query(File).filter(File.parent_id == directory.id)
	for filedir in subcontent:
		if filedir.directory:
			content = filedb.query(File).filter(File.parent_id == filedir.id)
			for file in content:
				delete_contents(file, db)
		else:
			filedb.delete(subcontent)
			filedb.commit()
			permdb.query(Permission_Assoc).filter(Permmission_Assoc.file_id == subcontent.id).delete()
			permdb.commit()



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
	if not check_token(username, token):
		return False

	resp = {}
	userdb = user_setup()
	user = userdb.query(User).filter(User.name == username).first()
	filedb = file_setup()

	directory = filedb.query(File).filter(File.identifier == dirid).first()

	if directory.filename != dirname:
		resp["new_dirname"] = directory.filename	

	permdb = permission_setup()
	if directory: 
		
		permfile = permdb.query(Permission_Assoc).get((user.id, directory.id))

		# if in the permissions database they have the permission to read
		if permfile:
			subfilesdir = filedb.query(File).filter(File.parent_id == directory.id)
			content = []
			for file in subfilesdir:
				content.append(file.identifier)

			resp["content"] = content
			resp["message"] = "success"
			return resp

	return False

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
	if not check_token(username, token):
		return False

	resp = {}
	userdb = user_setup()
	user = userdb.query(User).filter(User.name == username).first()
	filedb = file_setup()
	directory = filedb.query(File).filter(File.identifier == dirid).first()

	permdb = permission_setup()
	if directory:
		permfile = permdb.query(Permission_Assoc).get((user.id, directory.id))
		if permfile.perm_type:
			if filedb.query(File).filter(File.filename == dirname).first():
				return False
			else:
				directory.filename = dirname
				filedb.commit()
				resp["message"] = "success"
				return resp

	return False

##
# permdir(dirname, perms, username, token)
#
# dirname - the encrypted name of the dir we want to change permissions on
# perms - (bolean value, other username, key)
# username - username of the person
# token - the token of the person
#
# Checks the token, check that username is the correct owner, add the
# encrypted key into the permissions database for the directory
#
def permdir(dirid, dirname, perms, username, token):
	if not check_token(username, token):
		return False

	resp = {}
	userdb = user_setup()
	owner = userdb.query(User).filter(User.name == username).first()
	other_user = userdb.query(User).filter(User.name == perms[1]).first()
	filedb = file_setup()
	directory = filedb.query(File).filter(File.identifier == dirid).first()
	
	if directory.filename != dirname:
		resp["new_dirname"] = directory.filename


	permdb = permission_setup()
	if directory:
		if directory.owner_id == owner.id:
			permission = Permission_Assoc(user_id=other_user.id, file_id=directory.id, perm_type=perms[0], key=perms[2])
			permdb.add(permission)
			permdb.commit()
			resp["message"] = "success"
			return resp

	return False
