from django.shortcuts import render


from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

from .reports.reports import *
from .models import *
from .urls import *
from django.urls import get_resolver
import csv, json
from .forms import ImportFileForm


login_url='login'
# Create your views here.

@login_required(login_url=login_url)
def index(request, counter: int = 2):
    imagens = Imagem.objects.all()
    graficos = [imagem.imagem.url for imagem in imagens if imagem.imagem.name.lower().endswith(('.png', '.jpg', '.jpeg'))]

    # Check if the request is from a mobile
    if request.META.get('HTTP_USER_AGENT'):
        user_agent = request.META['HTTP_USER_AGENT'].lower()
        if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
            counter = 1

    return render(request, "index.html", {
        "counter": counter,
        "graficos": graficos
    })

@login_required(login_url=login_url)
def reports(request):
    content = {
        'title': 'Reports',
        'description': 'This is the reports page.',
        'data': []
    }
    return render(request, 'financas/reports.html', content)


# User
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.groups.filter(name='Pendente').exists() and not user.is_staff and not user.is_superuser:
                messages.error(request, 'O utilizador está pendente de aprovação.')
            else:
                login(request, user)
                return redirect('index')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'user/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required(login_url=login_url)
def user_management(request):
    return render(request, 'user/management.html')

# Alunos
@login_required(login_url=login_url)
def dashboard_alunos(request):
    content = {
        'title': 'Dashboard Alunos',
        'valencia': gerar_grafico_numero_alunos_por_valencia(),
        'sala': gerar_grafico_alunos_por_sala(),
    }
    return render(request, 'alunos/dashboard.html', content)

@login_required(login_url=login_url)
def galeria(request):
    imagens_por_tipo = {}
    imagens = Imagem.objects.prefetch_related('tipo_imagem_id').all()

    for imagem in imagens:
        for tipo in imagem.tipo_imagem_id.all():
            tipo_nome = tipo.tipo_imagem
            if tipo_nome not in imagens_por_tipo:
                imagens_por_tipo[tipo_nome] = []
            imagens_por_tipo[tipo_nome].append(imagem)
    counter = 3
    # Check if the request is from a mobile
    if request.META.get('HTTP_USER_AGENT'):
        user_agent = request.META['HTTP_USER_AGENT'].lower()
        if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
            counter = 1
    content = {
        'imagens_por_tipo': imagens_por_tipo,
        'counter': counter,
    }
    return render(request, 'testes/galeria.html', content)

@login_required(login_url='login')
def import_data(request):
    error = None
    preview = None
    model_names = [model.__name__ for model in apps.get_app_config('data_hub').get_models()]

    if request.method == 'POST':
        form = ImportFileForm(request.POST, request.FILES)
        selected_model = request.POST.get('model')
        if 'confirm' not in request.POST:
            # Primeira submissão: upload do ficheiro
            if form.is_valid() and selected_model in model_names:
                f = request.FILES['file']
                ext = f.name.split('.')[-1].lower()
                if ext not in ['csv', 'json']:
                    error = 'Invalid file extension. Only CSV or JSON allowed.'
                else:
                    # Leitura dos dados
                    if ext == 'csv':
                        decoded = f.read().decode('utf-8').splitlines()
                        reader = csv.DictReader(decoded)
                        data = list(reader)
                    else:
                        data = json.load(f)
                    preview = data
            else:
                error = "Invalid form or model not selected."
        else:
            # Segunda submissão: importação dos dados selecionados
            preview = json.loads(request.POST.get('data_json'))
            form = ImportFileForm(request.POST)
            selected_model = request.POST.get('model')
            Model = apps.get_model('data_hub', selected_model)
            replace = form.cleaned_data.get('replace', False)
            selected_rows = request.POST.getlist('rows')
            for i, row in enumerate(preview):
                clean_row = {k: v for k, v in row.items() if k}
                if str(i) in selected_rows:
                    if replace:
                        Model.objects.update_or_create(id=clean_row.get('id'), defaults=clean_row)
                    else:
                        Model.objects.get_or_create(id=clean_row.get('id'), defaults=clean_row)
            return redirect('index')

        if preview is not None and not error:
            # Passa os dados para o preview como JSON escondido
            import json as pyjson
            return render(request, 'import/import_preview.html', {
                'form': form,
                'data': preview,
                'model_names': model_names,
                'selected_model': selected_model,
                'data_json': pyjson.dumps(preview)
            })

    else:
        form = ImportFileForm()
    return render(request, 'import/import.html', {
        'form': form,
        'error': error,
        'model_names': model_names,
        'selected_model': request.POST.get('model', '')
    })