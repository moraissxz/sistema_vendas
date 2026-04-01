from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Produto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'icone', 'ativo', 'ordem']
    list_editable = ['ativo', 'ordem']
    search_fields = ['nome']


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = [
        'imagem_preview', 'nome', 'categoria',
        'preco', 'disponivel', 'destaque'
    ]
    list_editable = ['disponivel', 'destaque']
    list_filter = ['categoria', 'disponivel', 'destaque']
    search_fields = ['nome', 'descricao']
    readonly_fields = ['imagem_preview', 'criado_em', 'atualizado_em']

    def imagem_preview(self, obj):
        if obj.imagem:
            return format_html(
                '<img src="{}" width="60" height="60" '
                'style="border-radius:8px; object-fit:cover;" />',
                obj.imagem.url
            )
        return 'Sem imagem'
    imagem_preview.short_description = 'Imagem'


admin.site.site_header = 'Sorveteria Frutidelis - Admin'
admin.site.site_title = 'Frutidelis Admin'
admin.site.index_title = 'Painel de Gerenciamento'