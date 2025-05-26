import json
import os
import traceback
import mysql.connector
from typing import Dict, Union 

def gerar_treino(user_data: Dict, conn) -> Union[str, Dict]:
    try:
        nome = user_data.get("nome")
        genero = user_data.get("genero", "").lower()
        objetivo = user_data.get("objetivo_temp", "").lower()

        idade_str = user_data.get("idade")
        peso_str = user_data.get("peso")
        altura_str = user_data.get("altura")

        if not all([nome, genero, objetivo, idade_str, peso_str, altura_str]):
            missing_fields = [
                f for f in ["nome", "genero", "objetivo", "idade", "peso", "altura"]
                if not user_data.get(f if f != "objetivo" else "objetivo_temp")
            ]
            return f"Erro: Faltam dados essenciais do usuário para montar o treino. Campos ausentes: {', '.join(missing_fields)}."

        try:
            idade = int(idade_str)
            peso = float(peso_str)
            altura = float(altura_str)
            if altura == 0: 
                return "Erro: Altura inválida (não pode ser zero)."
        except ValueError:
            return "Erro: Idade, peso ou altura contêm valores inválidos."

        imc = peso / (altura ** 2)

        caminho = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'treino.json'))
        with open(caminho, 'r', encoding='utf-8') as f:
            treinos = json.load(f)

        treino_encontrado = next(
            (t for t in treinos
             if t.get('genero', '').lower() == genero
             and t.get('objetivo', '').lower() == objetivo
             and t.get('idade_min', 0) <= idade <= t.get('idade_max', 999) 
             and t.get('imc_min', 0) <= imc <= t.get('imc_max', 999)),    
            None
        )

        if not treino_encontrado:
            return "Nenhum treino compatível foi encontrado com base em seu perfil atual (gênero, objetivo, idade, IMC)."

        return {
            "treino_selecionado_id": treino_encontrado.get('id'),
            "nome_treino": treino_encontrado.get('nome'),
            "divisao": treino_encontrado.get('divisao') 
        }

    except FileNotFoundError:
        print(f"ERRO em gerar_treino: Arquivo não encontrado em '{caminho}'")
        return "Erro crítico: Não foi possível encontrar o arquivo de configuração dos treinos."
    except KeyError as ke: 
        print(f"ERRO em gerar_treino: Chave não encontrada no JSON - {ke}")
        return f"Erro: Formato inválido no arquivo de treinos (chave ausente: {ke})."
    except Exception as e:
        print(f"Erro ao gerar treino: {e}")
        traceback.print_exc()
        return "Ocorreu um erro ao montar seu treino. Tente novamente."
