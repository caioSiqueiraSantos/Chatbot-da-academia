<?php
session_start();

if (!isset($_SESSION['nome'])) {
    header('Location: index.php');
    exit;
}

$nome = $_SESSION['nome'];
?>

<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Chat Interativo</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Arial', sans-serif;
      background-color: #0e0e10;
      color: #f1f1f1;
      height: 100vh;
      display: flex;
    }

    .user-info {
      width: 200px;
      background-color: #1a1a1d;
      padding: 20px;
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    .user-info img {
      width: 100px;
      height: 100px;
      border-radius: 50%;
      object-fit: cover;
      border: 2px solid #7289da;
      margin-bottom: 10px;
    }

    .user-info h2 {
      font-size: 18px;
      font-weight: 700;
    }

    .chat {
      flex: 1;
      display: flex;
      flex-direction: column;
    }

    .messages {
      flex: 1;
      padding: 20px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .message {
      max-width: 60%;
      padding: 10px 15px;
      border-radius: 10px;
      font-weight: 500;
    }

    .from-chat {
      background-color: #2f3136;
      align-self: flex-start;
      border-radius: 10px 10px 10px 0;
    }

    .from-user {
      background-color: #5865f2;
      align-self: flex-end;
      border-radius: 10px 10px 0 10px;
    }

    .input-area {
      padding: 10px;
      background-color: #1e1e22;
      display: flex;
    }

    .input-area input {
      flex: 1;
      padding: 10px;
      border: none;
      border-radius: 5px;
      background-color: #2f3136;
      color: #f1f1f1;
    }

    .input-area input:focus {
      outline: none;
    }
  </style>
</head>
<body>
  <div class="user-info">
    <img src="marcelinho.jpg"  />
    <h2>Marcelinho Fit</h2>
  </div>

  <div class="chat">
    <div class="messages" id="chat-box">
      <div class="message from-chat">Olá! Como posso te ajudar hoje?</div>
    </div>
    <div class="input-area">
      <input type="text" id="message-input" placeholder="Escreva uma mensagem..." />
    </div>
  </div>

  <script>
    const input = document.getElementById("message-input");
    const chatBox = document.getElementById("chat-box");

    const respostas = [
      "Claro! Posso te ajudar com isso.",
      "Interessante! Me conte mais.",
      "Você pode tentar fazer isso dessa forma...",
      "Legal! Quer ver um exemplo?",
      "Fico feliz em ajudar!",
    ];

    input.addEventListener("keypress", function (e) {
      if (e.key === "Enter" && input.value.trim() !== "") {
        const userMsg = input.value.trim();
        input.value = "";

        const userDiv = document.createElement("div");
        userDiv.className = "message from-user";
        userDiv.textContent = userMsg;
        chatBox.appendChild(userDiv);
        chatBox.scrollTop = chatBox.scrollHeight;

        setTimeout(() => {
          const botDiv = document.createElement("div");
          botDiv.className = "message from-chat";
          botDiv.textContent = respostas[Math.floor(Math.random() * respostas.length)];
          chatBox.appendChild(botDiv);
          chatBox.scrollTop = chatBox.scrollHeight;
        }, 800); 
      }
    });
  </script>
  <?php
  if (isset($_POST['sair'])) {
    session_destroy();
    header('Location: cadastro.php');
    exit;
  }
  ?>
</body>
</html>


</body>
</html>
