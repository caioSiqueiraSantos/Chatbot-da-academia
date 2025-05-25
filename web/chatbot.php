<?php
session_start();
if (!isset($_SESSION['usuario'])) {
  header("Location: index.php");
  exit();
}
$usuario = $_SESSION['usuario'];
?>

<!DOCTYPE html>
<html lang="pt-BR">

<head>
  <meta charset="UTF-8">
  <title>Chat - Get Fit Bot</title>
  <link rel="stylesheet" href="/static/style.css">
  <style>
    body {
      margin: 0;
      background-color: #1e1e2f;
      font-family: Arial, sans-serif;
      color: white;
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }

    .main-container {
      flex: 1;
    }

    .topo {
      display: flex;
      align-items: center;
      background-color: #2a2a3d;
      padding: 10px 20px;
    }

    .topo img {
      width: 60px;
      height: 60px;
      border-radius: 10px;
      margin-right: 15px;
    }

    .titulo {
      font-size: 22px;
      font-weight: bold;
      color: #00ffaa;
    }

    .chat-container {
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      min-height: 70vh;
      overflow-y: auto;
    }

    .mensagem {
      padding: 12px 16px;
      border-radius: 12px;
      max-width: 70%;
      line-height: 1.5em;
      white-space: pre-wrap;
    }

    .bot {
      background-color: #333;
      align-self: flex-start;
    }

    .usuario {
      background-color: #00ffaa;
      color: #000;
      align-self: flex-end;
    }

    .baloes {
      background-color: #2a2a3d;
      border-top: 1px solid #444;
      padding: 15px 20px;
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }

    .baloes button {
      background-color: #444;
      color: white;
      border: none;
      padding: 10px 15px;
      border-radius: 20px;
      cursor: pointer;
      transition: background 0.2s;
    }

    .baloes button:hover {
      background-color: #00ffaa;
      color: #000;
    }

    .entrada-texto {
      display: flex;
      padding: 10px 20px;
      background-color: #2a2a3d;
      border-top: 1px solid #444;
    }

    .entrada-texto input {
      flex-grow: 1;
      padding: 10px;
      border-radius: 8px;
      border: none;
      margin-right: 10px;
      background-color: #fff;
      color: #000;
    }

    .entrada-texto button {
      background-color: #00ffaa;
      color: #000;
      border: none;
      padding: 10px 15px;
      border-radius: 8px;
      cursor: pointer;
    }

    .botoes-sim-nao-container button {
      background-color: #555;
    }

    .botoes-sim-nao-container button:hover {
      background-color: #00bbaa;
    }
  </style>
</head>

<body>

  <div class="topo">
    <img src="/static/img/marcelinho.jpg" alt="Logo">
    <div class="titulo">Olá, <?= htmlspecialchars($usuario) ?>!</div>
  </div>

  <div class="main-container">
    <div class="chat-container" id="chat">
      <div class="mensagem bot">Olá <?= htmlspecialchars($usuario) ?>! Como posso te ajudar hoje?</div>
    </div>
    <div class="entrada-texto" id="entradaTexto" style="display: none;">
      <input type="text" id="inputUsuario" placeholder="Digite sua resposta..." onkeydown="if(event.key==='Enter') enviarTexto()" />
      <button onclick="enviarTexto()">Enviar</button>
    </div>

  </div>

  <div class="baloes">
    <button onclick="responder('Montar treino')">Montar treino</button>
    <button onclick="responder('Visualizar treino')">Visualizar treino</button>
    <button onclick="responder('Consultar desempenho')">Consultar desempenho</button>
    <button onclick="responder('Consultar medidas registradas')">Consultar medidas registradas</button>
    <button onclick="responder('Modificar medidas')">Modificar medidas</button>
    <button onclick="responder('Contatar personal trainer')">Contatar personal trainer</button>
  </div>


  <script>
    const chatContainer = document.getElementById('chat');
    const inputUsuario = document.getElementById('inputUsuario');
    const entradaTextoContainer = document.getElementById('entradaTexto');
    const menuBaloesPrincipais = document.querySelector('.baloes');
    const nomeUsuarioPHP = '<?= htmlspecialchars($usuario, ENT_QUOTES, 'UTF-8') ?>';

    function adicionarMensagemAoChat(texto, tipo) {
      const msgDiv = document.createElement('div');
      msgDiv.className = `mensagem ${tipo}`;
      msgDiv.textContent = texto;
      chatContainer.appendChild(msgDiv);
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function responder(perguntaTexto) {
      adicionarMensagemAoChat(perguntaTexto, 'usuario');

      if (menuBaloesPrincipais) menuBaloesPrincipais.style.display = 'none';
      entradaTextoContainer.style.display = 'none';
      removerBotoesSimNao();

      fetch('http://127.0.0.1:5000/perguntar', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            usuario: nomeUsuarioPHP,
            pergunta: perguntaTexto
          })
        })
        .then(response => {
          if (!response.ok) {
            return response.json().then(errData => {
              throw new Error(errData.resposta || `Erro HTTP: ${response.status}`);
            });
          }
          return response.json();
        })
        .then(data => {
          adicionarMensagemAoChat(data.resposta, 'bot');
          if (Array.isArray(data.botoes) && data.botoes.length > 0) {
            criarBotoesDeOpcao(data.botoes);
          } else {
            analisarRespostaBot(data.resposta);
          }
        })


        .catch(error => {
          console.error("Erro ao enviar/receber mensagem:", error);
          adicionarMensagemAoChat(`Erro: ${error.message || "Não foi possível conectar ao bot."}`, 'bot');
          if (menuBaloesPrincipais) menuBaloesPrincipais.style.display = 'flex';
          entradaTextoContainer.style.display = 'none';
          removerBotoesSimNao();
        });
    }

    function criarBotoesDeOpcao(opcoes) {
      removerBotoesSimNao(); // se houver

      const container = document.createElement('div');
      container.className = 'baloes botoes-opcao';

      opcoes.forEach(opcao => {
        const botao = document.createElement('button');
        botao.textContent = opcao;
        botao.onclick = () => responder(opcao);
        container.appendChild(botao);
      });

      chatContainer.appendChild(container);
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function analisarRespostaBot(respostaBot) {
      const respostaLower = respostaBot.toLowerCase();
      let mostrarEntradaDeTexto = false;
      let mostrarOpcoesSimNao = false;

      const frasesParaSimNao = [
        "deseja adicionar", "deseja atualizar", "deseja alterar",
        "deseja confirmar", "tem certeza", "confirma?", "responda com 'sim' ou 'não'"
      ];

      const frasesParaEntradaDeTexto = [
        "qual seu peso", "qual sua altura", "qual seu gênero",
        "digite seu", "informe o", "seu nome",
        "peso inválido", "altura inválida", "gênero inválido",
        "valor inválido", "formato incorreto", "tente novamente com",
        "por favor, digite", "por favor, insira", "necessário informar"
      ];

      if (frasesParaSimNao.some(frase => respostaLower.includes(frase))) {
        mostrarOpcoesSimNao = true;
      } else if (frasesParaEntradaDeTexto.some(frase => respostaLower.includes(frase))) {
        mostrarEntradaDeTexto = true;
      }

      if (mostrarOpcoesSimNao) {
        criarBotoesSimNao();
        entradaTextoContainer.style.display = 'none';
        if (menuBaloesPrincipais) menuBaloesPrincipais.style.display = 'none';
      } else if (mostrarEntradaDeTexto) {
        removerBotoesSimNao();
        entradaTextoContainer.style.display = 'flex';
        inputUsuario.focus();
        if (menuBaloesPrincipais) menuBaloesPrincipais.style.display = 'none';
      } else {
        removerBotoesSimNao();
        entradaTextoContainer.style.display = 'none';
        if (menuBaloesPrincipais) menuBaloesPrincipais.style.display = 'flex';
      }
    }

    function enviarTexto() {
      const texto = inputUsuario.value.trim();
      if (texto === "") return;

      responder(texto);
      inputUsuario.value = "";
    }

    function removerBotoesSimNao() {
      const botoesExistentes = chatContainer.querySelector('.botoes-sim-nao-container, .botoes-opcao');
      if (botoesExistentes) {
        botoesExistentes.remove();
      }
    }


    function criarBotoesSimNao() {
      removerBotoesSimNao();

      const btnContainer = document.createElement('div');
      btnContainer.className = 'baloes botoes-sim-nao-container';
      btnContainer.style.justifyContent = 'center';
      btnContainer.style.marginTop = '10px';

      const botaoSim = document.createElement('button');
      botaoSim.textContent = "Sim";
      botaoSim.onclick = () => {
        responder("Sim");
      };

      const botaoNao = document.createElement('button');
      botaoNao.textContent = "Não";
      botaoNao.onclick = () => {
        responder("Não");
      };

      btnContainer.appendChild(botaoSim);
      btnContainer.appendChild(botaoNao);
      chatContainer.appendChild(btnContainer);
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    inputUsuario.addEventListener('keydown', function(event) {
      if (event.key === 'Enter') {
        event.preventDefault();
        enviarTexto();
      }
    });

    document.addEventListener('DOMContentLoaded', () => {
      if (menuBaloesPrincipais) menuBaloesPrincipais.style.display = 'flex';
      entradaTextoContainer.style.display = 'none';
    });
  </script>


</body>

</html>