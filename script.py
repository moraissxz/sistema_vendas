import os
import subprocess
import sys


def executar_comando(comando, descricao):
    print(f"\n⚙️  {descricao}...")
    resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
    if resultado.returncode == 0:
        print(f"✅ {descricao} - OK")
    else:
        print(f"❌ Erro: {resultado.stderr}")
    return resultado.returncode == 0


def criar_arquivo(caminho, conteudo=""):
    dirname = os.path.dirname(caminho)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print(f"📄 Criado: {caminho}")


def criar_pasta(caminho):
    os.makedirs(caminho, exist_ok=True)
    print(f"📁 Criada: {caminho}")


def main():
    print("=" * 50)
    print("Criando projeto Sorveteria")
    print("=" * 50)

    if sys.platform == "win32":
        pip = "venv\\Scripts\\pip"
        python = "venv\\Scripts\\python"
    else:
        pip = "venv/bin/pip"
        python = "venv/bin/python"

    executar_comando("python3 -m venv venv", "Criando ambiente virtual")
    executar_comando(f"{pip} install --upgrade pip", "Atualizando pip")
    executar_comando(
        f"{pip} install django psycopg2-binary Pillow python-decouple whitenoise gunicorn",
        "Instalando dependencias"
    )
    executar_comando(f"{python} -m django startproject sorveteria .", "Criando projeto Django")
    executar_comando(f"{python} manage.py startapp loja", "Criando app loja")

    pastas = [
        "templates/loja",
        "static/css",
        "static/js",
        "static/img",
        "media/produtos",
        "loja/templatetags",
    ]
    print("\nCriando pastas...")
    for pasta in pastas:
        criar_pasta(pasta)

    arquivos = [
        "loja/templatetags/__init__.py",
        "loja/templatetags/loja_tags.py",
        "loja/carrinho.py",
        "loja/whatsapp.py",
        "loja/context_processors.py",
        "loja/urls.py",
        "templates/base.html",
        "templates/loja/index.html",
        "templates/loja/produtos.html",
        "templates/loja/carrinho.html",
        "templates/loja/checkout.html",
        "templates/loja/pedido_finalizado.html",
        "templates/loja/detalhe_produto.html",
        "static/css/style.css",
        "static/js/carrinho.js",
    ]
    print("\nCriando arquivos...")
    for arquivo in arquivos:
        criar_arquivo(arquivo)

    criar_arquivo("requirements.txt",
        "Django==4.2.7\n"
        "psycopg2-binary==2.9.9\n"
        "Pillow==10.1.0\n"
        "python-decouple==3.8\n"
        "whitenoise==6.6.0\n"
        "gunicorn==21.2.0\n"
    )

    criar_arquivo(".env",
        "SECRET_KEY=django-insecure-troque-isso\n"
        "DEBUG=True\n"
        "ALLOWED_HOSTS=localhost,127.0.0.1\n"
        "DB_NAME=sorveteria_db\n"
        "DB_USER=postgres\n"
        "DB_PASSWORD=sua_senha_aqui\n"
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "WHATSAPP_NUMERO=5511999999999\n"
        "NOME_SORVETERIA=Sorveteria Gelato Divino\n"
    )

    criar_arquivo(".gitignore",
        "__pycache__/\n"
        "*.pyc\n"
        "venv/\n"
        ".env\n"
        "*.log\n"
        "media/\n"
        "staticfiles/\n"
        "db.sqlite3\n"
    )

    criar_arquivo("README.md",
        "# Sorveteria\n"
        "Sistema de vendas com WhatsApp.\n"
    )

    print("\n" + "=" * 50)
    print("ESTRUTURA CRIADA COM SUCESSO!")
    print("=" * 50)
    print("\nPROXIMOS PASSOS:")
    print("1. source venv/bin/activate")
    print("2. Configure o .env")
    print("3. python manage.py migrate")
    print("4. python manage.py createsuperuser")
    print("5. python manage.py runserver")


if __name__ == "__main__":
    main()
