vCREATE DATABASE getfit DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE getfit;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    senha VARCHAR(100),
    idade INT,
    peso FLOAT,
    altura FLOAT,
    genero VARCHAR(20)
    objetivo VARCHAR(20);
);
