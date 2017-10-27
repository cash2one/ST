# cookie secret
COOKIE_SECRET = "SSdsadasdX312312Csededddqw"
COOKIE_DOMAIN = None

# postgresql 配置
POSTGRESQL = {
    "master": {
        "url": "postgresql://postgres:postgres@127.0.0.1/db0",

    },
    # "slave": {
    #     "url": "postgresql://dbuser:111111@192.168.123.141/dprm",
    # }
}

# redis 配置
REDIS = {
    "master": {
        'host': '127.0.0.1',
        'port': 6379
    }
}
MONGO = {
    # "dprm": {
    #     "host": "mongodb://192.168.123.143",
    #     "port": 27017
    # }
}
# session 配置
SESSION = {
    "cookie": "session",
    "redis": "master",
}

APP_KEY = "8635cab927cdb857d752eed5"
MASTER_SECRET = "c4db0bd0dceb7b5a9876596a"
