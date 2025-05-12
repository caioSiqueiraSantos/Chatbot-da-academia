# app.py
from flask_cors import CORS
from flask import Flask, request, jsonify
import mysql.connector
from utils.gerar_treino import gerar_treino # Certifique-se que o nome do arquivo e função estão corretos
from utils.avaliar_desempenho import avaliar_desempenho # Idem
from utils.calcular_imc import calcular_imc # Idem
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
    deve_fechar_conexao_nesta_rodada = True # Por padrão, fechamos a conexão

    if not usuario_nome or not pergunta_original:
        return jsonify({"resposta": "Dados incompletos (usuário ou pergunta faltando)."})

    pergunta_lower = pergunta_original.strip().lower()

    conn = None # Inicializa conn
    try:
        conn = conectar_banco()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE nome = %s", (usuario_nome,))
        user_db_data = cursor.fetchone()

        if not user_db_data:
            # conn já estará fechado pelo bloco finally se user_db_data for None
            return jsonify({"resposta": f"Usuário '{usuario_nome}' não encontrado no sistema."})

        # 1. Se o usuário está em um fluxo de estado (ex: modificando medidas)
        if usuario_nome in estado_usuario:
            resposta_final = processar_fluxo(usuario_nome, pergunta_original, conn)
            # Se o fluxo não terminou (usuário ainda está em estado_usuario), não feche a conexão.
            if usuario_nome in estado_usuario:
                deve_fechar_conexao_nesta_rodada = False
        
        # 2. Se não está em fluxo, trata como novo comando
        else:
            if pergunta_lower == "consultar medidas registradas":
                resposta_final = calcular_imc(user_db_data)
            elif pergunta_lower == "montar treino":
                resposta_final = gerar_treino(user_db_data) # Assumindo que gerar_treino usa user_db_data
            elif pergunta_lower == "consultar desempenho":
                resposta_final = avaliar_desempenho(user_db_data) # Assumindo que avaliar_desempenho usa user_db_data
            elif pergunta_lower == "visualizar treino":
                resposta_final = "Seu último treino (exemplo): 3x agachamento, 3x flexão, 15min cardio." # Se buscar do BD, usar conn
            elif pergunta_lower == "modificar medidas":
                resposta_final = iniciar_modificacao(user_db_data)
                # Se iniciar_modificacao colocou o usuário em um estado, não feche a conexão.
                if usuario_nome in estado_usuario:
                    deve_fechar_conexao_nesta_rodada = False
            elif pergunta_lower == "contatar personal trainer":
                resposta_final = "Entendido! Seu personal trainer será notificado."
            else:
                resposta_final = f"Desculpe, não entendi o comando: '{pergunta_original}'. Pode tentar uma das opções?"
        
        return jsonify({"resposta": resposta_final})

    except mysql.connector.Error as err:
        print(f"Erro de Banco de Dados: {err}") # Log do erro no servidor
        return jsonify({"resposta": "Desculpe, estamos com problemas técnicos para acessar os dados. Tente mais tarde."}), 500
    except Exception as e:
        print(f"Erro Inesperado na Aplicação: {e}") # Log do erro no servidor
        return jsonify({"resposta": "Ocorreu um erro inesperado no servidor. Tente novamente."}), 500
    finally:
        if conn and conn.is_connected() and deve_fechar_conexao_nesta_rodada:
            conn.close()
            # print(f"Conexão com BD fechada para {usuario_nome} nesta rodada.") # Para debug
        # elif conn and conn.is_connected() and not deve_fechar_conexao_nesta_rodada:
            # print(f"Conexão com BD MANTIDA ABERTA para {usuario_nome} (fluxo em andamento).") # Para debug

if __name__ == '__main__':
    app.run(debug=True, port=5000)