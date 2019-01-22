import sqlite3


class SQL:
	def __init__(self):
		self.conn = sqlite3.connect('db.sqlite')
		self.db = self.conn.cursor()

	def execute(self, query, args):
		self.db.execute(query, args)
		return self.db.fetchall() if self.db.lastrowid == 0 else self.db.lastrowid

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.conn.commit()
		self.conn.close()