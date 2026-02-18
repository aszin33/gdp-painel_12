let servidorAtual = localStorage.getItem('servidor_atual');

// ==================== STATUS DO BOT ====================

async function verificarStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        const statusCard = document.getElementById('botStatus');
        const statStatus = document.getElementById('statStatus');
        const statServers = document.getElementById('statServers');
        const statRAM = document.getElementById('statRAM');
        
        console.log('Status do bot:', data);
        
        if (data.status === 'online') {
            statusCard.className = 'status-card online';
            statusCard.querySelector('span').textContent = 'Bot Online';
            
            if (statStatus) statStatus.textContent = 'Online';
            if (statServers) statServers.textContent = data.servidores || '0';
            if (statRAM) statRAM.textContent = data.ram || '100MB';
        } else {
            statusCard.className = 'status-card offline';
            statusCard.querySelector('span').textContent = 'Bot Offline';
            
            if (statStatus) statStatus.textContent = 'Offline';
            if (statServers) statServers.textContent = '-';
            if (statRAM) statRAM.textContent = '-';
        }
    } catch (error) {
        console.error('Erro ao verificar status:', error);
        document.getElementById('botStatus').className = 'status-card offline';
        document.getElementById('botStatus').querySelector('span').textContent = 'Erro de conexão';
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
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
    
    try {
        console.log(`Enviando GDP para: /api/gdp/${servidorAtual}/${quantidade}`);
        
        const response = await fetch(`/api/gdp/${servidorAtual}/${quantidade}`);
        const data = await response.json();
        
        console.log('Resposta:', data);
        
        if (data.sucesso) {
            mostrarToast('✅ Comando GDP enviado com sucesso!', 'success');
        } else {
            mostrarToast('❌ Erro: ' + (data.erro || 'desconhecido'), 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarToast('❌ Erro de conexão', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-play"></i> Executar';
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
    
    const btn = document.querySelector('.btn-nuclear');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
    
    try {
        console.log(`Enviando Nuclear para: /api/nuclear/${servidorAtual}`);
        
        const response = await fetch(`/api/nuclear/${servidorAtual}`);
        const data = await response.json();
        
        console.log('Resposta:', data);
        
        if (data.sucesso) {
            mostrarToast('☢️ Comando nuclear enviado!', 'warning');
        } else {
            mostrarToast('❌ Erro: ' + (data.erro || 'desconhecido'), 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarToast('❌ Erro de conexão', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-radiation"></i> EXECUTAR';
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
    console.log('🚀 GDP Control iniciado');
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