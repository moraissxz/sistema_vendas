/**
 * carrinho.js
 * Funções globais do carrinho: AJAX para adicionar produtos,
 * atualização do badge e notificações.
 *
 * A função getCookie está definida UMA VEZ aqui.
 * Não repita ela em nenhum template.
 */

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function atualizarBadge(totalItens) {
    const badge = document.getElementById('badge-carrinho');
    if (badge) {
        badge.textContent = totalItens;
        if (totalItens > 0) {
            badge.classList.remove('d-none');
        } else {
            badge.classList.add('d-none');
        }
    }
}

function mostrarNotificacao(mensagem, tipo) {
    tipo = tipo || 'success';
    const div = document.createElement('div');
    div.className = `alert alert-${tipo} alert-dismissible fade show shadow`;
    div.style.cssText = 'position:fixed; top:90px; right:20px; z-index:9999; min-width:280px; max-width:360px;';
    div.innerHTML = `
        ${mensagem}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(div);
    setTimeout(() => {
        if (div.parentNode) div.remove();
    }, 3000);
}

document.addEventListener('DOMContentLoaded', function () {
    // AJAX para formulários de adicionar ao carrinho
    const formsAdicionar = document.querySelectorAll('.form-adicionar');
    formsAdicionar.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            const url = form.action;
            const quantidadeInput = form.querySelector('input[name="quantidade"]');
            const qtd = quantidadeInput ? parseInt(quantidadeInput.value) : 1;

            // Feedback visual imediato no botão
            const btn = form.querySelector('button[type="submit"]');
            const textoOriginal = btn ? btn.innerHTML : null;
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
            }

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify({ quantidade: qtd })
            })
            .then(function (response) {
                return response.json().then(data => ({ ok: response.ok, data }));
            })
            .then(function ({ ok, data }) {
                if (ok && data.sucesso) {
                    atualizarBadge(data.total_itens);
                    mostrarNotificacao('✅ ' + data.mensagem, 'success');
                } else {
                    mostrarNotificacao(
                        '⚠️ ' + (data.mensagem || 'Não foi possível adicionar.'),
                        'warning'
                    );
                }
            })
            .catch(function () {
                mostrarNotificacao('❌ Erro de conexão. Tente novamente.', 'danger');
            })
            .finally(function () {
                if (btn && textoOriginal) {
                    btn.disabled = false;
                    btn.innerHTML = textoOriginal;
                }
            });
        });
    });
});