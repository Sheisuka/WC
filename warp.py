import random
import time
from typing import List, Optional, Union

from loguru import logger

from config import settings
from manager_gpt import GptClient
from models import Account
from warpcast_modified import WarpModified


class Warp:
    def __init__(self, account: Account, text: Optional[str] = None) -> None:
        self.client = WarpModified(mnemonic=account.ps, proxy=account.proxy)
        self.client_gpt = GptClient(role=account.role)
        self.language = account.language
        self.text = text
        time.sleep(0.5)
        self.me = self.client.get_me()

    def get_users(self, total_limit=300):
        users = []
        fid = self.client.get_user_by_username(username=settings.donar_name).fid
        cursor = None

        self.client.send_device()
        while len(users) < total_limit:
            response = self.client.get_followers(fid=fid, cursor=cursor, limit=100)

            for user in response.users:
                if (
                    hasattr(user, "pfp")
                    and user.pfp
                    and user.pfp.url
                    != "https://imagedelivery.net/BXluQx4ige9GuW0Ia56BHw/3ffc18c3-e259-432c-8d42-5f07e140be00/rectcrop3"
                ):
                    users.append(user)

                    if len(users) >= total_limit:
                        return users[:total_limit]

            cursor = response.cursor

            if response.cursor is None:
                break

            time.sleep(1)
        print(users)

        return users[:total_limit]

    def sb_get_random_cast_hash(self, users: list):
        while True:
            random_user = random.choice(users)
            user_casts = self.client.get_casts(fid=random_user.fid).casts
            if (
                len(user_casts) > 2
                and random_user.pfp.url
                != "https://imagedelivery.net/BXluQx4ige9GuW0Ia56BHw/3ffc18c3-e259-432c-8d42-5f07e140be00/rectcrop3"
            ):
                random_user_cast = random.choice(user_casts)
                self.client.casts_wiewed(
                    cast_hashes=[
                        random_user_cast.hash,
                    ]
                )
                return random_user_cast.hash

            time.sleep(1)

    def sb_send_comment(self, text: str, cast_hash: str):
        return self.client.post_cast(text=text, parent=cast_hash).cast

    def sb_check_comment(self, cast_hash: str, text: str):
        thread_casts = self.client.get_thread_casts(thread_hash=cast_hash)
        self.client.casts_wiewed(
            cast_hashes=[
                cast_hash,
            ]
        )
        for i, cast in enumerate(thread_casts.casts, 1):
            if cast.text == text:
                return False
        return True

    def sb_delete_post(self, cast_hash: str):
        self.client.delete_cast(cast_hash=cast_hash)

    def change_bio_and_display_name(
        self, change_type: str, bio: str = None, display_name: str = None
    ):
        if settings.gpt_use_on_set_bio_or_name:
            match change_type:
                case "all":
                    text = self.client_gpt.get_msg(
                        content=f"Напиши мне никнейм и очень короткую биографию на 2-4 лова на {self.language} языке нужно добавить небрежности. что бы она выглядела более натурально, например писать с маленькой буквы или допускать сленговые выражение или даже ошибки. ответ верни формате: имя:биография без дополнительных кавычек"
                    )
                    display_name, bio = text.split(":")
                    logger.info(
                        f"@{self.me.username} : Заполняем имя {display_name} и био {bio} с помощью GPT"
                    )

                case "display_name":
                    text = self.client_gpt.get_msg(
                        content="Напиши мне никнеймнужно добавить небрежности. что бы он выглядел более натурально, например писать с маленькой буквы или допускать сленговые выражение или даже ошибки. в ответ верни только без дополнительных кавычек и дополнительных комментариев"
                    )
                    display_name = text
                    logger.info(
                        f"@{self.me.username} : Заполняем имя {display_name} с помощью GPT"
                    )

                case "bio":
                    text = self.client_gpt.get_msg(
                        content=f"Напиши мне очень короткую биографию на 2-4 лова на {self.language} языке нужно добавить небрежности. что бы она выглядела более натурально, например писать с маленькой буквы или допускать сленговые выражение или даже ошибки. ответ верни только биография без дополнительных кавычек и дополнительных комментариев"
                    )
                    bio = text
                    logger.info(
                        f"@{self.me.username} : Заполняем био {bio} с помощью GPT"
                    )

                case _:
                    logger.error("Неизвестная ошибка.")
        else:
            if display_name and bio:
                logger.info(
                    f"@{self.me.username} : Заполняем имя {display_name} и био {bio} с account_data.txt"
                )

            elif display_name and not bio:
                logger.info(
                    f"@{self.me.username} : Заполняем имя {display_name} с account_data.txt"
                )

            elif bio and not display_name:
                logger.info(
                    f"@{self.me.username} : Заполняем био {bio} с account_data.txt"
                )

        self.client.set_bio_and_display_name(
            bio=bio if bio else self.me.profile.bio.text,
            display_name=display_name if display_name else self.me.display_name,
        )

        logger.success(f"@{self.me.username} : успешно заполнили профиль!")

    def send_random_post(self):
        if settings.gpt_use_on_post:
            logger.info(
                f"@{self.me.username} : Делаем пост через ГПТ на {self.language} языке"
            )
            retry = 0
            while True:
                retry += 1
                logger.info(f"Попытка {retry}")
                try:
                    text = self.client_gpt.get_msg(
                        content=f"Напиши мне пост для твиттера на {self.language} языке без каких-либо дополнительных комментариев и тегов и не нужно оборачивать текст в кавычки"
                    )
                    break
                except Exception as e:
                    logger.error(f"При запросе к GPT случилась ошибка: {e}")
                    logger.info("Поспим 10 секунд и попробуем еще раз")
                    time.sleep(10)
                    if retry > 3:
                        break
        else:
            text = self.text
            logger.info(f"@{self.me.username} : Берем пост из post.txt")

        self.client.post_cast(text=text)

        random_time_sleep = random.randint(
            settings.sl_inside_account[0], settings.sl_inside_account[1]
        )

        logger.success(
            f"@{self.me.username} : Разместили рандомный пост '{text}', спим {random_time_sleep} сек"
        )

        time.sleep(random_time_sleep)

    def send_comment_on_cast(self, users: List):
        how_random_user = random.randint(
            settings.max_user_for_comment[0], settings.max_user_for_comment[1]
        )

        logger.info(
            f"@{self.me.username} : Пишем коменты на посты у {how_random_user} пользователей"
        )

        for _ in range(how_random_user):
            random_user = random.choice(users)

            how_random_comment = random.randint(
                settings.max_comment_per_user[0], settings.max_comment_per_user[1]
            )

            user_casts = self.client.get_casts(fid=random_user.fid).casts

            logger.info(
                f"@{self.me.username} : Пишем коменты на {how_random_comment} поста(-ов) или меньше у пользователя @{random_user.username}"
            )

            if how_random_comment > len(user_casts):
                logger.warning(
                    f"@{self.me.username} : хотели написать коменты на {how_random_comment} постов, но у этого пользователя (@{random_user.username}) только {len(user_casts)} поста."
                )

                how_random_comment = len(user_casts)

            random_user_casts = random.sample(user_casts, how_random_comment)

            for i, cast in enumerate(random_user_casts, 1):
                self.client.casts_wiewed(
                    cast_hashes=[
                        cast.hash,
                    ]
                )
                if len(cast.text) > 6:
                    if settings.gpt_use_on_comment_post:
                        logger.info(
                            f"@{self.me.username} : Делаем тематический комент к посту"
                        )
                        retry = 0
                        while True:
                            retry += 1
                            logger.info(f"Попытка {retry}")
                            try:
                                text = self.client_gpt.get_context_comment(
                                    post=cast.text
                                )
                                break

                            except Exception as e:
                                logger.error(f"При запросе к GPT случилась ошибка: {e}")
                                logger.info("Поспим 10 секунд и попробуем еще раз")
                                time.sleep(10)
                                if retry > 3:
                                    break
                    else:
                        time.sleep(1)
                self.client.post_cast(text=text, parent=cast.hash)

                random_time_sleep = random.randint(
                    settings.sl_inside_account[0], settings.sl_inside_account[1]
                )

                logger.success(
                    f"@{self.me.username} : Написали тематический коммент({text}) на рандомный пост ({cast.text}) от @{cast.author.username} это пост {i}/{len(random_user_casts)}, спим {random_time_sleep} сек"
                )

                time.sleep(random_time_sleep)

    def random_like(self, users: List):
        how_random_user = random.randint(
            settings.max_user_for_like[0], settings.max_user_for_like[1]
        )

        logger.info(
            f"@{self.me.username} : Лайкаем посты у {how_random_user} пользователей"
        )

        for _ in range(how_random_user):
            random_user = random.choice(users)

            how_random_likes = random.randint(
                settings.max_likes_per_user[0], settings.max_likes_per_user[1]
            )

            user_casts = self.client.get_casts(fid=random_user.fid).casts

            logger.info(
                f"@{self.me.username} : Лайкаем {how_random_likes} поста(-ов) или меньше у пользователя @{random_user.username}"
            )

            if how_random_likes > len(user_casts):
                logger.warning(
                    f"@{self.me.username} : хотели залайкать {how_random_likes}, но у этого пользователя (@{random_user.username}) только {len(user_casts)} поста."
                )

                how_random_likes = len(user_casts)

            random_user_casts = random.sample(user_casts, how_random_likes)

            for i, cast in enumerate(random_user_casts, 1):
                self.client.casts_wiewed(
                    cast_hashes=[
                        cast.hash,
                    ]
                )

                self.client.like_cast(cast.hash)

                random_time_sleep = random.randint(
                    settings.sl_inside_account[0], settings.sl_inside_account[1]
                )

                logger.success(
                    f"@{self.me.username} : Залайкали рандомный пост от @{cast.author.username} это лайк {i}/{len(random_user_casts)}, спим {random_time_sleep} сек"
                )

                time.sleep(random_time_sleep)

    def random_follow(self, users: List):
        how_follow = random.randint(
            settings.max_followers[0], settings.max_followers[1]
        )

        random_users = random.sample(users, how_follow)

        for i, user in enumerate(random_users, 1):
            self.client.follow_user(user.fid)

            random_time_sleep = random.randint(
                settings.sl_inside_account[0], settings.sl_inside_account[1]
            )

            logger.success(
                f"@{self.me.username} : подписались на @{user.username} это подписка {i}/{len(random_users)}, спим {random_time_sleep} сек"
            )

            time.sleep(random_time_sleep)

    def random_actions(self, users: List):
        methods = [
            ("рандом пост", self.send_random_post, ()),
            ("рандом лайк", self.random_like, (users,)),
            ("рандом подписка", self.random_follow, (users,)),
            ("рандомный комент", self.send_comment_on_cast, (users,)),
        ]

        random.shuffle(methods)
        i = 0

        for name, method, params in methods:
            i += 1
            method(*params)

            random_time_sleep = random.randint(
                settings.sl_inside_account[0], settings.sl_inside_account[1]
            )

            logger.info(
                f"@{self.me.username} Закончили {i}/{len(methods)} '{name}', спим внутри random_actions между действиями {random_time_sleep} сек"
            )
            logger.info("#" * 50)

            if i < len(methods):
                time.sleep(random_time_sleep)

    def custom_random_actions(self, users: List, work_methods: Union[List, str]):
        methods = {
            "random_like": ("рандом лайк", self.random_like, (users,)),
            "random_post": ("рандом пост", self.send_random_post, ()),
            "random_follow": ("рандом подписка", self.random_follow, (users,)),
            "random_comment": (
                "рандом комменты к постам",
                self.send_comment_on_cast,
                (users,),
            ),
        }

        if isinstance(work_methods, list):
            random.shuffle(work_methods)
        else:
            work_methods = list(work_methods)

        i = 0
        for choise_method in work_methods:
            name, method, params = methods[choise_method]

            i += 1
            method(*params)

            random_time_sleep = random.randint(
                settings.sl_inside_account[0], settings.sl_inside_account[1]
            )

            logger.info(
                f"@{self.me.username} Закончили {i}/{len(work_methods)} '{name}', спим внутри random_actions между действиями {random_time_sleep} сек"
            )
            logger.info("#" * 50)

            time.sleep(random_time_sleep)
