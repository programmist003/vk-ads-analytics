import toml
from icecream import ic
import requests
import pandas as pd
import time
import sys
from collections import OrderedDict
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
from app import config, Core, TOKEN_FILE
from auth import read_token, vk_auth_with_local_webserver
from export import upload_gsheet
import numpy as np

API_ADDRESS = Core.API_ADDRESS
VERSION = Core.VERSION

token = read_token() or vk_auth_with_local_webserver()
ic(token)

with open(TOKEN_FILE, "w+") as f:
    f.write(token)

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
ad_ids = pd.DataFrame(columns=["campaign_id", "id", "client_id", "owner_id"])
for index, client in client_ids.iterrows():
    client_id = {client.id: "client_id", client.owner_id: "account_id"}
    client_id = {v: k for k, v in client_id.items()}
    params = {
        'access_token': token,
        'v': VERSION,
    }
    params.update(client_id)
    r = requests.get(f'{API_ADDRESS}ads.getAds',
                     params=params).json()
    data = r.get("response") if "response" in r else None
    ads = pd.DataFrame(data, columns=["campaign_id", "id"])
    ads["client_id"] = client.id
    ads["owner_id"] = client.owner_id
    ad_ids = pd.concat([ad_ids, ads])
    time.sleep(0.5)
ic(ad_ids)

# Getting statistics
list_of_owners = ad_accs_data.loc[:, "id"].to_list()
ic(list_of_owners)
ads_stats = pd.DataFrame(
    columns=["id", "impressions", "clicks", "spent", "day_from", "day_to"])
for owner in list_of_owners:
    ads = ad_ids.loc[ad_ids["owner_id"] == owner, "id"].tolist()
    while len(ads):
        needed = slice(min(len(ads), 2000))
        r = requests.post(f"{API_ADDRESS}ads.getStatistics", params={
                          'access_token': token,
                          'v': VERSION,
                          'account_id': owner,
                          'ids_type': 'ad',
                          'ids': ','.join(map(str, ads[needed])),
                          'period': 'overall',
                          'date_from': '0',
                          'date_to': '0'
                          }).json()
        del ads[needed]
        data = r.get("response") if "response" in r else None
        ic(data)
        # impressions, clicks, spent, day_start, day_end
        tmp_df = pd.DataFrame(data)
        ic(tmp_df)
        stats = pd.DataFrame(
            columns=["id", "impressions", "clicks", "spent", "day_from", "day_to"])
        for index, ad in tmp_df.iterrows():
            for ad_stats in ad.get("stats"):
                ad_with_stats = pd.DataFrame([{
                    "id": ad.get("id"),
                    "impressions": ad_stats.get("impressions"),
                    "clicks": ad_stats.get("clicks"),
                    "spent": ad_stats.get("spent"),
                    "day_from": ad_stats.get("day_from"),
                    "day_to": ad_stats.get("day_to"),
                }])
                stats = pd.concat([stats, ad_with_stats])
        ic(stats)
        ads_stats = pd.concat([ads_stats, stats])
ic(ads_stats)

# Merging data
full_data = ads_stats.merge(
    ad_ids, how="outer", on="id").replace({np.nan: None})
ic(full_data)

# Preparing for data export
prepared_data: list[tuple[str, str, pd.DataFrame]] = []
for index, client in client_ids.iterrows():
    client_id, owner_id, *other = client.values
    ic(client_id)
    ic(owner_id)
    client_data = full_data.loc[(full_data["client_id"] == client_id) & (full_data["owner_id"] == owner_id),
                                ["id", "impressions", "clicks", "spent", "day_from", "day_to", "campaign_id"]]
    prepared_data.append((str(owner_id), str(client_id)
                         if client_id != owner_id else "data", client_data))
    ic(prepared_data)

# Exporting data to xlsx
files_with_data = []
for filename_without_ext, sheet_name, client_data in prepared_data:
    filename = f"{filename_without_ext}.xlsx"
    client_data.reset_index(drop=True).to_excel(
        filename, sheet_name)
    files_with_data.append(filename)

# Uploading data to Google Drive
for *path_to_sheet, data in prepared_data:
    upload_gsheet(*path_to_sheet, data)
    time.sleep(0.5)
sys.exit()
