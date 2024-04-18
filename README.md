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
