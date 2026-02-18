let servidorAtual = localStorage.getItem('servidor_atual');

// ==================== STATUS DO BOT ====================

async function verificarStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        const statusEl = document.getElementById('status');
        
        if (data.status === 'online') {
            statusEl.className = 'status online';
            statusEl.innerHTML = '<span class="dot"></span><span>✅ Bot Online</span>';
        } else {
            statusEl.className = 'status offline';
            statusEl.innerHTML = '<span class="dot"></span><span>❌ Bot Offline</span>';
        }
    } catch (error) {
        console.error('Erro:', error);
    }
}

// ==================== CONFIGURAÇÃO ====================

function salvarServidor() {
    const serverId = document.getElementById('serverId').value.trim();
    
    if (!serverId) {
        mostrarToast('Digite o ID do servidor', 'error');
        return;
    }
    
    if (!/^\d+$/.test(serverId)) {
        mostrarToast('ID inválido! Use apenas números', 'error');
        return;
    }
    
    servidorAtual = serverId;
    localStorage.setItem('servidor_atual', serverId);
    
    document.getElementById('serverInfo').classList.remove('hidden');
    document.getElementById('activeServer').textContent = serverId;
    document.getElementById('modalServer').textContent = serverId;
    
    mostrarToast('Servidor salvo com sucesso!', 'success');
}

// ==================== COMANDO GDP ====================

async function executarGDP() {
    if (!servidorAtual) {
        mostrarToast('Configure um servidor primeiro!', 'error');
        return;
    }
    
    const quantidade = document.getElementById('gdpQuantidade').value || 100;
    const btn = event.currentTarget;
    
    btn.disabled = true;
    btn.textContent = '⏳ Enviando...';
    
    try {
        const response = await fetch(`/api/gdp/${servidorAtual}/${quantidade}`);
        const data = await response.json();
        
        if (data.sucesso) {
            mostrarToast('Comando GDP enviado com sucesso!', 'success');
        } else {
            mostrarToast('Erro: ' + (data.erro || 'desconhecido'), 'error');
        }
    } catch (error) {
        mostrarToast('Erro de conexão', 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = '🚀 Criar';
    }
}

// ==================== COMANDO NUCLEAR ====================

function confirmarNuclear() {
    if (!servidorAtual) {
        mostrarToast('Configure um servidor primeiro!', 'error');
        return;
    }
    
    document.getElementById('modal').style.display = 'flex';
    document.getElementById('confirmInput').value = '';
}

function fecharModal() {
    document.getElementById('modal').style.display = 'none';
}

async function executarNuclear() {
    const confirmacao = document.getElementById('confirmInput').value;
    
    if (confirmacao !== 'CONFIRMAR') {
        mostrarToast('Digite CONFIRMAR corretamente', 'error');
        return;
    }
    
    fecharModal();
    
    const btn = document.querySelector('.btn-danger');
    const textoOriginal = btn.textContent;
    
    btn.disabled = true;
    btn.textContent = '⏳ Enviando...';
    
    try {
        const response = await fetch(`/api/nuclear/${servidorAtual}`);
        const data = await response.json();
        
        if (data.sucesso) {
            mostrarToast('☢️ Comando nuclear enviado!', 'warning');
        } else {
            mostrarToast('Erro: ' + (data.erro || 'desconhecido'), 'error');
        }
    } catch (error) {
        mostrarToast('Erro de conexão', 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = textoOriginal;
    }
}

// ==================== TOAST ====================

function mostrarToast(mensagem, tipo) {
    const toast = document.getElementById('toast');
    toast.textContent = mensagem;
    toast.className = `toast show ${tipo}`;
    
    setTimeout(() => {
        toast.className = 'toast';
    }, 3000);
}

// ==================== INICIALIZAÇÃO ====================

document.addEventListener('DOMContentLoaded', () => {
    verificarStatus();
    setInterval(verificarStatus, 30000);
    
    if (servidorAtual) {
        document.getElementById('serverId').value = servidorAtual;
        document.getElementById('serverInfo').classList.remove('hidden');
        document.getElementById('activeServer').textContent = servidorAtual;
        document.getElementById('modalServer').textContent = servidorAtual;
    }
});

// Fechar modal ao clicar fora
window.onclick = function(event) {
    const modal = document.getElementById('modal');
    if (event.target === modal) {
        fecharModal();
    }
}