from secrets import token_urlsafe as token

import bcrypt
from webserver.httpResponse.parser import parser
from webserver.redirect import Redirect
from webserver.sql.query import Query


def auth(func):
	def authentication(request):
		if 'token' in request.cookies:
			result = Query('SELECT username FROM admin_users WHERE token=?', request.cookies['token']).execute()
			if len(result) == 1:
				return func(request, result[0][0])
		return Redirect('/admin-login')
	return authentication

@auth
def admin(request, username):
	tables = Query('SELECT name FROM sqlite_master WHERE type=?', 'table').execute()
	tables = [table[0] for table in tables if not table[0].startswith('admin_')]
	return parser('index.html', admin=True, username=username, tables=tables)

@auth
def createTable(request, username):
	print(request.attrs)
	return parser('newTable.html', admin=True, username=username)

def login(request):
	error = False
	attrs = request.attrs
	if 'username' in attrs and 'password' in attrs:
		error = True
		query = Query('SELECT username, password FROM admin_users WHERE username=?', attrs['username'])
		result = query.execute()
		if len(result) == 1 and bcrypt.checkpw(attrs['password'].encode(), result[0][1]):
			query = 'SELECT token FROM admin_users WHERE token=?'
			t = token()
			while len(Query(query, t).execute()) != 0:
				t = token()
			Query('UPDATE admin_users SET token=? WHERE username=?', t, attrs['username']).execute()
			request.setCookie('token', t, 'HttpOnly')
			return Redirect('/admin')
	return parser('login.html', admin=True, error=error)
