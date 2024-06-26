# Melhorias no projeto
## Preparando o ambiente
Nada demais: criação da virtualenv, instalação das dependências, migrações, criação do superuser etc.

## Reorganizando diretórios
1. Movemos os diretórios `galeria` e `usuarios` para o diretório `apps`.
2. Modificamos o arquivo `settings.py`, de maneira que as referências mudem de `aplicativo.apps.AplicativoConfig` para `apps.aplicativo.apps.AplicativoConfig`.

```python
# Exemplo em settins.py:
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Não se esqueça de modificar a referência para 'apps.galeria' no arquivo 'GaleriaConfig'.
    'apps.galeria.apps.GaleriaConfig',   
    # Não se esqueça de modificar a referência para 'apps.usuarios' no arquivo 'UsuariosConfig'.
    'apps.usuarios.apps.UsuariosConfig', 
]
```

3. Modifique os arquivos localizados em `aplicativo.apps.AplicativoConfig`, mudando o nome do aplicativo de `aplicativo` para `apps.aplicativo`.
```python
# Exemplo em apps.usuarios.apps.UsuariosConfig:
from django.apps import AppConfig

class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usuarios'
```
> O mesmo deve ser feito no arquivo `admin.py`, `urls.py` e `views.py` de cada app.

4. Atualize os paths no arquivo `setup\urls.py`. As rotas lá precisam ser atualizadas também.

## Refatorando a estilização
Movemos o arquivo `galerias/base.html` para `shared/base.html` e depois atualizamos os arquivos de template HTML que dependem desse `base.html`.

Os formulário de `usuarios/login.html` e `usuarios/cadastro.html` também precisam referenciar o arquivo movido `shared/base.html`.

Os arquivos de template do app `usuarios` dependiam do Bootstrap até agora. Vamos remover essa dependência e modificar o arquivo `setups/static/styles/style.css`.

# Inserir fotografias
## URLs e Views
Nada demais: acréscimo de algumas URLs do CRUD, das views associadas (inclusive algumas retornando `pass`) e modificações do HTML.

## Formulário de galeria
Foco nos Widgets e atributos dos objetos do formulário, que estarão contidos no arquivo `apps\galeria\forms.py`:

```python
from django import forms

from apps.galeria.models import Fotografia

class NovaImagemForm(forms.ModelForm):
    class Meta:
        model = Fotografia
        exclude = ['publicada',]
        widgets = {
            'nome' : forms.TextInput(attrs={'class' : 'form-control'}),
            'legenda' : forms.TextInput(attrs={'class' : 'form-control'}),
            'categoria' : forms.Select(attrs={'class' : 'form-control'}),
            'descricao' : forms.Textarea(attrs={'class' : 'form-control'}),
            'foto' : forms.FileInput(attrs={'class' : 'form-control'}),
            'data_fotografia' : forms.DateInput(
                attrs={
                    'type' : 'date',
                    'class' : 'form-control',
                },
                format = '%d/%m/%Y',
            ),
            'usuario' : forms.Select(attrs={'class' : 'form-control'}),
        }
```
> Elementos que compõem os widgets (dentro da classe `Meta`):
> 1. os Widgets costumam ter a palavra `Input` (exceção para `TextArea` e `Select`);
> 2. atributos CSS são acrescentados no construtor dos Widgets com o dicionário `attrs`;
> 3. o campo `DateInput` tem ainda o parâmetro de construtor chamado `format`.

## Lógica de novo item
Mudanças: 
1. O modelo `Fotografia` foi alterado: o campo `publicada` agora vai usar o valor default `True` ao invés de `False`;
2. Como o modelo mudou, foi necessário criar a migration do modelo de `Fotografia`;
3. O formulário em `forms.py` mudou de nome para `FotografiaForms`. Além disso, personalizamos os labels do formulário, usando o dicionário `labels` dentro da subclasse `Meta` do formulário;
4. A view `galerias.nova_imagem` inseriu lógica para evitar acesso por quem não está logado e uma operação de salvar caso o método do formulário seja `POST` (recurso ainda não testado).

Conteúdo do arquivo `app.galeria.views.py`:
```python
from django.shortcuts import render, get_object_or_404, redirect

from apps.galeria.models import Fotografia
from apps.galeria.forms import FotografiaForms

from django.contrib import messages
# Resto do código 
def nova_imagem(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Usuário não logado')
        return redirect('login')
    form = FotografiaForms()
    if request.method == 'POST':
        form = FotografiaForms(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nova fotografia cadastrada.')
            return redirect('index')
        
    return render(request, 'galeria/nova_imagem.html', {'form' : form})
```
Conteúdo do arquivo `app.galeria.forms.py`:
```python
from django import forms

from apps.galeria.models import Fotografia

class FotografiaForms(forms.ModelForm):
    class Meta:
        model = Fotografia
        exclude = ['publicada',]
        widgets = {
            # Resto do código
            'usuario' : forms.Select(attrs={'class' : 'form-control'}),
        }
        labels = {
            'descricao' : 'Descrição',
            'data_fotografia' : 'Data de registro',
            'usuario' : 'Usuário',
        }
```

## Templates e botões
Ao usar formulários que submetam arquivos (como os de imagem), é necessário modificar o HTML para que o tipo de encoding (`enctype`) seja `multipart-/form-data`:

```HTML
<!-- Arquivo templates\galeria\nova_imagem.html -->
<section class="galeria" style="margin-left: 5em">
    <form action="{% url 'nova_imagem' %}" method="POST" enctype="multipart/form-data">
        <!-- Resto do código -->
        <div>
            <button type="submit" class="btn btn-success col-12" style="padding: top 5px;">Cadastrar Nova Fotografia</button>
        </div>
    </form>
</section>
```

O backend precisa ser alterado também para processar formulários (note o parâmetro `request.FILES` na construção do formulário):
```python
## Arquivo apps\galeria\views.py

# Resto do código
def nova_imagem(request):
    # Resto do código
    form = FotografiaForms()
    if request.method == 'POST':
        form = FotografiaForms(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nova fotografia cadastrada.')
            return redirect('index')

```
# Deleção, edição e filtro
## Edição de fotografias
Modificando as rotas em `galeria/urls.py`:
```python
from django.urls import path
from apps.galeria.views import index, imagem, buscar, nova_imagem, editar_imagem, deletar_imagem

urlpatterns = [
    # Resto do código
    path('editar-imagem/<int:foto_id>', editar_imagem, name='editar_imagem'),
]
```
> Note a "tag" `/<int:foto_id>`: ela é o parâmetro fornecido para função `editar_imagem` na view.

Mudança em `views/galeria`:
```python
def editar_imagem(request, foto_id):
    fotografia = Fotografia.objects.get(id=foto_id)
    form = FotografiaForms(instance=fotografia)

    if request.method == 'POST':
        form = FotografiaForms(request.POST, request.FILES, instance=fotografia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fotografia editada com sucesso.')
            return redirect('index')

    return render(
        request, 
        'galeria/editar_imagem.html', 
        {
            'form' : form,
            'foto_id' : foto_id,
        }
    )
```

Como referenciar a função `editar_imagem` no template de `galeria/imagem.html`:
```html
<a href="{% url 'editar_imagem' fotografia.id %}">Editar</a>
```

Template para `galeria/editar_imagem.html`:
```html
{% extends 'shared/base.html' %}
{% load static %}
{% block content %}
<section class="galeria" style="margin-left: 5em">
    <form action="{% url 'editar_imagem' foto_id %}" method="POST" enctype="multipart/form-data">
        {% csrf_token %}
        <div class="row">
            {% for field in form.visible_fields %}
            <div class="col-12 col-lg-12" style="margin-bottom: 10px;">
                <label for="{{ field.id_for_label }}">{{field.label}}</label>
                {{ field }}
            </div>
            {% endfor %}
        </div>
        <div>
            <button type="submit">Editar Fotografia</button>
        </div>
    </form>
</section>
{% endblock %}
```
## Deleção de fotografias
Modificando as rotas em `galeria/urls.py`:
```python
from django.urls import path
from apps.galeria.views import index, imagem, buscar, nova_imagem, editar_imagem, deletar_imagem

urlpatterns = [
    # Resto do código
    path('deletar-imagem', deletar_imagem, name='deletar_imagem'),
]
```
> Note a "tag" `/<int:foto_id>`: ela é o parâmetro fornecido para função `deletar_imagem` na view.

Mudança em `views/galeria`:
```python
def deletar_imagem(request, foto_id):
    fotografia = Fotografia.objects.get(id=foto_id)
    fotografia.delete()
    messages.success(request, 'Fotografia deletada com sucesso.')
    return redirect('index')
```

Como referenciar a função `deletar_imagem` no template de `galeria/imagem.html`:
```html
<a href="{% url 'deletar_imagem' fotografia.id %}">Deletar</a>
```

## Funcionalidade de filtro
Inclusão da rota de filtros em `galeria/urls.py`:
```python
from django.urls import path
from apps.galeria.views import (
    # Resto do código
    filtro,
)

urlpatterns = [
    # Resto do código
    path('filtro/<str:categoria>', filtro, name='filtro'),
]
```

Criação da view de filtro em `galeria/views.py`:
```python
def buscar(request):
    # Resto do código
    # Vamos remover a antiga página `galeria/buscar.html`.
    return render(request, "galeria/index.html", {"cards": fotografias})

# Resto do código
def filtro(request, categoria):
    fotografias = Fotografia.objects.order_by("data_fotografia").filter(publicada=True, categoria=categoria)
    return render(request, 'galeria/index.html', { 'cards' : fotografias})
```

Mudança no template `galeria/index.html` para conter as referências à nova view de filtro:
```html
<ul class="tags__lista">
    <li class="tags__tag"><a href="{% url 'filtro' 'NEBULOSA' %}">Nebulosa</a></li>
    <li class="tags__tag"><a href="{% url 'filtro' 'ESTRELA' %}">Estrela</a></li>
    <li class="tags__tag"><a href="{% url 'filtro' 'GALÁXIA' %}">Galáxia</a></li>
    <li class="tags__tag"><a href="{% url 'filtro' 'PLANETA' %}">Planeta</a></li>
</ul>
```

# Lidando com a AWS
## Criando um bucket no S3
O bucket AWS tem uma configuração de lista de controle de acesso (ACL - Access Control List).

É necessário criar um usuário que vai fazer o acesso ao bucket.

## Criando um usuário na IAM
O IAM (Identity and Access Management) é um meio de controlar o acesso de usuários a recursos e serviços da AWS.

Ao criar um usuário no IAM:
* não habilite o acesso ao console (por que?);
* escolha, na opção de anexar políticas diretamente, a política `AmazonS3FullAccess`;
* na aba `Credenciais de segurança`, escolha a opção `Criar chave de acesso`. Em seguida, escolha a credencial de `Command Line Interface (CLI)`. Isso vai gerar um par `Chave de acesso` e `Chave de acesso secreta`.

# Melhorando a persistência
## Conexão com o Django
Inclua a dependência para as bibliotecas `django-storages` e `boto3`.

Altere as configurações do arquivo `settings.py` logo antes da variável `STATIC_URL` (ou outra variável que começa com static):
```python
# settings.py

# Resto do código

# AWS Configuração
AWS_ACCESS_KEY_ID = 'teste'
AWS_SECRET_ACCESS_KEY_ID = 'teste'
AWS_STORAGE_BUCKET_NAME = 'incredible-hulk'
MEU_DOMINIO = 's3.amazonaws.com'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.{MEU_DOMINIO}' # Caminho dos arquivos.
AWS_DEFAULT_ACL = 'public-read' # Nome do ACL (Lista de Controle de Acesso).
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl' : 'max-age=86400',
}
AWS_LOCATION = 'static'
AWS_QUERYSTRING_AUTH = False
AWS_HEADERS = {
    'Access-Control-Allow-Origin' : '*',
}
# Resto do código
```
## Fotografias no bucket
Atualização do arquivo `setup.settings.py`:
```python
# Resto do código
INSTALLED_APPS = [
    # Resto do código
    # Referência à dependência django-storages
    'storages', 
]
# Resto do código

# AWS Configuração
AWS_ACCESS_KEY_ID = 'teste'
AWS_SECRET_ACCESS_KEY_ID = 'teste'
AWS_STORAGE_BUCKET_NAME = 'incredible-hulk'
MEU_DOMINIO = 's3.amazonaws.com'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.{MEU_DOMINIO}' # Caminho dos arquivos na AWS.
AWS_DEFAULT_ACL = 'public-read' # Nome do ACL (Lista de Controle de Acesso).
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl' : 'max-age=86400',
}
AWS_LOCATION = 'static'
AWS_QUERYSTRING_AUTH = False
AWS_HEADERS = {
    'Access-Control-Allow-Origin' : '*',
}

# Documentação antiga (usada no curso): https://django-storages.readthedocs.io/en/1.5.2/backends/amazon-S3.html
# Variáveis na documentação antiga:
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# STATICFILES_STORAGE = 'storages.backends.s3boto.S3Boto3Storage' # Este import falha.
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# STATIC_URL = 'static/' # Anterior
STATIC_URL = f'http://{AWS_S3_CUSTOM_DOMAIN}/static/' # A barra no final é obrigatória.

# Resto do código 
# MEDIA_URL = "/media/" # Anterior
MEDIA_URL = f'http://{AWS_S3_CUSTOM_DOMAIN}/media/'

```

Atualização do arquivo `setup.urls.py`:
```python
# Resto do código
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```
Depois de atualizar essa referência, precisamos modificar os templates que referenciam o app `static`, removendo a primeira barra de cada referência da função `static`.
```HTML
<!-- Resto do código -->
<link rel="stylesheet" href="{% static 'styles/style.css' %}">
<!-- Resto do código -->
<img src="{% static 'assets/logo/Logo(2).png' %}" alt="Logo da Alura Space" />
```

# Melhorando a segurança
Use a biblioteca `dotenv` para ocultar informações sensíveis (nome e endereço do bucket, usuário e senha etc.).

Outra coisa é o gerador de chaves secretas do Django (veja o conteúdo do arquivo `scripts\secret_key_generator.py`):
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```
> Para gerar a chave secreta, basta executar o script num terminal. Depois você pode copiar essa secret_key para o arquivo `.env`. Como o arquivo `.env` está no `.gitignore`, vamos deixar um exemplo no arquivo `.env.exemplo`.

Mudanças no arquivo `setup\settings.py`:
```python
# Resto do código
# AWS Configuração
AWS_ACCESS_KEY_ID = str(os.getenv('AWS_ACCESS_KEY_ID'))
AWS_SECRET_ACCESS_KEY_ID = str(os.getenv('AWS_SECRET_ACCESS_KEY_ID'))
AWS_STORAGE_BUCKET_NAME = str(os.getenv('AWS_STORAGE_BUCKET_NAME'))
# Resto do código
```

Conteúdo do arquivo `.env`:
```bash
SECRET_KEY = 'u2*i1ldhsc4q(xox5tbk1o=zx=xy1a2e2m!0!t06juzild1$-j'
AWS_ACCESS_KEY_ID = 'teste'
AWS_SECRET_ACCESS_KEY_ID = 'teste'
AWS_STORAGE_BUCKET_NAME = 'incredible-hulk'
```
