import toml
from icecream import ic
import requests
import pandas as pd
import time
import sys
from collections import OrderedDict

API_ADDRESS = "https://api.vk.com/method/"
OAUTH_ENDPOINT = "https://oauth.vk.com/"
VERSION = "5.131"

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
    columns=["id", "owner_id", "name"])
for index, account in ad_accs_data.iterrows():
    if account.type == "general":
        clients = pd.DataFrame([{"id": None}], columns=["id", "name"])
        clients["owner_id"] = account.id
        clients["id"] = account.id
        clients["name"] = account["name"]
        client_ids = pd.concat([client_ids, clients])
        ic(clients)
        continue
    r = requests.post(f"{API_ADDRESS}ads.getClients", params={
        "access_token": token,
        "v": VERSION,
        "account_id": account.id}).json()
    data = r.get("response") if "response" in r else None
    clients = pd.DataFrame(data, columns=["id", "name"])
    clients["owner_id"] = account.id
    client_ids = pd.concat([client_ids, clients])
    time.sleep(0.5)
ic(client_ids)

# Getting ads
ad_ids = pd.DataFrame(columns=["campaign_id", "id", "client_id"])
for index, client in client_ids.iterrows():
    client_id = {client.id: "client_id", client.owner_id: "account_id"}
    client_id = {v: k for k, v in client_id.items()}
    params = {
        'access_token': token,
        'v': VERSION,
    }
    params.update(client_id)
    r = requests.get('https://api.vk.com/method/ads.getAds',
                     params=params).json()
    data = r.get("response") if "response" in r else None
    ads = pd.DataFrame(data, columns=["campaign_id", "id"])
    ads["client_id"] = client.id
    ad_ids = pd.concat([ad_ids, ads])
    time.sleep(0.5)
ic(ad_ids)
