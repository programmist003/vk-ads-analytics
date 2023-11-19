import toml
from icecream import ic
import requests
from pandas import DataFrame

API_ADDRESS = "https://api.vk.com/method/"
OAUTH_ENDPOINT = "https://oauth.vk.com/"

config = toml.load("config.toml")
token = config.get("token")
ic(token)

# Getting data from VK API and putting it to dataframe
r = requests.post(f"{API_ADDRESS}ads.getAccounts",
                  params={"access_token": token, "v": "5.131"}).json()
data = r.get("response") if "response" in r else r.get("error")
ic(data)
ads_accs_data = DataFrame(
    data=data, columns=["account_id", "account_type", "account_name"])
ic(ads_accs_data)
