<?php
session_start();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $nome = $_POST['nome'];
    $idade = $_POST['idade'];
    $genero = $_POST['genero'];
    $peso = $_POST['peso'];

    $linha = "$nome;$idade;$genero;$peso\n";
    file_put_contents('usuarios.txt', $linha, FILE_APPEND);

    $_SESSION['nome'] = $nome;
    header('Location: chat.php');
    exit;
}
?>

<link rel="stylesheet" href="style.css">
<div class="logo">
  <img src="marcelinho.jpg">
  <p>Marcelinho Fit</p>
</div>

<div class="container">
  <h2>Cadastro</h2>
  <form method="POST">
    <input type="text" name="nome" placeholder="Seu nome" required>
    <input type="number" name="idade" placeholder="Idade" required>
    <input type="text" name="genero" placeholder="Gênero (ex: Masculino/Feminino/Outro)" required>
    <input type="number" name="peso" placeholder="Peso (kg)" step="0.1" required>
    <button type="submit">Cadastrar</button>
  </form>
</div>


session_start();
$_SESSION['nome'] = $nome;
header('Location: chatbot.php');

