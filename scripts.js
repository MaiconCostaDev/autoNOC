// === BANCO DE DADOS DE HOSTS ===
let bancoHosts = JSON.parse(localStorage.getItem('bancoHosts')) || {};

function salvarNoLocalStorage() {
  localStorage.setItem('bancoHosts', JSON.stringify(bancoHosts));
}

function cadastrarHost() {
  const host = document.getElementById('hostInput').value.trim().toUpperCase();
  const problema = document.getElementById('problemaInput').value.trim();
  const resolucao = document.getElementById('resolucaoInput').value.trim();
  const time = document.getElementById('timeInput').value.trim();
  const email = document.getElementById('emailInput').value.trim();

  if (host && problema && resolucao && time && email) {
    bancoHosts[host] = { problema, resolucao, time, email };
    salvarNoLocalStorage();
    alert(`✅ Host ${host} cadastrado com sucesso!`);
    document.getElementById('hostInput').value = '';
    document.getElementById('problemaInput').value = '';
    document.getElementById('resolucaoInput').value = '';
    document.getElementById('timeInput').value = '';
    document.getElementById('emailInput').value = '';
  } else {
    alert('⚠️ Por favor, preencha todos os campos.');
  }
}

function consultarHost() {
  const hostConsulta = document.getElementById('consultaHost').value.trim().toUpperCase();
  const resultado = bancoHosts[hostConsulta];

  if (resultado) {
    document.getElementById('resultadoConsulta').innerHTML = ` 
      <p><strong>Host:</strong> ${hostConsulta}</p>
      <p><strong>Problema:</strong> ${resultado.problema}</p>
      <p><strong>Resolução:</strong> ${resultado.resolucao}</p>
      <p><strong>Time responsável:</strong> ${resultado.time}</p>
      <p><strong>Emails de contato:</strong> ${resultado.email}</p>
    `;
  } else {
    document.getElementById('resultadoConsulta').innerHTML = `<p>❌ Host não encontrado.</p>`;
  }
}

function deletarHost() {
  const hostDeletar = document.getElementById('deletarHost').value.trim().toUpperCase();
  if (bancoHosts[hostDeletar]) {
    delete bancoHosts[hostDeletar];
    salvarNoLocalStorage();
    document.getElementById('resultadoDelecao').innerHTML = `<p>✅ Host ${hostDeletar} deletado com sucesso.</p>`;
  } else {
    document.getElementById('resultadoDelecao').innerHTML = `<p>❌ Host não encontrado.</p>`;
  }
}

// === DASHBOARD ===

function mostrarSecao(secao) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.getElementById(secao).classList.add('active');
  if (secao === 'dashboard') carregarDashboard();
}

function carregarDashboard() {
  mostrarNumeroHosts();
  mostrarProblemaMaisFrequente();
  mostrarHostsPorTime();
  mostrarUltimosHosts();
  gerarGraficoProblemas();
}

function mostrarNumeroHosts() {
  document.getElementById('numHosts').innerHTML = `<p><strong>Total de Hosts Cadastrados:</strong> ${Object.keys(bancoHosts).length}</p>`;
}

function mostrarProblemaMaisFrequente() {
  const problemas = {};
  Object.values(bancoHosts).forEach(host => {
    problemas[host.problema] = (problemas[host.problema] || 0) + 1;
  });
  const problemaMaisFrequente = Object.entries(problemas).reduce((a, b) => b[1] > a[1] ? b : a, ["N/A", 0]);
  document.getElementById('problemaMaisFrequente').innerHTML = `<p><strong>Problema Mais Frequente:</strong> ${problemaMaisFrequente[0]} (${problemaMaisFrequente[1]} ocorrências)</p>`;
}

function mostrarHostsPorTime() {
  const times = {};
  Object.values(bancoHosts).forEach(host => {
    times[host.time] = (times[host.time] || 0) + 1;
  });
  const timesHtml = Object.entries(times).map(entry => `<p><strong>${entry[0]}:</strong> ${entry[1]} hosts</p>`).join('');
  document.getElementById('hostsPorTime').innerHTML = timesHtml;
}

function mostrarUltimosHosts() {
  const ultimos = Object.keys(bancoHosts).slice(-5).map(host => `<p>${host}</p>`).join('');
  document.getElementById('ultimoHost').innerHTML = `<strong>Últimos Hosts Cadastrados:</strong>${ultimos}`;
}

function gerarGraficoProblemas() {
  const problemas = {};
  Object.values(bancoHosts).forEach(host => {
    problemas[host.problema] = (problemas[host.problema] || 0) + 1;
  });

  const ctx = document.getElementById('graficoProblema').getContext('2d');
  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: Object.keys(problemas),
      datasets: [{
        label: 'Número de Ocorrências',
        data: Object.values(problemas),
        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4CAF50', '#FF5722'],
        hoverBackgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4CAF50', '#FF5722']
      }]
    }
  });
}

// === LOGIN & CADASTRO ===

let bancoUsuarios = JSON.parse(localStorage.getItem('bancoUsuarios')) || {};

function salvarUsuarios() {
  localStorage.setItem('bancoUsuarios', JSON.stringify(bancoUsuarios));
}

function cadastrarUsuario() {
  const usuario = document.getElementById('cadastroUsername').value.trim();
  const senha = document.getElementById('cadastroPassword').value;
  const mensagem = document.getElementById('cadastroMensagem');

  if (!usuario || !senha) {
    mensagem.textContent = '⚠️ Preencha todos os campos.';
    mensagem.style.color = 'orange';
    return;
  }

  if (!usuario.includes('.') || usuario.length < 3) {
    mensagem.textContent = '❌ O usuário deve estar no formato nome.sobrenome.';
    mensagem.style.color = 'red';
    return;
  }

  if (senha.length < 8) {
    mensagem.textContent = '❌ A senha deve ter no mínimo 8 caracteres.';
    mensagem.style.color = 'red';
    return;
  }

  if (bancoUsuarios[usuario]) {
    mensagem.textContent = '❌ Usuário já existe.';
    mensagem.style.color = 'red';
    return;
  }

  bancoUsuarios[usuario] = senha;
  salvarUsuarios();

  mensagem.textContent = '✅ Usuário cadastrado com sucesso!';
  mensagem.style.color = 'limegreen';

  document.getElementById('cadastroUsername').value = '';
  document.getElementById('cadastroPassword').value = '';

  // Aguarda 2 segundos e volta pro login
  setTimeout(() => {
    document.getElementById('cadastro-section').style.display = 'none';
    document.getElementById('login-section').style.display = 'flex';
    mensagem.textContent = '';
  }, 2000);
}

function login() {
  const username = document.getElementById('loginUsername').value.trim();
  const password = document.getElementById('loginPassword').value;
  const erroLogin = document.getElementById('loginError');

  if (bancoUsuarios[username] === password) {
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('cadastro-section').style.display = 'none';
    document.getElementById('nav-bar').style.display = 'flex';
    erroLogin.style.display = 'none';
  } else {
    erroLogin.style.display = 'block';
  }
}

function mostrarFormularioCadastro() {
  document.getElementById('login-section').style.display = 'none';
  document.getElementById('cadastro-section').style.display = 'flex';
  document.getElementById('loginError').style.display = 'none';
}

function mostrarLogin() {
  document.getElementById('cadastro-section').style.display = 'none';
  document.getElementById('login-section').style.display = 'flex';
  document.getElementById('cadastroMensagem').textContent = '';
  document.getElementById('loginError').style.display = 'none';
}
// Durante o login
localStorage.setItem('maicon.costa', username);

// Ao carregar o site, verificar se o usuário está logado
const usuarioLogado = localStorage.getItem('maicon.costa');
if (usuarioLogado) {
  // Redirecionar para a página de dashboard
}
