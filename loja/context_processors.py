from django.conf import settings
from .carrinho import Carrinho


def carrinho_context(request):
    carrinho = Carrinho(request)
    return {
        'carrinho': carrinho,
        'carrinho_total_itens': len(carrinho),
        'whatsapp_numero': settings.WHATSAPP_NUMERO,
        'nome_sorveteria': settings.NOME_SORVETERIA,
    }