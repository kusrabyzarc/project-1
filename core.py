import hashlib
import psycopg2

import pygost.gost34112012


class UserFlags:
    _flag_names = [
        "ADMIN",  # Пользователь с административными правами (создание/удаление пользователей, полный доступ)
        "DISABLED",  # Учётка заблокирована
        "NEED_PASSWORD_CHANGE",  # Требуется смена пароля при следующем входе
        "TIME_TRACKING_LOCKED",  # Пользователь не может логировать время
        "READONLY",  # Только просмотр задач (без редактирования)
        "BETA_ACCESS",  # Доступ к экспериментальным функциям
    ]
    FLAGS = {name: 1 << idx for idx, name in enumerate(_flag_names)}

    def __init__(self, value=0):
        self.value = value

    def get(self, flag: str) -> bool:
        return bool(self.value & self.FLAGS[flag])

    def set(self, flag: str, enabled: bool):
        if enabled:
            self.value |= self.FLAGS[flag]
        else:
            self.value &= ~self.FLAGS[flag]

    def toggle(self, flag: str):
        self.value ^= self.FLAGS[flag]

    def as_dict(self) -> dict:
        return {name: self.get(name) for name in self._flag_names}

    def to_int(self) -> int:
        return self.value

    @classmethod
    def from_int(cls, value: int):
        return cls(value)


class DBConnection:
    def __init__(self,
                 dbname='postgres',
                 user='postgres',
                 password='pidorasiananas',
                 host='192.168.0.69',
                 port='5432'):
        self.connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.connection.cursor()

    def execute(self, query, params=None):
        try:
            self.cursor.execute(query, params)
        except psycopg2.Error as e:
            self.connection.rollback()
            raise e

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        self.cursor.close()
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()


class Ruchki:
    def _pass2hash(self, password) -> str:
        sha256 = hashlib.sha256(password.encode()).hexdigest()
        gost = pygost.gost34112012.GOST34112012(password.encode()).hexdigest()
        return f'{sha256}${gost}'

    def user_exists(self, name: str) -> bool:
        with DBConnection() as conn:
            conn.execute("SELECT 1 FROM public.credentials WHERE username = %s LIMIT 1;", (name,))
            return conn.fetchone() is not None

    def create_user(self, name: str, password: str) -> bool:
        hashstr = self._pass2hash(password)
        with DBConnection() as conn:
            try:
                conn.execute(
                    "INSERT INTO public.credentials (username, password_hash) VALUES (%s, %s) ON CONFLICT (username) DO NOTHING;",
                    (name, hashstr)
                )
                return conn.cursor.rowcount > 0
            except psycopg2.Error:
                return False

    def validate_credentials(self, name: str, password: str) -> bool:
        hashstr = self._pass2hash(password)
        with DBConnection() as conn:
            conn.execute(
                "SELECT COUNT(*) FROM public.credentials WHERE username = %s AND password_hash = %s;",
                (name, hashstr)
            )
            count = conn.fetchone()[0]
            if count > 1:
                raise ValueError("Несколько пользователей с одинаковыми данными — нарушение уникальности.")
            return count == 1

    def delete_user(self, name) -> bool:
        with DBConnection() as conn:
            if not self.user_exists(name):
                return False

            conn.execute("DELETE FROM public.credentials WHERE username = %s",
                         (name,))
            return True


if __name__ == '__main__':
    ruchki = Ruchki()
    print(ruchki.create_user('huesos', '12345678'))
    print(ruchki.validate_credentials('huesos', '12345678'))
