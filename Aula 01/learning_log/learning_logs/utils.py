import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import logging
from colorama import Fore, Style

# Configuração do logging
logging.basicConfig(filename='drive_api.log', level=logging.ERROR)

# Caminho para o arquivo de credenciais e ID do Drive compartilhado
GOOGLE_APPLICATION_CREDENTIALS = r"C:\Users\Geral\Desktop\UploadContratoAutomatico\Aula 01\learning_log\credentials\uploadcontratos-442920-9f346da0dfce.json"
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

        # Query para listar apenas pastas no Drive compartilhado
        query = f"'{DRIVE_ID}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"

        page_token = None  # Para paginação

        print("Testando a conexão com a API...")
        # Loop para listar todas as pastas
        while True:
            print("Conexão estabelecida")
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


def upload_pdf_to_folders(file_path, folder_ids):

    SCOPES = ['https://www.googleapis.com/auth/drive']
    credentials = Credentials.from_service_account_file(
        r"C:\Users\Geral\Desktop\UploadContratoAutomatico\Aula 01\learning_log\credentials\uploadcontratos-442920-9f346da0dfce.json",
        scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)

    results = {}
    for folder_id in folder_ids:
        try:
            # Obter o nome da pasta pai
            folder_metadata = service.files().get(
                fileId=folder_id,
                fields="name",
                supportsAllDrives=True
            ).execute()
            parent_folder_name = folder_metadata.get('name')
            if "- (" in parent_folder_name:
                parent_folder_name = parent_folder_name.split(" - (")[0].strip()
            else:
                parent_folder_name = parent_folder_name.split(" - ANCINE")[0].strip()
            parent_folder_name = parent_folder_name.title()

            print(Fore.CYAN + f"Nome da pasta pai: {parent_folder_name}" + Style.RESET_ALL)

            # Busca subpastas na pasta pai
            query_main = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            subpastas = []
            page_token_main = None

            while True:
                response_main = service.files().list(
                    q=query_main,
                    spaces='drive',
                    fields='nextPageToken, files(id, name)',
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                    pageToken=page_token_main
                ).execute()

                for subfolder in response_main.get('files', []):
                    subpastas.append({'id': subfolder['id'], 'name': str(subfolder['name']).lower()})
                    print(Fore.YELLOW + f"Nome da subpasta: {subfolder['name']}" + Style.RESET_ALL)
                    print(Fore.YELLOW + f"ID da subpasta: {subfolder['id']}" + Style.RESET_ALL)

                    # Se encontra "7. Contratos" ou "5. Contratos", busca subpastas dentro dela
                    if str(subfolder['name']).lower() in ["7. contratos", "5. contratos"]:
                        print(Fore.MAGENTA + "Pasta 'Contratos' encontrada" + Style.RESET_ALL)
                        id_PastaContratos = subfolder['id']
                        query_sub = f"'{id_PastaContratos}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
                        page_token_sub = None

                        while True:
                            response_sub = service.files().list(
                                q=query_sub,
                                spaces='drive',
                                fields='nextPageToken, files(id, name)',
                                supportsAllDrives=True,
                                includeItemsFromAllDrives=True,
                                pageToken=page_token_sub
                            ).execute()

                            for subfolder3 in response_sub.get('files', []):
                                print(Fore.YELLOW + f"Nome da subpasta: {subfolder3['name']}" + Style.RESET_ALL)
                                print(Fore.YELLOW + f"ID da subpasta: {subfolder3['id']}" + Style.RESET_ALL)
                                if str(subfolder3['name']).lower() == "c. contratos de exibição":
                                    print(Fore.MAGENTA + "Pasta 'c. Contratos de Exibição' encontrada" + Style.RESET_ALL)
                                    # Salvar o ID da pasta encontrada
                                    id_PastaContratosExib = subfolder3['id']

                                    # Nome personalizado: Nome do arquivo + Nome da pasta pai
                                    base_name = os.path.basename(file_path).replace("_", " ").replace(".pdf", "")  # Substituir underscores e remover extensão
                                    new_file_name = f"{base_name} - {parent_folder_name}.pdf"  # Adicionar extensão .pdf no final

                                    # Metadados do arquivo
                                    file_metadata = {
                                        'name': new_file_name,
                                        'parents': [id_PastaContratosExib]
                                    }

                                    # Enviar arquivo
                                    media = MediaFileUpload(file_path, mimetype='application/pdf')
                                    uploaded_file = service.files().create(
                                        body=file_metadata,
                                        media_body=media,
                                        fields='id, name, parents',
                                        supportsAllDrives=True  # Suporte para Drives compartilhados
                                    ).execute()

                                    results[folder_id] = Fore.GREEN + f"Arquivo enviado com sucesso: {uploaded_file['name']} (ID: {uploaded_file['id']})" + Style.RESET_ALL
                                    print(Fore.GREEN + "Contrato subido na pasta 'c. Contratos de Exibição'" + Style.RESET_ALL)
                                    break  # Interrompe a busca após encontrar e enviar o arquivo
                                else:
                                    print(Fore.MAGENTA + "Pasta 'c. Contratos de Exibição' não encontrada" + Style.RESET_ALL)

                            page_token_sub = response_sub.get('nextPageToken', None)
                            if page_token_sub is None:
                                break

                page_token_main = response_main.get('nextPageToken', None)
                if page_token_main is None:
                    break

        except Exception as e:
            results[folder_id] = Fore.RED + f"Erro: Não foi possível enviar o arquivo para a pasta '{folder_id}'. Detalhes: {e}" + Style.RESET_ALL

    return results
