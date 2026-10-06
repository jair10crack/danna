from decimal import Decimal, ROUND_HALF_UP

from django import template

register = template.Library()


@register.filter
def pesos(valor):
    if valor is None:
        valor = 0
    numero = Decimal(str(valor)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    texto = f'{int(numero):,}'.replace(',', '.')
    return f'${texto}'


@register.filter
def cantidad(valor):
    if valor is None:
        return '0'
    numero = Decimal(str(valor))
    texto = f'{numero:.3f}'.rstrip('0').rstrip('.')
    if '.' in texto:
        entero, _, decimales = texto.partition('.')
        return f'{entero},{decimales}'
    return texto
