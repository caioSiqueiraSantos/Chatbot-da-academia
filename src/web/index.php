<?php
session_start();
require_once 'config.php';

$mensagem = '';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (isset($_POST['cadastro'])) {
        $nome = $_POST['nome'];
        $email = $_POST['email'];
        $senha = $_POST['senha'];
        $peso = $_POST['peso'];
        $idade = $_POST['idade'];
        $genero = $_POST['genero'];
        $altura = $_POST['altura'];

        foreach ($usuarios as $usuario) {
            if ($usuario['email'] == $email) {
                $mensagem = "Esse email já foi registrado!";
                break;
            }
        }

        if (empty($mensagem)) {
            $usuarios[] = [
                'nome' => $nome,
                'email' => $email,
                'senha' => $senha,
                'peso' => $peso,
                'idade' => $idade,
                'genero' => $genero,
                'altura' => $altura
            ];
            file_put_contents('config.php', '<?php $usuarios = ' . var_export($usuarios, true) . ';');

            $_SESSION['usuario'] = $nome;
            header('Location: chatbot.php');
            exit;
        }
    }

    if (isset($_POST['login'])) {
        $email = $_POST['email'];
        $senha = $_POST['senha'];
        foreach ($usuarios as $usuario) {
            if ($usuario['email'] == $email && $usuario['senha'] == $senha) {
                $_SESSION['usuario'] = $usuario['nome'];
                header('Location: chatbot.php');
                exit;
            }
        }
        $mensagem = "Login inválido!";
    }
}
?>

<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Cadastro/Login</title>
    <link rel="stylesheet" href="style.css">
</head>
<body class="login-body">
    <div class="logo-container">
        <img src="marcelinho.jpg" alt="Logo">
        <p class="logo-legenda">MARCELINHO FIT</p>
    </div>

    <div class="form-container">
        <?php if ($mensagem) echo "<p class='mensagem'>$mensagem</p>"; ?>

        <form method="post">
            <h2>Cadastro</h2>
            <input type="text" name="nome" placeholder="Nome" required>
            <input type="email" name="email" placeholder="Email" required>
            <input type="password" name="senha" placeholder="Senha" required>
            <input type="number" name="peso" placeholder="Peso (kg)" required>
            <input type="number" name="idade" placeholder="Idade" required>
            <input type="text" name="genero" placeholder="Gênero" required>
            <input type="number" name="altura" placeholder="Altura (cm)" required>
            <button type="submit" name="cadastro">Cadastrar</button>
        </form>

        <form method="post">
            <h2>Login</h2>
            <input type="email" name="email" placeholder="Email" required>
            <input type="password" name="senha" placeholder="Senha" required>
            <button type="submit" name="login">Entrar</button>
        </form>
    </div>
</body>
</html>
