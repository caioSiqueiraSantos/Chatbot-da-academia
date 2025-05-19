from flask_cors import CORS
from flask import Flask, request, jsonify
import mysql.connector

from utils.gerar_treino import gerar_treino 
from utils.avaliar_desempenho import avaliar_desempenho 
from utils.calcular_imc import calcular_imc 
from utils.modificar_medidas import iniciar_modificacao, processar_fluxo, estado_usuario

app = Flask(__name__)
CORS(app)

def conectar_banco():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='getfit'
    )

@app.route('/perguntar', methods=['POST'])
def responder():
    dados = request.json
    usuario_nome = dados.get('usuario')
    pergunta_original = dados.get('pergunta')
    resposta_final = ""
    deve_fechar_conexao_nesta_rodada = True 

    if not usuario_nome or not pergunta_original:
        return jsonify({"resposta": "Dados incompletos (usuário ou pergunta faltando)."})

    pergunta_lower = pergunta_original.strip().lower()

    conn = None 
    try:
        conn = conectar_banco()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE nome = %s", (usuario_nome,))
        user_db_data = cursor.fetchone()

        if not user_db_data:
            return jsonify({"resposta": f"Usuário '{usuario_nome}' não encontrado no sistema."})

        # Caso esteja no processo de modificação de medidas
        if usuario_nome in estado_usuario:
            resposta_final = processar_fluxo(usuario_nome, pergunta_original, conn)
            if usuario_nome in estado_usuario:
                deve_fechar_conexao_nesta_rodada = False
            return jsonify({"resposta": resposta_final})

        # Consulta de medidas
        if pergunta_lower == "consultar medidas registradas":
            resposta_final = calcular_imc(user_db_data)
            return jsonify({"resposta": resposta_final})

        # Modificação de medidas
        elif pergunta_lower == "modificar medidas":
            resposta_final = iniciar_modificacao(user_db_data)
            if usuario_nome in estado_usuario:
                deve_fechar_conexao_nesta_rodada = False
            return jsonify({"resposta": resposta_final, "botoes": []})

        # Montar treino
        elif pergunta_lower == "montar treino":
            if not user_db_data.get("peso") or not user_db_data.get("altura") or not user_db_data.get("genero"):
                resposta_final = iniciar_modificacao(user_db_data)
                if usuario_nome in estado_usuario:
                    deve_fechar_conexao_nesta_rodada = False
                return jsonify({"resposta": resposta_final, "botoes": []})

            elif not user_db_data.get("objetivo"):
                return jsonify({
                    "resposta": "Qual o seu objetivo?",
                    "botoes": ["Emagrecimento", "Força", "Hipertrofia", "Resistência"]
                })

            else:
                resposta_final = gerar_treino(user_db_data, conn)
                if isinstance(resposta_final, dict):
                    return jsonify(resposta_final)
                else:
                    return jsonify({"resposta": resposta_final})

        # Quando usuário clicar em um dos objetivos
        elif pergunta_lower in ["emagrecimento", "força", "hipertrofia", "resistência"]:
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET objetivo = %s WHERE nome = %s", (pergunta_lower, usuario_nome))
            conn.commit()
            cursor.close()

            user_db_data["objetivo"] = pergunta_lower
            resposta_final = gerar_treino(conn)
            if isinstance(resposta_final, dict):
                return jsonify(resposta_final)
            else:
                return jsonify({"resposta": resposta_final})

        # Visualizar treino
        elif pergunta_lower == "visualizar treino":
            return jsonify({
                "resposta": "Escolha qual parte do treino deseja visualizar:",
                "botoes": ["Treino A", "Treino B", "Treino C"]
            })

        # Consultar desempenho
        elif pergunta_lower == "consultar desempenho":
            resposta_final = avaliar_desempenho(user_db_data)
            return jsonify({"resposta": resposta_final})

        # Contato com personal trainer
        elif pergunta_lower == "contatar personal trainer":
            return jsonify({"resposta": "Entendido! Seu personal trainer será notificado."})

        # Comando desconhecido
        else:
            return jsonify({"resposta": f"Desculpe, não entendi o comando: '{pergunta_original}'. Pode tentar uma das opções?"})

    except mysql.connector.Error as err:
        print(f"Erro de Banco de Dados: {err}") 
        return jsonify({"resposta": "Desculpe, estamos com problemas técnicos para acessar os dados. Tente mais tarde."}), 500

    except Exception as e:
        print(f"Erro Inesperado na Aplicação: {e}") 
        return jsonify({"resposta": "Ocorreu um erro inesperado no servidor. Tente novamente."}), 500

    finally:
        if conn and conn.is_connected() and deve_fechar_conexao_nesta_rodada:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
