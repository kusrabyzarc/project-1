import concurrent.futures
import string
import random
import time

from core import Ruchki

ruchki = Ruchki()
n = 0

# Генератор случайного имени пользователя
def random_username(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Генератор нагрузки — создание, валидация, удаление
def stress_worker(user_index):
    global n
    username = f"test_{random_username()}"
    password = "securepass123"

    try:
        created = ruchki.create_user(username, password)
        validated = ruchki.validate_credentials(username, password)
        deleted = ruchki.delete_user(username)
        print(n + 1)
        n += 1
        return {
            "id": user_index,
            "created": created,
            "validated": validated,
            "deleted": deleted,
        }
    except Exception as e:
        print(n + 1)
        n += 1
        return {
            "id": user_index,
            "error": str(e)
        }


def main():
    users_count = 4096
    max_workers = 64

    print(f"[+] Запуск нагрузочного теста: {users_count} пользователей, {max_workers} потоков")
    start = time.perf_counter()

    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(stress_worker, i) for i in range(users_count)]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)

    duration = time.perf_counter() - start
    print(f"[✓] Тест завершён за {duration:.2f} секунд")

    success = sum(1 for r in results if r.get("created") and r.get("validated") and r.get("deleted"))
    failures = len(results) - success

    print(f"Успешно: {success} / Неуспешно: {failures}")

    for r in results:
        if "error" in r:
            print(f"[!] Ошибка #{r['id']}: {r['error']}")


if __name__ == '__main__':
    main()
