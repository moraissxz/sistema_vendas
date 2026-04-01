from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def moeda_br(valor):
    try:
        valor = Decimal(str(valor))
        return f"R$ {valor:.2f}".replace('.', ',')
    except (ValueError, TypeError):
        return "R$ 0,00"


@register.filter
def multiplica(valor, fator):
    try:
        return Decimal(str(valor)) * Decimal(str(fator))
    except (ValueError, TypeError):
        return 0