<?php
session_start();
require_once 'config.php';

$mensagem = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Cadastro
    if (isset($_POST['cadastrar'])) {
        $nome = $_POST['nome'];
        $email = $_POST['email'];
        $senha = $_POST['senha'];
        $idade = $_POST['idade'];


        $stmt = $conn->prepare("SELECT * FROM usuarios WHERE email = ?");
        $stmt->execute([$email]);

        if ($stmt->rowCount() > 0) {
            $mensagem = "Esse e-mail já foi cadastrado.";
        } else {
            $stmt = $conn->prepare("INSERT INTO usuarios (nome, email, senha, idade, peso, altura, genero) VALUES (?, ?, ?, ?, ?, ?, ?)");
            $stmt->execute([$nome, $email, $senha, $idade, $peso, $altura, $genero]);
            $_SESSION['usuario'] = $nome;
            header("Location: chatbot.php");
            exit;
        }
    }

    // Login
    if (isset($_POST['login'])) {
        $email = $_POST['email'];
        $senha = $_POST['senha'];

        $stmt = $conn->prepare("SELECT * FROM usuarios WHERE email = ? AND senha = ?");
        $stmt->execute([$email, $senha]);
        $user = $stmt->fetch();

        if ($user) {
            $_SESSION['usuario'] = $user['nome'];
            header("Location: chatbot.php");
            exit;
        } else {
            $mensagem = "Email ou senha inválidos.";
        }
    }
}
?>

<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Get Fit - Login</title>
  <link rel="stylesheet" href="/static/style.css">
  <style>
    .toggle-link {
      color: #00ffaa;
      font-size: 14px;
      text-align: center;
      margin-top: 10px;
      cursor: pointer;
      text-decoration: underline;
    }
  </style>
</head>
<body class="login-body">

  <div class="logo-container">
    <img src="/static/img/marcelinho.jpg" alt="Logo">
    <p class="logo-legenda">GET FIT</p>
  </div>

  <?php if ($mensagem): ?>
    <p class="mensagem"><?= $mensagem ?></p>
  <?php endif; ?>

  <div class="form-container" id="login-form">
    <h2>Login</h2>
    <form method="post">
      <input type="email" name="email" placeholder="Email" required>
      <input type="password" name="senha" placeholder="Senha" required>
      <button type="submit" name="login">Entrar</button>
    </form>
    <div class="toggle-link" onclick="mostrarCadastro()">Cadastrar</div>
  </div>

  <div class="form-container" id="cadastro-form" style="display: none;">
    <h2>Cadastro</h2>
    <form method="post">
      <input type="text" name="nome" placeholder="Nome completo" required>
      <input type="email" name="email" placeholder="Email" required>
      <input type="password" name="senha" placeholder="Senha" required>
      <input type="number" name="idade" placeholder="Idade" required>
      <button type="submit" name="cadastrar">Cadastrar</button>
    </form>
    <div class="toggle-link" onclick="mostrarLogin()">Voltar ao login</div>
  </div>

  <script>
    function mostrarCadastro() {
      document.getElementById('login-form').style.display = 'none';
      document.getElementById('cadastro-form').style.display = 'block';
    }
    function mostrarLogin() {
      document.getElementById('login-form').style.display = 'block';
      document.getElementById('cadastro-form').style.display = 'none';
    }
  </script>
</body>
</html>
