import re
from datetime import datetime
from os.path import isfile
from socket import socket
from threading import Thread

import webserver.admin

from settings import AssetsFolders, TemplatesFolder
from urls import urls as user_urls

from .admin.urls import urls
from .httpResponse.contentTypes import Types
from .httpResponse.parser import parser
from .redirect import Redirect
from .request import Request
from .sql.query import Query
from .sql.queue import Queue


class WebServer():
	def __init__(self):
		self.socket = socket()
		self.socket.bind(('127.0.0.1', 8000))
		self.socket.listen()
		# Initiate the queue
		self._queue = Queue()
		Queue._instance.append(self._queue)
		# Add the admin urls
		self._urls = list(urls)
		for url in user_urls:
			if url not in self._urls:
				self._urls.append(url)
		while True:
			conn, addr = self.socket.accept()
			Thread(target=self._connHandler, args=[conn, addr]).start()

	def _connHandler(self, conn, addr):
		request = Request(conn.recv(1024).decode())
		date = datetime.now().strftime(r'%Y-%m-%d %H:%M:%S')
		# Default
		code = 404
		message = request.method + ' ' + request.obj
		# Checks if the request exists in urls
		for url in self._urls:
			if url.match(request.obj):
				try:
					content = url.getContent(request)
					# Checks for redirect
					if isinstance(content, Redirect):
						code = 301
					else:
						code = 200
						ctype = url.contentType
				except Exception as e:
					code = 500
					message += ': ' + str(e)
				break
		else: # No break - request not found in urls
			if request.referer and any([x for x in urls if x.match(request.referer)]):
				adminPath = webserver.admin.__file__
				path = adminPath[:adminPath.rfind('\\')+1] + 'Templates\\' + request.obj
				if isfile(path):
					code = 200
					ctype = path[path.rfind('.')+1:]
					with open(path, 'rb') as f:
						content = f.read()
			elif isfile(TemplatesFolder + request.obj):
				# Searches the requested file in assets folders
				for directory in AssetsFolders:
					if directory != '' and request.obj.startswith('/' + directory):
						path = TemplatesFolder + request.obj
						code = 200
						ctype = path[path.rfind('.')+1:]
						with open(path, 'rb') as f:
							content = f.read()
						break
		# Not Found Error / Internal Server Error
		if code == 404 or code == 500:
			content = self._errorHandler(str(code) + '.html')
			ctype = 'html'
		# Sends the response
		conn.send(('HTTP/1.1 ' + str(code) + '\n').encode())
		if code == 301:
			conn.send(('Location: ' + content.location + '\n').encode())
			message += ' -> ' + content.location
		if len(request._setCookies) > 0:
			conn.send(('\n'.join(request._setCookies)).encode())
		if code != 301 and content != b'':
			conn.send(('Content-Type: ' + Types[ctype] + '\n\n').encode())
			conn.send(content)
		conn.close()
		# Log
		self._log(date, addr[0], code, message)

	def _errorHandler(self, htmlfile):
		try:
			content = parser(htmlfile)
		except:
			content = b''
		return content

	def _log(self, date, ip, code, message):
		self._queue.push(Query('INSERT INTO admin_logs VALUES (?, ?, ?, ?)', date, ip, code, message))
