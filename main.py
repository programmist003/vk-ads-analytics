import toml
from icecream import ic
import requests
import pandas as pd
import time
import sys

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
    data, columns=["account_id", "account_type", "account_name"])
ad_accs_data.rename(
    columns={"account_id": "id", "account_type": "type", "account_name": "name"}, inplace=True)
ic(ad_accs_data)

# Getting client ids of VK ad accounts
client_ids = pd.DataFrame(
    columns=["client_id", "account_id"])
for index, account in ad_accs_data.iterrows():
    account_id = account.id
    if account.type == "general":
        continue
    r = requests.post(f"{API_ADDRESS}ads.getClients", params={
        "access_token": token,
        "v": "5.131",
        "account_id": account_id}).json()
    data = r.get("response") if "response" in r else None
    clients = pd.DataFrame(data, columns=["id", "name"])
    clients.rename(columns={"id": "client_id"}, inplace=True)
    clients["account_id"] = account_id
    client_ids = pd.concat([client_ids, clients])
    time.sleep(0.5)
ic(client_ids)
