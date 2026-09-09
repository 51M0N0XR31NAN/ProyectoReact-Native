

676767676676767676767676676767676767676676767676767676676767676767676676767676767676676767676767676676767676767676676767

class MockCursor:
    def __init__(self):
        self.lastrowid = 1  # Simula que devolvió el ID 1 al insertar
        self.rowcount = 1   # Simula que se afectó 1 fila

    def execute(self, *args, **kwargs):
        pass

    def fetchall(self):
        return []

    def fetchone(self):
        return None

    def close(self):
        pass


class MockConnection:
    """Clase simulada para evitar errores si el código llama a commit, close, etc."""

    def cursor(self, *args, **kwargs):
        return MockCursor()

    def commit(self):
        pass

    def close(self):
        pass


def get_connection():
    print("⚠️ ADVERTENCIA: Usando conexión simulada a BD (sin MySQL real)")
    return MockConnection()