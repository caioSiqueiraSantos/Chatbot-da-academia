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
  <title>Chat</title>
  <link rel="stylesheet" href="style.css">
  <style>
    body {
      margin: 0;
      font-family: Arial, sans-serif;
      background-color: #1e1e2f;
      color: #fff;
    }
    .topo {
      display: flex;
      align-items: center;
      padding: 10px 20px;
      background-color: #2a2a3d;
    }
    .topo img {
      width: 60px;
      height: 60px;
      border-radius: 10px;
      margin-right: 10px;
    }
    .titulo {
      font-size: 20px;
      color: #00ffaa;
    }
    .chat-container {
      padding: 20px;
      height: 70vh;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .mensagem {
      padding: 10px 15px;
      border-radius: 12px;
      max-width: 70%;
      line-height: 1.4em;
    }
    .usuario {
      background-color: #00ffaa;
      color: #000;
      align-self: flex-end;
    }
    .bot {
      background-color: #333;
      align-self: flex-start;
    }
    .entrada {
      display: flex;
      padding: 15px 20px;
      background-color: #2a2a3d;
      border-top: 1px solid #444;
    }
    .entrada input {
      flex: 1;
      padding: 10px;
      border: none;
      border-radius: 6px;
      margin-right: 10px;
      background-color: #444;
      color: white;
    }
    .entrada button {
      background-color: #00ffaa;
      color: #000;
      border: none;
      padding: 10px 20px;
      border-radius: 6px;
      cursor: pointer;
    }
  </style>
</head>
<body>

  <div class="topo">
    <img src="marcelinho.jpg" alt="Bot">
    <div class="titulo">Olá, <?= htmlspecialchars($usuario) ?>!</div>
  </div>

  <div class="chat-container" id="chat">
    <div class="mensagem bot">Bem-vindo, <?= htmlspecialchars($usuario) ?>! Como posso ajudar?</div>
  </div>

  <div class="entrada">
    <input type="text" id="mensagemInput" placeholder="Digite sua mensagem..." onkeydown="if(event.key==='Enter') enviarMensagem()">
    <button onclick="enviarMensagem()">Enviar</button>
  </div>

  <script>
    function enviarMensagem() {
      const input = document.getElementById('mensagemInput');
      const texto = input.value.trim();
      if (texto === "") return;

      const chat = document.getElementById('chat');

      const msgUsuario = document.createElement('div');
      msgUsuario.className = 'mensagem usuario';
      msgUsuario.innerText = texto;
      chat.appendChild(msgUsuario);

      input.value = "";

      const resposta = gerarResposta(texto);

      setTimeout(() => {
        const msgBot = document.createElement('div');
        msgBot.className = 'mensagem bot';
        msgBot.innerText = resposta;
        chat.appendChild(msgBot);
        chat.scrollTop = chat.scrollHeight;
      }, 500);
    }

    function gerarResposta(pergunta) {
      const p = pergunta.toLowerCase();

      if (p.includes("treino")) return "Você pode começar com 3 séries de agachamento, 2 de flexão e caminhada.";
      if (p.includes("caloria") || p.includes("calorias")) return "A média diária é de 2000 a 2500 kcal, mas depende do seu perfil.";
      if (p.includes("peso")) return "Para perder peso, foque em alimentação balanceada e exercícios aeróbicos.";
      if (p.includes("hora") || p.includes("melhor horário")) return "O melhor horário para treinar é quando você consegue manter uma rotina.";
      
      return "Desculpe, ainda estou aprendendo a responder isso!";
    }
  </script>

</body>
</html>
