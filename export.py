import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from app import config


def upload_gsheet(name, sheet_name, dataframe):
    creds_file = "credentials.json"
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    gc = gc = gspread.service_account(creds_file)
    sh = gc.create(name)
    worksheet = sh.add_worksheet(sheet_name, 1000, 1000)
    worksheet.update([dataframe.columns.values.tolist()] +
                     dataframe.values.tolist())
    sh.share(config.gmail, perm_type='user', role='writer')
