import re

class url:
	def __init__(self, regex, func, ctype='html'):
		self._regex = regex
		self._func = func
		self._ctype = ctype

	def match(self, string):
		return True if re.match(self._regex, string) else False

	def getContent(self, request):
		return self._func(request)

	@property
	def contentType(self):
		return self._ctype

	def __eq__(self, other):
		return self._regex == other._regex