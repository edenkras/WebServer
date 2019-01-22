from .queue import Queue

class Query:
	def __init__(self, query, *args, **kwargs):
		self.query = query
		self.args = args if len(args) > 0 else kwargs
		self._response = None

	def execute(self):
		Queue.getInstance().push(self)
		while self._response is None:
			pass
		return self._response
