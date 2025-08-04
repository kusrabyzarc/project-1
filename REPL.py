from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import prompt
import signal
import core

ruchki = core.Ruchki()
history = FileHistory('.cli_history')

# Топ-уровневые команды и их подкоманды
commands_tree = {
    "user": {
        "create": None,
        "delete": None,
        "validate": None,
        "exists": None,
    },
    "task": {
        "add": None,
        "delete": None,
        # ...
    },
    "ctx": None,
    "exit": None,
}

def make_completer(context_user):
    # В completer всегда добавляем топ-уровневые команды
    # и если есть контекст — добавляем низкоуровневые команды без префикса
    base = commands_tree.copy()

    if context_user:
        # Низкоуровневые команды, доступные в контексте (пример для user)
        # Здесь можно расширить по необходимости
        base.update({
            "validate": None,
            "delete": None,
            "exists": None,
        })

    return NestedCompleter.from_nested_dict(base)


def mask_input(prompt_text='Password: '):
    return prompt(prompt_text, is_password=True)


def handle_user_command(args):
    if not args:
        print("Ошибка: укажите подкоманду user (create/delete/validate/exists)")
        return

    subcommand = args[0]
    args = args[1:]

    if subcommand == 'create':
        if len(args) != 1:
            print("Формат: user create <username>")
            return
        name = args[0]
        password = mask_input("Введите пароль: ")
        print("Пользователь создан" if ruchki.create_user(name, password) else "Пользователь не создан")

    elif subcommand == 'delete':
        if len(args) != 1:
            print("Формат: user delete <username>")
            return
        print("Пользователь удалён" if ruchki.delete_user(args[0]) else "Пользователь не удалён")

    elif subcommand == 'validate':
        if len(args) != 1:
            print("Формат: user validate <username>")
            return
        password = mask_input("Введите пароль: ")
        print("Пара логин:пароль верная" if ruchki.validate_credentials(args[0], password) else "Пара логин:пароль неверная")

    elif subcommand == 'exists':
        if len(args) != 1:
            print("Формат: user exists <username>")
            return
        print("Пользователь существует" if ruchki.user_exists(args[0]) else "Пользователь не существует")

    else:
        print(f"Неизвестная подкоманда user: {subcommand}")


def handle_context_command(args, context_user):
    # ctx без аргументов — сброс
    if not args:
        return None
    # ctx с аргументом — установка контекста
    return args[0]


def handle_context_commands(command, args, context_user):
    # Низкоуровневые команды, выполняемые в контексте
    if command == "validate":
        if len(args) != 0:
            print("Формат: validate")
            return
        password = mask_input("Введите пароль: ")
        res = ruchki.validate_credentials(context_user, password)
        print("Пара логин:пароль верная" if res else "Пара логин:пароль неверная")

    elif command == "delete":
        if args:
            print("Формат: delete")
            return
        res = ruchki.delete_user(context_user)
        print("Пользователь удалён" if res else "Пользователь не удалён")

    elif command == "exists":
        if args:
            print("Формат: exists")
            return
        res = ruchki.user_exists(context_user)
        print("Пользователь существует" if res else "Пользователь не существует")

    else:
        print(f"Неизвестная команда в контексте: {command}")


def run_cli():
    context_user = None
    session = PromptSession(history=history)
    print("CLI. Используй TAB для автодополнения. `exit` для выхода.")

    while True:
        session.completer = make_completer(context_user)
        prompt_str = f"DB [{context_user}]> " if context_user else "DB> "

        try:
            with patch_stdout():
                user_input = session.prompt(prompt_str).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nВыход...")
            break

        if not user_input:
            continue

        tokens = user_input.split()
        command = tokens[0]
        args = tokens[1:]

        if command == "exit":
            break

        elif command == "ctx":
            context_user = handle_context_command(args, context_user)
            if context_user:
                print(f"Контекст переключён на пользователя '{context_user}'")
            else:
                print("Контекст сброшен")

        elif command == "user":
            handle_user_command(args)

        elif command == "task":
            # Пример заглушки — сделай свою реализацию
            print(f"task команда с аргументами: {args}")

        elif context_user:
            # Если контекст установлен и команда не топ-уровневая — обрабатываем в контексте
            handle_context_commands(command, args, context_user)

        else:
            print(f"Неизвестная команда: {command}")


def main():
    signal.signal(signal.SIGINT, lambda s, f: print("\n(Нажми `exit` для выхода)"))
    run_cli()


if __name__ == "__main__":
    main()
