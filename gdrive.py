from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
SCOPES = ['https://www.googleapis.com/auth/drive']
import datetime
import random


class GDrive():

    def start_connection():
        #Create the credentials object that link the bot to drive
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        #Load the connection up
        GDrive.service = build('drive', 'v3', credentials=creds)

    def get_current_dir():
        #Get current date
        folder_name = datetime.datetime.now().strftime('%x')
        page_token = None
        while True:
            response = GDrive.service.files().list(q = "mimeType = 'application/vnd.google-apps.folder' and trashed = False and 'root' in parents",
                                                  spaces='drive',
                                                  fields='nextPageToken, files(id, name)',
                                                  pageToken=page_token).execute()
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        for folder in response.get('files', []):
            if folder.get('name') == folder_name: #We already have a folder. Just dump everything here
                folder_id = folder.get('id')
                folder_id_string = "'"+folder_id+"'" #Used only for the mime type
                while True:
                    response = GDrive.service.files().list(q=folder_id_string+ " in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = False",
                                                          spaces='drive',
                                                          fields='nextPageToken, files(id, name)',
                                                          pageToken=page_token).execute()
                    page_token = response.get('nextPageToken', None)
                    if page_token is None:
                        break
                file_numbers=[]
                for file in response.get('files', []):
                    file_numbers.append(file.get('name'))
                maximum = max(file_numbers, default = 1)
                new_folder_number = str(int(maximum)+1)
                new_folder_metadata = {'name': new_folder_number, 'parents' : [folder_id], 'mimeType': 'application/vnd.google-apps.folder'}
                new_folder = GDrive.service.files().create(body=new_folder_metadata,fields='id').execute()
                new_folder_id = new_folder.get('id')
                break
            else:# In this case we dont have a folder for today and we have to create one
                new_date_folder_name = datetime.datetime.now().strftime('%x')
                new_folder_metadata = {'name': new_date_folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
                new_date_folder = GDrive.service.files().create(body=new_folder_metadata,fields='id').execute()
                date_folder_id = new_date_folder.get('id')
                #Now create the new folder for the bug report or feature request
                new_folder_metadata = {'name': '1', 'parents' : [date_folder_id], 'mimeType': 'application/vnd.google-apps.folder'}
                new_folder = GDrive.service.files().create(body=new_folder_metadata,fields='id').execute()
                new_folder_id = new_folder.get('id')
                break
        return new_folder_id

    def upload_picture(filepath,drive_loaction):
        file_name = str(random.randint(0,15000)) +'.jpg'
        file_metadata = {'name': file_name, 'parents': [drive_loaction]}
        media = MediaFileUpload(filepath,mimetype='image/jpeg')
        file = GDrive.service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()

    def upload_video(filepath, drive_loaction):
        file_name = str(random.randint(0,15000)) +'.mp4'
        file_metadata = {'name': file_name, 'parents': [drive_loaction]}
        media = MediaFileUpload(filepath,mimetype='video/mp4')
        file = GDrive.service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()

    def upload_textfile(filepath, drive_loaction):
        file_name = 'info.txt'
        file_metadata = {'name': file_name, 'parents': [drive_loaction]}
        media = MediaFileUpload(filepath,mimetype='unknown/txt')
        file = GDrive.service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()




GDrive.start_connection()
