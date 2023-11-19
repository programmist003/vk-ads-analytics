import toml
from icecream import ic

config = toml.load("config.toml")
token = config.get("token")
ic(token)
