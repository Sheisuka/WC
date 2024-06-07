import g4f
import g4f.debug
import httpx
from g4f.client import Client
from g4f.Provider import FreeChatgpt, Liaobots, Phind, RetryProvider
from openai import OpenAI

from config import settings

g4f.debug.logging = settings.gpt_debug


class GptClient:
    def __init__(self, role: str, proxy: str = None) -> None:
        if settings.gpt_api_key_use:
            custom_http_client = httpx.Client(proxy=f"http://{settings.gpt_proxy}")
            self.client = OpenAI(
                api_key=settings.gpt_api_key,
                http_client=custom_http_client,
            )
        else:
            self.client = Client(
                proxies="http://{proxy}" if proxy else proxy,
                provider=RetryProvider([Phind, FreeChatgpt, Liaobots], shuffle=False),
            )
        self.role = role

    def get_context_comment(self, post: str):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Определи язык следующего поста и напиши тематический комментарий на этом языке. Верни только комментарий без дополнительных пояснений и не оборачивай его в кавычки.",
                },
                {"role": "user", "content": f"Пост: {post}\n\nКомментарий:"},
            ],
            max_tokens=50,
            temperature=0.7,
            stop=["Комментарий:"],
        )
        return response.choices[0].message.content

    def get_msg(self, content: str):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": self.role,
                },
                {
                    "role": "user",
                    "content": content,
                },
            ],
        )
        return response.choices[0].message.content
