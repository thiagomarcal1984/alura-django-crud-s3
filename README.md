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
