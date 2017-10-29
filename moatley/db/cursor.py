class Cursor(object):
    def __init__(self, db):
        self._db = db
        self._cursor = None

    def __enter__(self):
        self._db.ping(True)
        self._cursor = self._db.cursor()
        return self._cursor

    def __exit__(self, type, value, traceback):
        self._db.commit()
        self._cursor.close()


