from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_inicial, name='pagina_inicial'),
    path('cardapio/', views.lista_produtos, name='lista_produtos'),
    path('cardapio/produto/<int:produto_id>/', views.detalhe_produto, name='detalhe_produto'),

    path('registro/', views.pagina_registro, name='registro'),
    path('login/', views.pagina_login, name='login'),
    path('logout/', views.pagina_logout, name='logout'),

    path('carrinho/', views.ver_carrinho, name='ver_carrinho'),
    path('carrinho/adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('carrinho/remover/<int:produto_id>/', views.remover_do_carrinho, name='remover_do_carrinho'),
    path('carrinho/atualizar/', views.atualizar_carrinho, name='atualizar_carrinho'),
    path('carrinho/limpar/', views.limpar_carrinho, name='limpar_carrinho'),

    path('checkout/', views.checkout, name='checkout'),
    path('checkout/finalizar/', views.finalizar_pedido, name='finalizar_pedido'),

    # SEO
    path('robots.txt', views.robots_txt, name='robots_txt'),
]