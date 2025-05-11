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
  <link rel="stylesheet" href="style.css">
  <style>
    body {
      margin: 0;
      background-color: #1e1e2f;
      font-family: Arial, sans-serif;
      color: white;
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
    }

    .mensagem {
      padding: 12px 16px;
      border-radius: 12px;
      max-width: 70%;
      line-height: 1.5em;
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
  </style>
</head>
<body>

  <div class="topo">
    <img src="marcelinho.jpg" alt="Logo">
    <div class="titulo">Olá, <?= htmlspecialchars($usuario) ?>!</div>
  </div>

  <div class="chat-container" id="chat">
    <div class="mensagem bot">Olá <?= htmlspecialchars($usuario) ?>! Como posso te ajudar hoje?</div>
  </div>

  <div class="baloes">
    <button onclick="responder('montar treino')">Montar treino</button>
    <button onclick="responder('visualizar treino')">Visualizar treino</button>
    <button onclick="responder('consultar desempenho')">Consultar desempenho</button>
    <button onclick="responder('consultar medidas registradas')">Consultar medidas registradas</button>
    <button onclick="responder('modificar medidas')">Modificar medidas</button>
    <button onclick="responder('contatar personal trainer')">Contatar personal trainer</button>
  </div>

  <script>
    function responder(pergunta) {
      const chat = document.getElementById('chat');

      const msgUser = document.createElement('div');
      msgUser.className = 'mensagem usuario';
      msgUser.textContent = pergunta;
      chat.appendChild(msgUser);

      let resposta = '';
      switch(pergunta) {
        case 'montar treino':
          resposta = 'Vamos montar um treino com base nos seus objetivos!';
          break;
        case 'visualizar treino':
          resposta = 'Aqui está seu treino atual: 3x agachamento, 3x flexão, 15min cardio.';
          break;
        case 'consultar desempenho':
          resposta = 'Você melhorou 15% em resistência desde o último mês.';
          break;
        case 'consultar medidas registradas':
          resposta = 'Suas medidas atuais: Peso: 72kg, Altura: 1.75m, IMC: 23.5.';
          break;
        case 'modificar medidas':
          resposta = 'Vamos atualizar suas medidas. Por favor, vá até o formulário de atualização.';
          break;
        case 'contatar personal trainer':
          resposta = 'Você será conectado ao personal via WhatsApp em instantes.';
          break;
        default:
          resposta = 'Desculpe, não entendi.';
      }

      setTimeout(() => {
        const msgBot = document.createElement('div');
        msgBot.className = 'mensagem bot';
        msgBot.textContent = resposta;
        chat.appendChild(msgBot);
        chat.scrollTop = chat.scrollHeight;
      }, 500);
    }
  </script>

</body>
</html>
