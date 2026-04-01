from decimal import Decimal
from django.conf import settings
from .models import Produto

MAX_ITENS = getattr(settings, 'CARRINHO_MAX_ITENS', 30)


class Carrinho:
    def __init__(self, request):
        self.session = request.session
        carrinho = self.session.get('carrinho')
        if not carrinho:
            carrinho = self.session['carrinho'] = {}
        self.carrinho = carrinho

    def salvar(self):
        self.session.modified = True

    def adicionar(self, produto, quantidade=1, sobrescrever_quantidade=False):
        produto_id = str(produto.id)

        # Limite de produtos distintos no carrinho
        if produto_id not in self.carrinho and len(self.carrinho) >= MAX_ITENS:
            return False  # Sinaliza que não foi adicionado

        if produto_id not in self.carrinho:
            self.carrinho[produto_id] = {
                'nome': produto.nome,
                'preco': str(produto.preco),
                'quantidade': 0,
                'subtotal': '0',
                'imagem': produto.imagem.url if produto.imagem else '',
            }

        if sobrescrever_quantidade:
            self.carrinho[produto_id]['quantidade'] = quantidade
        else:
            self.carrinho[produto_id]['quantidade'] += quantidade

        if self.carrinho[produto_id]['quantidade'] <= 0:
            self.remover(produto)
            return True

        # Garante que quantidade não ultrapassa 99
        self.carrinho[produto_id]['quantidade'] = min(
            self.carrinho[produto_id]['quantidade'], 99
        )

        preco = Decimal(self.carrinho[produto_id]['preco'])
        qtd = self.carrinho[produto_id]['quantidade']
        self.carrinho[produto_id]['subtotal'] = str(preco * qtd)
        self.salvar()
        return True

    def remover(self, produto):
        produto_id = str(produto.id) if hasattr(produto, 'id') else str(produto)
        if produto_id in self.carrinho:
            del self.carrinho[produto_id]
            self.salvar()

    def atualizar_quantidade(self, produto_id, quantidade):
        produto_id = str(produto_id)
        if quantidade <= 0:
            if produto_id in self.carrinho:
                del self.carrinho[produto_id]
        elif produto_id in self.carrinho:
            self.carrinho[produto_id]['quantidade'] = min(int(quantidade), 99)
            preco = Decimal(self.carrinho[produto_id]['preco'])
            self.carrinho[produto_id]['subtotal'] = str(
                preco * self.carrinho[produto_id]['quantidade']
            )
        self.salvar()

    def get_total(self):
        return sum(Decimal(item['subtotal']) for item in self.carrinho.values())

    def get_total_formatado(self):
        total = self.get_total()
        return f"R$ {total:.2f}".replace('.', ',')

    def limpar(self):
        self.session['carrinho'] = {}
        self.salvar()

    def esta_vazio(self):
        return len(self) == 0

    def get_itens_lista(self):
        itens = []
        for produto_id, item in self.carrinho.items():
            itens.append({
                'produto_id': produto_id,
                'nome': item['nome'],
                'preco': Decimal(item['preco']),
                'quantidade': item['quantidade'],
                'subtotal': Decimal(item['subtotal']),
            })
        return itens

    def __iter__(self):
        produto_ids = list(self.carrinho.keys())
        produtos = Produto.objects.filter(id__in=produto_ids)
        produtos_dict = {str(p.id): p for p in produtos}

        # Remove itens cujo produto foi deletado do banco
        ids_invalidos = [pid for pid in produto_ids if pid not in produtos_dict]
        for pid in ids_invalidos:
            del self.carrinho[pid]
        if ids_invalidos:
            self.salvar()

        for produto_id, item in self.carrinho.items():
            if produto_id not in produtos_dict:
                continue
            item_copia = item.copy()
            item_copia['produto'] = produtos_dict[produto_id]
            item_copia['preco'] = Decimal(item['preco'])
            item_copia['subtotal'] = Decimal(item['subtotal'])
            yield item_copia

    def __len__(self):
        return sum(item['quantidade'] for item in self.carrinho.values())