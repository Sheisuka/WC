class Settings:
    # Включить мобильные прокси. В папку с проксями ложим одну проксю, ip будет меняться по ссылке для каждого ака.
    # Если включили мобильные прокси не забудьте указать ссылку для смены ip
    # По умолчанию False. Берутся все доступные прокси из proxy.txt и по очереди используются для каждого акак, если проксей меньше чем аккаунтов,
    # то они будут использоваться по кругу.
    # login:pass@ip:port формат прокси. тут настройка прокси только для аккаунтов, настройка для gpt ниже.
    # proxy всегда true если вы не положите прокси в proxy.txt софт просто запустится без проксей.
    proxy = True
    mobile_proxy = False
    mobile_change_link = ""

    # Теги аккаунтов у которых будут браться фоловеры для рандомный действий.
    # Для каждого акак берется. Общее кол-во делиться на кол-во доноров и полученное кол-во береться с каждого донора.
    donar_names = [
        "vitalik.eth",
    ]
    # Сколько пользователей набираем для взаймодействия 200-300 самый оптимальный вариант
    # Чем больше пользователей набираете тем дольше будет процес набора и тем больше вероятность попасть под рейт лимит
    how_get_users = 300

    # Максимальное число для случайного числа лайков у каждого аккаунта. Берется случайное число в пределах указанных.
    max_likes_per_user = [3, 8]
    # У какого кол-ва юзеров будем лайкать посты
    max_user_for_like = [5, 10]

    # Максимальное число для случайного числа коментов у каждого аккаунта. Берется случайное число в пределах указанных.
    max_comment_per_user = [3, 8]
    # У какого кол-ва юзеров будем писать коменты к постам
    max_user_for_comment = [5, 10]

    # Максимальное число для случайного числа подписок. Рандом от 1 до указанного.
    max_followers = [2, 5]

    # Сколько спим между между аккаунтами.
    sl_between_account = [30, 60]

    # Сколько спим между действиями внутри аккаунтов
    sl_inside_account = [20, 30]

    # Максимальное кол-во попыток для любых повторов, от попыток отправить комент или лайк, до попыток гпт получить пост нужной длины
    max_retry = 5

    # Убираем пост из списка, после создания в варпкасте. При ручной генерации поста. Один пост = один аккаунт, без повторений.
    # РАБОТАЕТ ТОЛЬКО ПРИ gpt_use_on_post = FALSE
    uniq_post_between_account = True

    # Бесконечный режим, если приватники закончились, то пойдут по кругу
    infinity_mode = False

    # Перемешать список аккаунтов перед стартом
    before_start_shuffle_ps_list = True

    # GPT MODULE
    # Используем ли официальный api ключ openai - без него будет работать на хакнутой версии, но стабильности не будет. Постоянные ошибки. Ключ надо покупать отдельно.
    # Если сами не знаете как сделать ключ пишите в сапорт дам ссылку на продавца, стоит 3 копейки.
    # По умолчанию включена хакнутая версия
    gpt_api_key_use = True

    # Это рабочий ключ, но на нем может закончиться баланс, рекомендую сделать себе личный. Стоит это примерно 800р, но вам его хватит на вечно.
    gpt_api_key = "sk-proj-jkoVj93l8mOXA3zfERnkT3BlbkFJ0Epiu3HzZWIM2CuO2Lmw"

    # Это рабочие прокси, но они могут быть не стабильны потому что их юзают все, рекомендую купить себе свои.
    # login:pass@ip:port нужна любая страна кроме Рф и Украины. Если не знаете где купить, пишете в саппорт дам ссылку.
    gpt_proxy = "Kxb5iqxR:XWwJey96@109.172.122.7:63690"

    # Используем ли gpt для создания публикаций
    gpt_use_on_post = True

    # Тут есть варик писать только через gpt. Не ставьте False. Используем ли gpt для контекстного комента к чужому посту
    gpt_use_on_comment_post = True
    # Писать тематический комментарий на языке аккаунта. Если поставить False то будет писать комент на языке поста на который делается коммент.
    gpt_use_language_on_comment_post = False

    # Используем ли gpt для заполнения имени и био
    gpt_use_on_set_bio_or_name = True

    # Включить ли дебаг сообщения для gpt кастомной
    gpt_debug = True

    #### БД
    # При запуске использовать данные из бд или данные из .txt файлав
    db_use = False
    # Название базы данных. Ее можно менять для работы с разными базами данные, если у вас их создано несколько
    db_file_name = "db.json"
    db_dir = "data/db"

    ### БОЛЬШОЙ МОДУЛЬ РАНДОМА, ВНИМАТЕЛЬНО ПРОЧИТАЙ ВСЕ НАСТРОЙКИ ПЕРЕД ЕГО ЗАПУСКОМ ###
    # Список из каких действий будет формироваться рандомные действия в рандомном маршруте
    # ["random_like", "random_post", "random_follow", "random_comment"]
    actions_list = [
        "random_post",  # В первом кошельке будет выполнен только рандомный пост
        [
            "random_like",
            "random_post",
            "random_follow",
            "random_comment",
        ],  # Во втором кошельке будет в рандомном порядке выполнены все эти 4 дейтсвия
        [
            "random_follow",
            "random_comment",
        ],  # В третьем кошельке будут в рандомном порядке выполнены два действия
        [
            "random_like",
            "random_post",
            "random_follow",
            "random_comment",
        ],  # В четвертом кошельке будут рандомно порядке выполнены 4 действия
    ]  # Если кошельков больше чем рандомный листов, то они пойдут по кругу в рамдомном порядке

    # Перемешивать ли общий список при старте (или перед началом каждого круга методов) или следовать по той структуре которую вы указали
    shuffle_method = True


settings = Settings()
