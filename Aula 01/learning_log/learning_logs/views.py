from django.http import HttpResponse
from django.shortcuts import render
from .models import Projeto 
from .utils import listar_pastas_drive
from .utils import upload_pdf_to_folders
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import JsonResponse
from django.utils.text import slugify
from colorama import Fore, Style

# Create your views here.

def index(request):
    """Página principal"""
    pastas = listar_pastas_drive()  # Obtém as pastas do Google Drive
    context = {'pastas': pastas}  # Adiciona ao contexto
    return render(request, 'learning_logs/index.html', context)

def salvar_ids(request):
    """View para processar os IDs e nomes das pastas selecionadas"""
    if request.method == 'POST':
        # Captura os valores enviados no formulário
        pastas_selecionadas = request.POST.getlist('pastas')

        # Separar IDs e nomes
        resultado = []
        array_id = []
        for pasta in pastas_selecionadas:
            id_pasta, nome_pasta = pasta.split('|')  # Divide o valor "id|name"
            resultado.append({'id': id_pasta, 'name': nome_pasta})
            array_id.append(id_pasta)  # Adiciona apenas o ID ao array

        # Renderiza o template 'salvar_ids.html' com as pastas selecionadas e IDs
        return render(request, 'learning_logs/salvar_ids.html', {'pastas': resultado,'id_array': array_id})
    else:
        return HttpResponse("Método inválido.", status=400)
    
import os
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

def subir_arquivo(request):
    """View para chamar método que sobe os arquivos para o drive"""
    if request.method == 'POST':
        id_pasta = request.POST.getlist('id_array')
        array_id = [id.strip('"') for id in id_pasta]
        print(Fore.YELLOW + "IDs das pastas processados para upload:" + Style.RESET_ALL, array_id)

        # Debug: Exibir IDs processados
        print(Fore.YELLOW + "IDs das pastas recebidos:" + Style.RESET_ALL, array_id)

        # Receber o arquivo selecionado
        uploaded_file = request.FILES.get('uploaded_file')
        if uploaded_file:
            # Salvar o arquivo no sistema de arquivos local temporariamente
            temp_dir = r"C:\Temp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            file_path = os.path.join(temp_dir, uploaded_file.name.replace(" ", "_"))

            try:
                # Salvar o arquivo localmente
                with open(file_path, 'wb') as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)

                # Chamar a função para fazer o upload do arquivo para o Google Drive
                results = upload_pdf_to_folders(file_path, array_id)

                # Debug: Exibir informações do arquivo e IDs
                print(Fore.GREEN + f"Arquivo enviado: {uploaded_file.name}" + Style.RESET_ALL)
                print(Fore.GREEN + f"IDs das pastas: {array_id}" + Style.RESET_ALL)

                # Remover o arquivo temporário
                os.remove(file_path)

                # Retornar resultados como JSON
                return JsonResponse({'results': results})
            except Exception as e:
                print(Fore.RED + f"Erro ao processar o arquivo: {str(e)}" + Style.RESET_ALL)
                return HttpResponse(Fore.RED + "Erro ao processar o arquivo." + Style.RESET_ALL, status=500)
        else:
            return HttpResponse("Nenhum arquivo enviado.", status=400)

    return render(request, 'learning_logs/subir_arquivo.html', {'array': array_id})



