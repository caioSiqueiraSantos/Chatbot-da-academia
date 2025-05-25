import json
import os
import sys
from typing import Dict, Union

def log_error(error_msg: str):
    """Log de erros para depuração"""
    print(f"ERRO: {error_msg}", file=sys.stderr)

def formatar_treino(treino: Dict) -> str:
    """Formata o treino para exibição no chat"""
    try:
        formatted = f"➤ Objetivo: {treino.get('nome', 'Treino Personalizado')}\n\n"
        for divisao, exercicios in treino.get('divisao', {}).items():
            formatted += f" {divisao}:\n"
            formatted += "\n".join(f"   ▪ {ex}" for ex in exercicios)
            formatted += "\n\n"
        return formatted.strip()
    except Exception as e:
        log_error(f"Erro ao formatar treino: {str(e)}")
        return "Treino montado :)"

def carregar_treinos(json_path: str) -> Union[Dict, None]:
    """Carrega os treinos do arquivo JSON"""
    try:
        with open(json_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        log_error(f"Falha ao carregar treino.json: {str(e)}")
        return None

def gerar_treino(user_data: Dict, conn) -> Union[Dict, str]:
    """Gera treino personalizado baseado no objetivo do usuário"""
    try:
        # Verificação básica dos dados do usuário
        if not user_data or not user_data.get("nome"):
            return "Dados do usuário incompletos."

        objetivo = user_data.get("objetivo", "").lower()
        if not objetivo:
            return "Objetivo de treino não definido."

        # Caminho para o arquivo JSON
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.normpath(
            os.path.join(script_dir, '..', '..', 'database', 'treino.json')
        )

        # Carregar treinos
        todos_os_treinos = carregar_treinos(json_path)
        if not todos_os_treinos:
            return "Erro ao carregar treinos disponíveis."

        # Encontrar treino correspondente
        treino_escolhido = next(
            (t for t in todos_os_treinos 
             if str(t.get("objetivo", "")).lower() == objetivo),
            None
        )

        if not treino_escolhido:
            objetivos_disponiveis = ", ".join(
                {str(t.get("objetivo", "")) for t in todos_os_treinos}
            )
            return f"Objetivo '{objetivo}' inválido. Opções: {objetivos_disponiveis}"

        # Atualizar banco de dados
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE usuarios SET treino_id = %s WHERE nome = %s",
                (treino_escolhido.get("id"), user_data.get("nome")))
            conn.commit()
            cursor.close()
        except Exception as db_error:
            log_error(f"Erro DB ao salvar treino: {db_error}")

        # Retornar resposta formatada
        return {
            "message": "Treino montado com sucesso!",
            "formatted": formatar_treino(treino_escolhido),
            "treino": {
                "A": treino_escolhido.get('divisao', {}).get('A', []),
                "B": treino_escolhido.get('divisao', {}).get('B', []),
                "C": treino_escolhido.get('divisao', {}).get('C', [])
            }
        }

    except Exception as e:
        log_error(f"Erro inesperado em gerar_treino: {str(e)}")
        return "Desculpe, ocorreu um erro ao gerar seu treino."