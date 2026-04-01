from django.db import models
from django.core.files.base import ContentFile
from io import BytesIO


class Categoria(models.Model):
    nome = models.CharField(max_length=100, verbose_name='Nome')
    descricao = models.TextField(blank=True, null=True, verbose_name='Descricao')
    icone = models.CharField(
        max_length=10,
        blank=True,
        default='',
        verbose_name='Icone',
        help_text='Opcional — use um emoji, ex: 🍦'
    )
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    ordem = models.PositiveIntegerField(default=0, verbose_name='Ordem')

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome


class Produto(models.Model):
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='produtos',
        verbose_name='Categoria'
    )
    nome = models.CharField(max_length=200, verbose_name='Nome')
    descricao = models.TextField(verbose_name='Descricao')
    preco = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Preco'
    )
    imagem = models.ImageField(
        upload_to='produtos/',
        blank=True,
        null=True,
        verbose_name='Imagem'
    )
    disponivel = models.BooleanField(default=True, verbose_name='Disponivel')
    destaque = models.BooleanField(default=False, verbose_name='Destaque')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    # Dimensão máxima que a imagem será redimensionada ao salvar
    IMAGEM_MAX_PX = 800

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} - R$ {self.preco:.2f}"

    @property
    def preco_formatado(self):
        return f"R$ {self.preco:.2f}".replace('.', ',')

    def save(self, *args, **kwargs):
        """Redimensiona a imagem para no máximo IMAGEM_MAX_PX px antes de salvar."""
        super().save(*args, **kwargs)
        if self.imagem:
            self._redimensionar_imagem()

    def _redimensionar_imagem(self):
        try:
            from PIL import Image
            caminho = self.imagem.path
            img = Image.open(caminho)

            # Só redimensiona se for maior que o limite
            if img.width > self.IMAGEM_MAX_PX or img.height > self.IMAGEM_MAX_PX:
                img.thumbnail(
                    (self.IMAGEM_MAX_PX, self.IMAGEM_MAX_PX),
                    Image.LANCZOS
                )
                # Converte RGBA/P para RGB antes de salvar como JPEG
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                img.save(caminho, format='JPEG', quality=85, optimize=True)
        except Exception:
            # Nunca deixa um erro de imagem quebrar o salvamento do produto
            pass