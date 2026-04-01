import urllib.parse
from decimal import Decimal
from django.conf import settings


def gerar_mensagem_carrinho(nome_cliente, itens_lista, total,
                             tipo_entrega='retirada', endereco='', observacoes=''):
    nome_sorveteria = settings.NOME_SORVETERIA
    linhas = []

    linhas.append(f"*{nome_sorveteria}*")
    linhas.append(f"*Novo Pedido*")
    linhas.append("=" * 30)

    if nome_cliente:
        linhas.append(f"*Cliente:* {nome_cliente}")

    tipos = {'retirada': 'Retirada no local', 'delivery': 'Delivery'}
    linhas.append(f"*Entrega:* {tipos.get(tipo_entrega, tipo_entrega)}")

    if tipo_entrega == 'delivery' and endereco:
        linhas.append(f"*Endereco:* {endereco}")

    linhas.append("=" * 30)
    linhas.append("*Itens do Pedido:*")
    linhas.append("")

    for item in itens_lista:
        preco = Decimal(str(item['preco']))
        quantidade = item['quantidade']
        subtotal = Decimal(str(item['subtotal']))
        preco_fmt = f"R$ {preco:.2f}".replace('.', ',')
        subtotal_fmt = f"R$ {subtotal:.2f}".replace('.', ',')
        linhas.append(f"• {quantidade}x *{item['nome']}*")
        linhas.append(f"  Preco unit.: {preco_fmt}")
        linhas.append(f"  Subtotal: {subtotal_fmt}")
        linhas.append("")

    linhas.append("=" * 30)
    total_fmt = f"R$ {Decimal(str(total)):.2f}".replace('.', ',')
    linhas.append(f"*TOTAL: {total_fmt}*")

    if observacoes:
        linhas.append("=" * 30)
        linhas.append(f"*Observacoes:* {observacoes}")

    linhas.append("=" * 30)
    linhas.append("Pedido enviado pelo site!")

    return "\n".join(linhas)


def gerar_link_whatsapp(mensagem, numero=None):
    if numero is None:
        numero = settings.WHATSAPP_NUMERO
    numero_limpo = ''.join(filter(str.isdigit, str(numero)))
    mensagem_codificada = urllib.parse.quote(mensagem)
    return f"https://wa.me/{numero_limpo}?text={mensagem_codificada}"