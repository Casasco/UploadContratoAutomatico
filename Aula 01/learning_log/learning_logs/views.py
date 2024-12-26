from django.http import HttpResponse
from django.shortcuts import render
from .models import Projeto 
from .utils import listar_pastas_drive
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render

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
    
def subir_arquivo(request):
    """View para chamar método que sobe os arquivos para o drive"""
    if request.method == 'POST':
        id_pasta = request.POST.getlist('id_array')
        array_id = []
        for id in id_pasta:
            # Adiciona o ID entre aspas duplas
            array_id.append(f'"{id}"')

        # Exemplo de debug: Imprimir o resultado para ver os IDs processados
        print(array_id)

         # Receber o arquivo selecionado
        uploaded_file = request.FILES.get('uploaded_file')
        if uploaded_file:
            # Salvar o arquivo no sistema de arquivos local temporariamente
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads'))
            file_path = fs.save(uploaded_file.name, uploaded_file)
            file_url = fs.url(file_path)

            # Debug: Exibir informações do arquivo e IDs
            print(f"Arquivo enviado: {uploaded_file.name}")
            print(f"IDs das pastas: {array_id}")

            # Aqui você pode adicionar a lógica para manipular o arquivo no Google Drive
            # ou outro destino necessário.
        else:
            return HttpResponse("Nenhum arquivo enviado.", status=400)

        return render(request, 'learning_logs/subir_arquivo.html', {'array': array_id, 'file_url': file_url})
    else:
        return HttpResponse("Método inválido.", status=400)


