from threading import Thread

from .sql import SQL


class Queue:
	_instance = []

	@staticmethod
	def getInstance():
		return Queue._instance[0]

	def __init__(self):
		self._queue = []
		Thread(target=self._queueHandler).start()

	def push(self, query):
		self._queue.append(query)

	def _queueHandler(self):
		while True:
			if len(self._queue) > 0:
				with SQL() as db:
					query = self._queue.pop(0)
					query._response = db.execute(query.query, query.args)
