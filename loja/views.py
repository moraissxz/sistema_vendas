import json
import re
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator

from .models import Produto, Categoria
from .carrinho import Carrinho
from .whatsapp import gerar_mensagem_carrinho, gerar_link_whatsapp
from .forms import FormularioRegistro, FormularioLogin


# =============================================
# HELPERS
# =============================================

def _sanitizar_texto(texto, max_len=300):
    """Remove caracteres de controle e limita o tamanho do texto."""
    if not texto:
        return ''
    # Remove tabulações, quebras de linha múltiplas, caracteres de controle
    texto = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', texto)
    texto = texto.strip()
    return texto[:max_len]


# =============================================
# AUTENTICAÇÃO
# =============================================

def pagina_registro(request):
    if request.user.is_authenticated:
        return redirect('pagina_inicial')
    if request.method == 'POST':
        form = FormularioRegistro(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, f'Bem-vindo, {usuario.first_name}!')
            return redirect('pagina_inicial')
        else:
            messages.error(request, 'Corrija os erros abaixo.')
    else:
        form = FormularioRegistro()
    return render(request, 'loja/registro.html', {
        'form': form,
        'titulo_pagina': 'Criar Conta',
    })


def pagina_login(request):
    if request.user.is_authenticated:
        return redirect('pagina_inicial')
    if request.method == 'POST':
        form = FormularioLogin(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            usuario = authenticate(request, username=username, password=password)
            if usuario is not None:
                login(request, usuario)
                messages.success(
                    request,
                    f'Bem-vindo, {usuario.first_name or usuario.username}!'
                )
                return redirect(request.GET.get('next', 'pagina_inicial'))
            else:
                messages.error(request, 'Usuario ou senha incorretos.')
    else:
        form = FormularioLogin()
    return render(request, 'loja/login.html', {
        'form': form,
        'titulo_pagina': 'Entrar',
    })


def pagina_logout(request):
    logout(request)
    messages.info(request, 'Voce saiu da sua conta.')
    return redirect('pagina_inicial')


# =============================================
# PÁGINAS PRINCIPAIS
# =============================================

def pagina_inicial(request):
    produtos_destaque = Produto.objects.filter(
        disponivel=True, destaque=True
    ).select_related('categoria')[:6]
    categorias = Categoria.objects.filter(ativo=True)
    return render(request, 'loja/index.html', {
        'produtos_destaque': produtos_destaque,
        'categorias': categorias,
        'titulo_pagina': 'Inicio',
    })


def lista_produtos(request):
    from django.db.models import Q

    categoria_id = request.GET.get('categoria')
    busca = request.GET.get('busca', '').strip()

    produtos = Produto.objects.filter(
        disponivel=True
    ).select_related('categoria')

    categoria_selecionada = None

    if categoria_id:
        try:
            categoria_selecionada = get_object_or_404(
                Categoria, id=categoria_id, ativo=True
            )
            produtos = produtos.filter(categoria=categoria_selecionada)
        except (ValueError, TypeError):
            pass

    # Busca por nome E descrição
    if busca:
        produtos = produtos.filter(
            Q(nome__icontains=busca) | Q(descricao__icontains=busca)
        )

    categorias = Categoria.objects.filter(ativo=True)

    # Paginação: 12 produtos por página
    paginator = Paginator(produtos, 12)
    pagina_num = request.GET.get('pagina', 1)
    try:
        pagina_obj = paginator.page(pagina_num)
    except Exception:
        pagina_obj = paginator.page(1)

    return render(request, 'loja/produtos.html', {
        'produtos': pagina_obj,
        'pagina_obj': pagina_obj,
        'categorias': categorias,
        'categoria_selecionada': categoria_selecionada,
        'busca': busca,
        'total_produtos': paginator.count,
        'titulo_pagina': 'Cardapio',
    })


def detalhe_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id, disponivel=True)
    produtos_relacionados = Produto.objects.filter(
        disponivel=True,
        categoria=produto.categoria
    ).exclude(id=produto_id)[:4]
    return render(request, 'loja/detalhe_produto.html', {
        'produto': produto,
        'produtos_relacionados': produtos_relacionados,
        'titulo_pagina': produto.nome,
    })


# =============================================
# CARRINHO
# =============================================

def ver_carrinho(request):
    carrinho = Carrinho(request)
    return render(request, 'loja/carrinho.html', {
        'carrinho': carrinho,
        'titulo_pagina': 'Meu Carrinho',
    })


@require_POST
def adicionar_ao_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id, disponivel=True)
    carrinho = Carrinho(request)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    try:
        if is_ajax:
            dados = json.loads(request.body)
            quantidade = int(dados.get('quantidade', 1))
        else:
            quantidade = int(request.POST.get('quantidade', 1))
    except (json.JSONDecodeError, ValueError):
        quantidade = 1

    quantidade = max(1, min(quantidade, 99))
    adicionado = carrinho.adicionar(produto, quantidade=quantidade)

    if is_ajax:
        if adicionado:
            return JsonResponse({
                'sucesso': True,
                'mensagem': f'{produto.nome} adicionado ao carrinho!',
                'total_itens': len(carrinho),
                'total_valor': str(carrinho.get_total()),
            })
        else:
            return JsonResponse({
                'sucesso': False,
                'mensagem': 'Limite de itens no carrinho atingido.',
            }, status=400)

    if adicionado:
        messages.success(request, f'{produto.nome} adicionado ao carrinho!')
    else:
        messages.warning(request, 'Limite de itens no carrinho atingido.')

    proximo = request.POST.get(
        'proximo', request.META.get('HTTP_REFERER', '/cardapio/')
    )
    return redirect(proximo)


@require_POST
def remover_do_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    carrinho = Carrinho(request)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    carrinho.remover(produto)

    if is_ajax:
        return JsonResponse({
            'sucesso': True,
            'total_itens': len(carrinho),
            'total_valor': str(carrinho.get_total()),
            'carrinho_vazio': carrinho.esta_vazio(),
        })

    messages.info(request, f'{produto.nome} removido do carrinho.')
    return redirect('ver_carrinho')


@require_POST
def atualizar_carrinho(request):
    carrinho = Carrinho(request)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    try:
        if is_ajax:
            dados = json.loads(request.body)
        else:
            dados = request.POST.dict()
            dados.pop('csrfmiddlewaretoken', None)
    except json.JSONDecodeError:
        if is_ajax:
            return JsonResponse({'sucesso': False}, status=400)
        return redirect('ver_carrinho')

    for produto_id, quantidade in dados.items():
        try:
            carrinho.atualizar_quantidade(produto_id, int(quantidade))
        except (ValueError, TypeError):
            continue

    if is_ajax:
        return JsonResponse({
            'sucesso': True,
            'total_itens': len(carrinho),
            'total_valor': str(carrinho.get_total()),
            'total_formatado': carrinho.get_total_formatado(),
        })

    messages.success(request, 'Carrinho atualizado!')
    return redirect('ver_carrinho')


@require_POST
def limpar_carrinho(request):
    carrinho = Carrinho(request)
    carrinho.limpar()
    messages.info(request, 'Carrinho esvaziado.')
    return redirect('ver_carrinho')


# =============================================
# CHECKOUT
# =============================================

def checkout(request):
    carrinho = Carrinho(request)
    if carrinho.esta_vazio():
        messages.warning(request, 'Seu carrinho esta vazio.')
        return redirect('lista_produtos')

    dados_usuario = {}
    if request.user.is_authenticated:
        dados_usuario = {
            'nome': request.user.get_full_name() or request.user.username,
        }

    return render(request, 'loja/checkout.html', {
        'carrinho': carrinho,
        'total': carrinho.get_total(),
        'dados_usuario': dados_usuario,
        'titulo_pagina': 'Finalizar Pedido',
    })


@require_POST
def finalizar_pedido(request):
    """
    Não salva nada no banco.
    Sanitiza os campos, gera a mensagem e redireciona para o WhatsApp.
    """
    carrinho = Carrinho(request)
    if carrinho.esta_vazio():
        messages.warning(request, 'Seu carrinho esta vazio!')
        return redirect('lista_produtos')

    nome_cliente     = _sanitizar_texto(request.POST.get('nome_cliente', ''), 100)
    telefone_cliente = _sanitizar_texto(request.POST.get('telefone_cliente', ''), 20)
    tipo_entrega     = request.POST.get('tipo_entrega', 'retirada')
    endereco_entrega = _sanitizar_texto(request.POST.get('endereco_entrega', ''), 300)
    observacoes      = _sanitizar_texto(request.POST.get('observacoes', ''), 500)

    # Valida tipo de entrega contra valores permitidos
    if tipo_entrega not in ('retirada', 'delivery'):
        tipo_entrega = 'retirada'

    if tipo_entrega == 'delivery' and not endereco_entrega:
        messages.error(request, 'Informe o endereco de entrega.')
        return redirect('checkout')

    itens_lista = carrinho.get_itens_lista()
    mensagem = gerar_mensagem_carrinho(
        nome_cliente=nome_cliente,
        itens_lista=itens_lista,
        total=carrinho.get_total(),
        tipo_entrega=tipo_entrega,
        endereco=endereco_entrega,
        observacoes=observacoes,
    )
    link_whatsapp = gerar_link_whatsapp(mensagem)

    carrinho.limpar()
    return redirect(link_whatsapp)


# =============================================
# SEO
# =============================================

def robots_txt(request):
    from django.http import HttpResponse
    linhas = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /login/",
        "Disallow: /registro/",
        "Disallow: /carrinho/",
        "Disallow: /checkout/",
        "Allow: /",
        "Allow: /cardapio/",
        "",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(linhas), content_type="text/plain")