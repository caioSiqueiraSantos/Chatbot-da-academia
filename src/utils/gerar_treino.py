import json
import os
from typing import Dict, Union

def carregar_treinos(caminho_do_arquivo: str) -> list:
    """Carrega os dados de treinos a partir de um arquivo JSON."""
    try:
        with open(caminho_do_arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERRO: O arquivo de treinos não foi encontrado em {caminho_do_arquivo}")
        return []
    except json.JSONDecodeError:
        print(f"ERRO: Falha ao decodificar o JSON do arquivo {caminho_do_arquivo}")
        return []

def formatar_treino(treino: Dict) -> str:
    """Formata os detalhes de um treino para uma string legível."""
    if not treino:
        return "Treino inválido ou não fornecido."

    nome_treino = treino.get('nome', 'Seu Treino Personalizado').upper()
    divisoes = treino.get('divisao', {})

    resposta_formatada = f"✅ Treino Definido: **{nome_treino}**\n\n"
    for dia, exercicios in divisoes.items():
        resposta_formatada += f"🏋️ **TREINO {dia.upper()}**\n"
        for exercicio in exercicios:
            resposta_formatada += f"  - {exercicio}\n"
        resposta_formatada += "\n"

    return resposta_formatada.strip()

# ===================================================================
# SEU CÓDIGO EXISTENTE (COM A CORREÇÃO NO EXCEPT)
# ===================================================================

def gerar_treino(user_data: Dict, conn) -> Union[Dict, str]:
    """Gera treino personalizado baseado nas características do usuário"""
    try:
        if not user_data or not user_data.get("nome"):
            return "Dados do usuário incompletos."

        # Garante que objetivo_temp seja usado se existir
        if "objetivo_temp" in user_data:
            objetivo = user_data.get("objetivo_temp", "").lower()
        else:
            objetivo = user_data.get("objetivo", "").lower()

        genero = user_data.get("genero", "").lower()
        nome = user_data.get("nome")

        peso = float(user_data.get("peso", 0))
        altura = float(user_data.get("altura", 0))
        idade = int(user_data.get("idade", 0))

        if not objetivo or not genero or not peso or not altura or not idade:
            return "Informações incompletas para gerar o treino."

        imc = peso / (altura ** 2)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.normpath(
            os.path.join(script_dir, '..', '..', 'database', 'treino.json')
        )

        treinos = carregar_treinos(json_path) # Agora esta função existe
        if not treinos:
            return "Erro ao carregar treinos disponíveis."

        candidatos = [
            t for t in treinos
            if t.get("objetivo", "").lower() == objetivo
            and t.get("genero", "").lower() == genero
            and t.get("idade_min", 0) <= idade <= t.get("idade_max", 100)
            and t.get("imc_min", 0) <= imc <= t.get("imc_max", 100)
        ]

        if not candidatos:
            return "Nenhum treino encontrado com base nos seus dados."

        treino_escolhido = candidatos[0]

        return {
            "message": "Treino montado com sucesso!",
            "formatted": formatar_treino(treino_escolhido), # Agora esta função existe
            "treino_selecionado_id": treino_escolhido.get("id"),
            "nome_treino": treino_escolhido.get("nome"),
            "treino": {
                "A": treino_escolhido.get('divisao', {}).get('A', []),
                "B": treino_escolhido.get('divisao', {}).get('B', []),
                "C": treino_escolhido.get('divisao', {}).get('C', [])
            }
        }

    except Exception as e:
        # Correção da chamada de erro
        print(f"Erro inesperado em gerar_treino: {str(e)}")
        return "Desculpe, ocorreu um erro ao gerar seu treino."