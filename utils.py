import itertools
import os

import requests
from loguru import logger
from tabulate import tabulate
from tinydb import TinyDB

from config import settings
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


def prepare_data_on_db():
    if not os.path.exists("/data/db/"):
        os.mkdir("data/db/")

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

    if settings.proxy:
        try:
            with open("data/const/proxy.txt", "r", encoding="utf-8") as f:
                proxys = f.read().splitlines()
                proxy_cycle = itertools.cycle(proxys)
            if not proxys:
                logger.warning(
                    "Вы включили прокси в конфиге, но не добавили прокси в proxy.txt, создаю бд без проксей."
                )
        except FileNotFoundError:
            proxys = []
            proxy_cycle = itertools.cycle(proxys)
    else:
        proxys = []
        proxy_cycle = itertools.cycle(proxys)

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


def prepare_data_from_txt():
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

    account_list = []
    for i, ps in enumerate(private_seeds, 1):
        proxy = next(proxy_cycle, None)
        role = next(role_cycle, None)
        language = next(language_cycle, None)
        account_list.append(Account(ps=ps, proxy=proxy, role=role, language=language))

    return account_list
