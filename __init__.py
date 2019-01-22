from os.path import isfile
from getpass import getpass

import bcrypt

from .core import WebServer
from .sql.sql import SQL

def createUser():
	username = input('Enter username: ')
	password = getpass('Enter password: ')
	verifyPassword = ''
	while password != verifyPassword:
		verifyPassword = getpass('Re-enter password: ')
	with SQL() as db:
		try:
			db.execute('INSERT INTO admin_users (username, password) VALUES (?, ?)',
						[username,
						bcrypt.hashpw(password.encode(), bcrypt.gensalt())])
		except:
			print('Username already exists')

commands = {
	'runserver': WebServer,
	'createsuperuser': createUser
}

def management(cmd):
	if cmd in commands:
		if not isfile('db.sqlite'):
			with SQL() as db:
				db.execute('CREATE TABLE admin_users (username TEXT PRIMARY KEY, password TEXT, token TEXT UNIQUE)', [])
				db.execute('CREATE TABLE admin_logs (date TEXT, ip TEXT, code INTEGER, message TEXT)', [])
		commands[cmd]()
	else:
		print('\n'.join(commands.keys()))