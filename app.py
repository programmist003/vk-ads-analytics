import toml
from icecream import ic

CONFIG_FILE = "config.toml"
TOKEN_FILE = "token.txt"


class Core:
    API_ADDRESS = "https://api.vk.com/method/"
    VERSION = "5.131"
    OAUTH_ENDPOINT = "https://oauth.vk.com/authorize"
    SCOPE="ads,offline"


class Config:
    vk_app_id: int

    def __init__(self, f) -> None:
        conf = toml.load(f)
        if conf is not None:
            for key, value in conf.items():
                setattr(self, key, value)


config = Config(CONFIG_FILE)


def test():
    ic(config.__dict__)


if __name__ == "__main__":
    test()
