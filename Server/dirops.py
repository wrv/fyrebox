

##
# createdir(dirName, username, token)
#
# dirName - the encrypted name of the directory we want to create
# username - username of the person
# token - the token of the person
#
# Checks the token, creates a new entry in the file database
# responds with a success/failure based on if the directory already exists
#
def createdir(dirName, username, token):
	pass

##
# deletedir(dirName, username, token)
#
# dirName - the encrypted name of the dir we want to delete
# username - username of the person
# token - the token of the person
#
# Checks the token, checks write permission on dir and all files inside
# of folder. Remove corresponding dir. Respond with success/failure.
#
def deletedir(dirName, username, token):
	pass

##
# readdir(dirName, username, token)
#
# dirName - the encrypted name of the dir we want to read
# username - username of the person
# token - the token of the person
#
# Checks the token, check read permission on dir. For every file
# in the directory, send the name of the directory. Send json data
# of {op: readdir, dirName=[file names name], perm=(username, E_pk(key))}
#
def readdir(dirName, username, token):
	pass

##
# renamedir(oldName, newName, username, token)
#
# oldName - the encrypted name of the dir we want to rename
# newName - the new encrypted title we want to give a dir
# username - username of the person
# token - the token of the person
#
# Checks the token, check write permissions, overwrite dirName, respond 
# success or failure
#
def renamedir(oldName, newName, username, token):
	pass

##
# permdir(dirName, perms, username, token)
#
# dirName - the encrypted name of the dir we want to change permissions on
# perms - a tuple of user, permission, and secret key
# username - username of the person
# token - the token of the person
#
# Checks the token, check that username is the correct owner, add the
# encrypted key into the permissions database for the directory
#
def permdir(dirName, perms, username, token):
	pass
