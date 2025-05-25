from flask_cors import CORS
from flask import Flask, request, jsonify
import mysql.connector
import traceback # Para log de erros detalhado

# Seus outros imports
from utils.gerar_treino import gerar_treino 
from utils.avaliar_desempenho import avaliar_desempenho 
from utils.calcular_imc import calcular_imc 
from utils.modificar_medidas import iniciar_modificacao, processar_fluxo, estado_usuario

app = Flask(__name__)
CORS(app)

def conectar_banco():
    """Estabelece conexão com o banco de dados MySQL."""
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  # Sua senha do MySQL, se houver
        database='getfit'
    )

def _formatar_resposta_treino(dados_treino_gerado, mensagem_contextual_prefix=""):
    """
    Auxiliar para formatar a resposta JSON quando um treino é gerado/exibido.
    Inclui o treino formatado, botões e os dados brutos do treino (A, B, C).
    """
    if isinstance(dados_treino_gerado, dict) and "formatted" in dados_treino_gerado:
        resposta_texto = mensagem_contextual_prefix + dados_treino_gerado.get("formatted", "Erro ao formatar treino.")
        
        if "message" in dados_treino_gerado and mensagem_contextual_prefix == "" and \
           dados_treino_gerado["message"] not in resposta_texto:
             resposta_texto = dados_treino_gerado["message"] + "\n\n" + resposta_texto

        json_resposta = {
            "resposta": resposta_texto,
            "botoes": ["Escolher Novo Objetivo", "Modificar Medidas", "Retornar ao Menu"], 
            "treino_data": dados_treino_gerado.get("treino") 
        }
        return json_resposta
    elif isinstance(dados_treino_gerado, str): 
        return {"resposta": dados_treino_gerado, "botoes": ["Escolher Novo Objetivo", "Modificar Medidas", "Retornar ao Menu"]}
    else: 
        return {"resposta": "Ocorreu um problema ao processar os dados do treino.", "botoes": ["Escolher Novo Objetivo", "Modificar Medidas", "Retornar ao Menu"]}

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
    db_cursor = None 

    try:
        conn = conectar_banco()
        db_cursor = conn.cursor(dictionary=True) 
        db_cursor.execute("SELECT * FROM usuarios WHERE nome = %s", (usuario_nome,))
        user_db_data = db_cursor.fetchone()

        if not user_db_data:
            return jsonify({"resposta": f"Usuário '{usuario_nome}' não encontrado no sistema."})

        if usuario_nome in estado_usuario:
            resposta_final = processar_fluxo(usuario_nome, pergunta_original, conn) 
            if usuario_nome in estado_usuario: 
                deve_fechar_conexao_nesta_rodada = False
            return jsonify({"resposta": resposta_final})

        if pergunta_lower == "consultar medidas registradas":
            resposta_final = calcular_imc(user_db_data)
            return jsonify({"resposta": resposta_final})

        elif pergunta_lower == "modificar medidas":
            resposta_final = iniciar_modificacao(user_db_data) 
            if usuario_nome in estado_usuario:
                deve_fechar_conexao_nesta_rodada = False
            return jsonify({"resposta": resposta_final, "botoes": []})

        elif pergunta_lower == "montar treino":
            if not user_db_data.get("peso") or \
               not user_db_data.get("altura") or \
               not user_db_data.get("genero"):
                resposta_mod_medidas = iniciar_modificacao(user_db_data) 
                if usuario_nome in estado_usuario:
                    deve_fechar_conexao_nesta_rodada = False
                return jsonify({"resposta": resposta_mod_medidas, "botoes": []})
            
            elif user_db_data.get("objetivo") and user_db_data.get("objetivo").strip() != "":
                dados_treino = gerar_treino(user_db_data, conn) 
                prefixo_msg = f"Você já possui um treino ativo para o objetivo: **{user_db_data.get('objetivo', 'N/A')}**.\nSegue abaixo:\n\n"
                return jsonify(_formatar_resposta_treino(dados_treino, prefixo_msg))
            else:
                return jsonify({
                    "resposta": "Suas medidas estão registradas! Para qual objetivo você gostaria de um treino?",
                    "botoes": ["Emagrecimento", "Força", "Hipertrofia", "Resistência"]
                })

        elif pergunta_lower == "escolher novo objetivo":
            update_cursor = None
            try:
                update_cursor = conn.cursor() 
                update_cursor.execute("UPDATE usuarios SET objetivo = NULL, treino_id = NULL WHERE nome = %s", (usuario_nome,))
                conn.commit()
                
                if user_db_data:
                    user_db_data["objetivo"] = None
                    user_db_data["treino_id"] = None

                return jsonify({
                    "resposta": "Seu objetivo anterior foi removido. Qual o seu novo objetivo de treino?",
                    "botoes": ["Emagrecimento", "Força", "Hipertrofia", "Resistência"]
                })
            except mysql.connector.Error as db_err:
                print(f"Erro de Banco de Dados ao limpar objetivo para {usuario_nome}: {db_err}")
                traceback.print_exc()
                return jsonify({"resposta": "Tive um problema ao tentar limpar seu objetivo anterior. Por favor, tente novamente mais tarde."}), 500
            finally:
                if update_cursor:
                    update_cursor.close()
        
        elif pergunta_lower in ["emagrecimento", "força", "hipertrofia", "resistência"]:
            update_cursor = None
            try:
                update_cursor = conn.cursor() 
                update_cursor.execute("UPDATE usuarios SET objetivo = %s WHERE nome = %s", (pergunta_lower, usuario_nome))
                conn.commit()
                
                if user_db_data:
                     user_db_data["objetivo"] = pergunta_lower 
                else: 
                    user_db_data = {"nome": usuario_nome, "objetivo": pergunta_lower}

                dados_novo_treino = gerar_treino(user_db_data, conn) 
                prefixo_msg = f"Ótima escolha! Seu novo treino para **{pergunta_lower}** está pronto:\n\n"
                return jsonify(_formatar_resposta_treino(dados_novo_treino, prefixo_msg))
            except mysql.connector.Error as db_err:
                print(f"Erro de Banco de Dados ao definir objetivo '{pergunta_lower}' para {usuario_nome}: {db_err}")
                traceback.print_exc()
                return jsonify({"resposta": f"Tive um problema ao salvar seu objetivo '{pergunta_lower}'. Tente novamente."}), 500
            finally:
                if update_cursor:
                    update_cursor.close()
        
        elif pergunta_lower == "visualizar treino":
            if not user_db_data.get("peso") or \
               not user_db_data.get("altura") or \
               not user_db_data.get("genero"):
                resposta_mod_medidas_vis = iniciar_modificacao(user_db_data) 
                if usuario_nome in estado_usuario:
                    deve_fechar_conexao_nesta_rodada = False
                return jsonify({"resposta": resposta_mod_medidas_vis, "botoes": []})
            elif user_db_data.get("objetivo") and user_db_data.get("objetivo").strip() != "":
                dados_treino_vis = gerar_treino(user_db_data, conn)
                prefixo_msg_vis = f"Exibindo seu treino atual para o objetivo: **{user_db_data.get('objetivo', 'N/A')}**.\n\n"
                return jsonify(_formatar_resposta_treino(dados_treino_vis, prefixo_msg_vis))
            else:
                return jsonify({
                    "resposta": "Você ainda não definiu um objetivo de treino. Gostaria de montar um treino agora?",
                    "botoes": ["Montar Treino", "Modificar Medidas"]
                })

        elif pergunta_lower == "consultar desempenho":
            resposta_final = avaliar_desempenho(user_db_data) 
            return jsonify({"resposta": resposta_final})

        elif pergunta_lower == "contatar personal trainer":
            return jsonify({"resposta": "Entendido! Seu personal trainer será notificado."})

        else:
            return jsonify({"resposta": f"Desculpe, não entendi o comando: '{pergunta_original}'. Pode tentar uma das opções?"})

    except mysql.connector.Error as err:
        print(f"Erro de Banco de Dados: {err}") 
        traceback.print_exc() 
        return jsonify({"resposta": "Desculpe, estamos com problemas técnicos para acessar os dados. Tente mais tarde."}), 500

    except Exception as e:
        print(f"Erro Inesperado na Aplicação: {e}") 
        traceback.print_exc() 
        return jsonify({"resposta": "Ocorreu um erro inesperado no servidor. Tente novamente."}), 500

    finally:
        if db_cursor: 
            db_cursor.close()
        if conn and conn.is_connected() and deve_fechar_conexao_nesta_rodada:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
