import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from app import config
from typing import Literal
import pandas as pd
from icecream import ic


def upload_gsheet(name, sheet_name, dataframe):
    creds_file = "credentials.json"
    gc = gspread.service_account(creds_file)
    sh = open_or_create_spreadsheet(gc, name)
    open_or_create_worksheet(sh, sheet_name, dataframe)
    sh.share(config.gmail, perm_type='user', role='writer')


def open_or_create_spreadsheet(client: gspread.Client, name: str):
    try:
        return client.open(name)
    except gspread.SpreadsheetNotFound:
        return client.create(name)


def open_or_create_worksheet(spreadsheet: gspread.Spreadsheet, name: str, dataframe: pd.DataFrame):
    ws: gspread.Worksheet
    try:
        ws = spreadsheet.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(name, *dataframe.shape)
    ws.update([dataframe.columns.values.tolist()] +
              dataframe.values.tolist())
