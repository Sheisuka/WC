import itertools
import os

import questionary
import requests
from loguru import logger
from tabulate import tabulate
from tinydb import TinyDB

from config import settings
from manager_account import WarpManager
from models import Account
from warp import Warp


def truncate(value, length=10):
    if isinstance(value, str) and len(value) > length:
        return value[:length]
    return value


def print_on_table(data: list, headers: list):
    truncated_data = [
        [i] + [truncate(cell) for cell in row] for i, row in enumerate(data, 1)
    ]
    table = tabulate(truncated_data, headers, tablefmt="grid")
    print(table)


def show_table():
    db = TinyDB(settings.db_patch, ensure_ascii=False)
    table_data = []
    headers = None
    for data in db.all():
        account = Account.model_validate(data)

        if not headers:
            headers = account.to_list_headers()
            headers.insert(0, "#")

        table_data.append(account.to_list_value())

    print_on_table(data=table_data, headers=headers)


def prepare_data():
    db = TinyDB(settings.db_patch, ensure_ascii=False)

    with open("data/const/private_seeds.txt", "r", encoding="utf-8") as f:
        private_seeds = f.read().splitlines()

    if not private_seeds:
        raise ValueError("Фаил с сидками не может быть пустым!")

    try:
        with open("data/const/languages.txt", "r", encoding="utf-8") as f:
            language = f.read().splitlines()
            language_cycle = itertools.cycle(language)
        if not language:
            logger.warning(
                "Вы не добавили языки, создаю бд без языков, функции гпт будут работать не стабильно."
            )
    except FileNotFoundError:
        language = []

    try:
        with open("data/const/proxy.txt", "r", encoding="utf-8") as f:
            proxys = f.read().splitlines()
            proxy_cycle = itertools.cycle(proxys)
        if not proxys:
            logger.warning("Вы не добавили прокси, создаю бд без проксей.")
    except FileNotFoundError:
        proxys = []

    try:
        with open("data/gpt/roles.txt", "r", encoding="utf-8") as f:
            roles = f.read().splitlines()
            role_cycle = itertools.cycle(roles)
        if not roles:
            logger.warning("Вы не добавили роли для chat-gpt, создаем бд без ролей.")
    except FileNotFoundError:
        roles = []

    table_data = []
    headers = None
    for i, ps in enumerate(private_seeds, 1):
        proxy = next(proxy_cycle, None)
        role = next(role_cycle, None)
        language = next(language_cycle, None)

        account = Account(ps=ps, proxy=proxy, role=role)
        client = Warp(account=account)
        account = Account(
            display_name=client.me.display_name,
            username=client.me.username,
            bio=client.me.profile.bio.text,
            language=language,
            follower_count=client.me.follower_count,
            following_count=client.me.following_count,
            ps=ps,
            proxy=proxy,
            role=role,
        )

        db.insert(account.model_dump())

        if not headers:
            headers = account.to_list_headers()
            headers.insert(0, "#")

        table_data.append(account.to_list_value())

        if settings.mobile_proxy:
            logger.warning("Меняем ip у мобильной прокси при добавлении аккаунтов в бд")

            print(requests.get(settings.mobile_change_link).text)
    print_on_table(data=table_data, headers=headers)


if __name__ == "__main__":
    if os.path.exists(settings.db_patch):
        choice = questionary.select(
            "Что будем делать для каждого аккаунта Warpcast?",
            choices=[
                "------ СТАНДАРТНЫЙ ФУНКЦИОНАЛ",
                "1. Пишем случайный пост из posts.txt или с помощью GPT",
                "2. Ставим лайки на случайные посты пользователей",
                "3. Подписываемся на случайные аккаунты",
                "4. Пишем тематический комент с помощью GPT",
                " " * 15,
                "------ МАРШРУТЫ С РАНДОМОМ",
                "5. Делаем rnd пост, пишем rnd комент на rnd пост, ставим rnd лайки, подписываемся на rnd аккаунты в случайном порядке для каждого аккаунта. Данные с файла или с GPT",
                "6. Запускаем БОЛЬШОЙ рандомный модуль, внимательно изучи настройки перед его запуском",
                " " * 15,
                "------ ЗАПОЛНЕНИЕ АККАУНТА",
                "7. Заполняем имена с account_data.txt или через GPT",
                "8. Заполняем био c account_data.txt или через GPT",
                "9. Заполняем имена и био с account_data.txt или через GPT",
                " " * 15,
                "------ ЧЕКЕР БАНОВ",
                "10. Проверить теневой бан на аккаунтах (Результат записывается в бд)",
                " " * 15,
                "------ КОНТРОЛЬ АККАУНТОВ/БД",
                "11. Показать таблицу бд (Она так-же доступна в папке bd. Через vscode откройте фаил, выделите все, правой кнопкой, форматировать документ.)",
                " " * 15,
                "0. Выход",
            ],
            instruction="(Используйте стрелки для переключения)",
            pointer="🥎",
        ).ask()
    else:
        choice = questionary.select(
            "У вас еще не создана db. Внимательно проверте, что у вас добавлены private_seeds.txt, proxy.txt (login:pass@ip:port), roles.txt для использования gpt",
            choices=[
                "99. Cоздать базу данных",
            ],
            instruction="(Используйте стрелки для переключения)",
            pointer="🥎",
        ).ask()

    match choice.split(".")[0]:
        case "1":
            client = WarpManager()
            client.post_random_message()

        case "2":
            client = WarpManager()
            client.like_random_posts()

        case "3":
            client = WarpManager()
            client.follow_random_accounts()

        case "4":
            client = WarpManager()
            client.post_random_comment()

        case "5":
            client = WarpManager()
            client.perform_all_randomly()

        case "6":
            client = WarpManager()
            client.perform_custom_randomly()

        case "7":
            client = WarpManager()
            client.perform_set_display_name()

        case "8":
            client = WarpManager()
            client.perform_set_bio()

        case "9":
            client = WarpManager()
            client.perform_set_display_name_and_bio()

        case "10":
            client = WarpManager()
            client.shadow_ban_check()

        case "11":
            show_table()

        case "0":
            pass

        case "99":
            prepare_data()
            logger.success(
                "Успешно созданил базу данных! Перезапустите софт, что начать работу с аккаунтами."
            )

        case _:
            logger.error("Вы выбрали неизвестный вариант")
