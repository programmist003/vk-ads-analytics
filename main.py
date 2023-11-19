import toml
from icecream import ic
import requests
import pandas as pd
import time

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
ad_accs_data = pd.DataFrame(
    data=data, columns=["account_id", "account_type", "account_name"])
ad_accs_data.set_index("account_id", inplace=True, drop=True)
ic(ad_accs_data)

# Getting client ids of VK ad accounts
client_ids = pd.Series()
for index, account in ad_accs_data.iterrows():
    if account.account_type == "general":
        client_ids[index] = None
        continue
    r = requests.post(f"{API_ADDRESS}ads.getClients", params={
        "access_token": token,
        "v": "5.131",
        "account_id": account.name}).json()
    data = r.get("response") if "response" in r else r.get("error")
    client_ids[index] = [i.get("id") for i in data]
    time.sleep(0.5)
ad_accs_data["client_ids"] = client_ids
ic(ad_accs_data)
