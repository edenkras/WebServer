'''
request.method	->	GET / POST.
request.obj		->	The requested view / file.
request.attrs	->	Dictionary with the GET / POST attributes.
request.cookies	->	Dictionary with the cookies.

For example: test.com/home?name=Jhon&surname=Doe
	method = GET
	obj = home (no file type provided -> view)
	attrs = {'name': 'Jhon', 'surname': 'Doe'}
'''

import re
from urllib.parse import unquote_plus as percent_decode


class Request:
	def __init__(self, request):
		if not request:
			raise Exception('Test')

		request = request.replace('\r', '').split('\n\n')
		main = {i[0]: i[1] for i in [info.split(': ') for info in request[0].split('\n')[1:]]}
		r = request[0].split()

		# Method
		self.method = r[0]

		# target[0] -> Requested file / view
		# target[1] -> Get attributes
		target = r[1].split('?')
		self.obj = target[0]
		
		# Attributes
		self.attrs = {}
		if self.method == 'GET' and len(target) == 2:
			attrsString = target[1]
		else:
			attrsString = request[1]
		for k, v in re.findall('([^\&]+)=([^\&]+)', attrsString):
			k, v = percent_decode(k), percent_decode(v)
			if k.endswith('[]'):
				self.attrs.setdefault(k[:-2], []).append(v)
			else:
				self.attrs.setdefault(k, v)

		# Referer
		referer = main['Referer'] if 'Referer' in main else None
		if referer:
			referer = referer.replace('://', '')
			referer = referer[referer.find('/'):]
		self.referer = referer

		# Cookies
		self.cookies = {}
		cookiesString = main['Cookie'] if 'Cookie' in main else ''
		for k, v in re.findall('([^\;]+)=([^\;]+)', cookiesString):
			self.cookies[k] = v

		# Set cookies
		self._setCookies = []

	def setCookie(self, name, value, *args, **kwargs):
		cookie = 'Set-Cookie: ' + name + '=' + value + ';'
		for arg in args:
			cookie += arg + ';'
		for k, v in kwargs.items():
			cookie += k + '=' + v + ';'
		self._setCookies.append(cookie)
