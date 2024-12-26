import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import logging

# Configuração do logging
logging.basicConfig(filename='drive_api.log', level=logging.ERROR)

# Caminho para o arquivo de credenciais e ID do Drive compartilhado
GOOGLE_APPLICATION_CREDENTIALS = r"C:\Users\Geral\Desktop\Curso de Django\Aula 01\learning_log\credentials\uploadcontratos-442920-8e111876b414.json"
DRIVE_ID = '0AKlI-riQF64nUk9PVA'

def listar_pastas_drive():
    """
    Lista todas as pastas em um Drive compartilhado do Google Drive.
    Retorna:
        Uma lista de dicionários, onde cada dicionário representa uma pasta e contém
        os campos 'id' e 'name'.
    """

    folders = []  # Lista que armazenará as pastas

    try:
        # Configuração do escopo e credenciais
        SCOPES = ['https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(
            GOOGLE_APPLICATION_CREDENTIALS, scopes=SCOPES
        )

        # Criação do serviço Google Drive
        service = build('drive', 'v3', credentials=creds)

        # Teste simples: lista os 5 primeiros arquivos no Drive
        print("Testando a conexão com a API...")
        results = service.files().list(
            pageSize=5,
            fields="nextPageToken, files(id, name)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()

        items = results.get('files', [])
        print("Arquivos retornados no teste:")
        for item in items:
            print(f"ID: {item['id']}, Nome: {item['name']}")

        # Query para listar apenas pastas no Drive compartilhado
        query = f"'{DRIVE_ID}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"

        page_token = None  # Para paginação

        # Loop para listar todas as pastas
        while True:
            response = service.files().list(
                q=query,
                spaces='drive',
                fields='nextPageToken, files(id, name)',
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                pageToken=page_token
            ).execute()

            for file in response.get('files', []):
                folders.append({'id': file.get('id'), 'name': file.get('name')})

            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

    except Exception as e:
        print(f"Erro ao autenticar na API ou buscar arquivos: {e}")
        logging.error(f"Erro ao listar pastas: {str(e)}")

    return folders  # Retorna a lista de pastas


def uploadAndCopyFile(arquivoPrincipal, targetFolders):
    try:
        # Configuração do escopo e credenciais
        SCOPES = ['https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(
            GOOGLE_APPLICATION_CREDENTIALS, scopes=SCOPES
        )
    return

        


  


