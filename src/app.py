from flask_cors import CORS
from flask import Flask, request, jsonify
import mysql.connector
import traceback
import os
import json

from utils.gerar_treino import gerar_treino
from utils.avaliar_desempenho import avaliar_desempenho_checkins, registrar_checkin
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

def _formatar_resposta_treino_com_quebra_linha(dados_treino_gerado, mensagem_contextual_prefix=""):
    if isinstance(dados_treino_gerado, dict) and "formatted" in dados_treino_gerado:
        resposta_formatada = dados_treino_gerado.get("formatted", "")
        resposta_texto = mensagem_contextual_prefix + resposta_formatada
        if "message" in dados_treino_gerado and not mensagem_contextual_prefix:
            resposta_texto = dados_treino_gerado["message"] + "\n\n" + resposta_texto

        return {
            "resposta": resposta_texto,
            "botoes": ["Escolher Novo Objetivo", "Modificar Medidas", "Retornar ao Menu"],
            "treino_data": dados_treino_gerado.get("treino")
        }
    elif isinstance(dados_treino_gerado, str):
        return {"resposta": dados_treino_gerado, "botoes": ["Escolher Novo Objetivo", "Modificar Medidas", "Retornar ao Menu"]}
    else:
        return {"resposta": "Ocorreu um problema ao processar os dados do treino.", "botoes": ["Escolher Novo Objetivo", "Modificar Medidas", "Retornar ao Menu"]}

@app.route('/perguntar', methods=['POST'])
def responder():
    dados = request.json
    usuario_nome = dados.get('usuario')
    pergunta_original = dados.get('pergunta')
    resposta_final = {} 
    deve_fechar_conexao_nesta_rodada = True

    if not usuario_nome or not pergunta_original:
        return jsonify({"resposta": "Dados incompletos (utilizador ou pergunta em falta)."})

    pergunta_lower = pergunta_original.strip().lower()

    conn = None
    db_cursor = None

    try:
        conn = conectar_banco()
        db_cursor = conn.cursor(dictionary=True)
        db_cursor.execute("SELECT * FROM usuarios WHERE nome = %s", (usuario_nome,))
        user_db_data = db_cursor.fetchone()

        if not user_db_data:
            return jsonify({"resposta": f"Utilizador '{usuario_nome}' não encontrado no sistema."})

        if usuario_nome in estado_usuario:
            resposta_processada = processar_fluxo(usuario_nome, pergunta_original, conn)
            if usuario_nome in estado_usuario:
                deve_fechar_conexao_nesta_rodada = False
            
            if isinstance(resposta_processada, dict) and "proximos_botoes" in resposta_processada:
                 return jsonify({"resposta": resposta_processada["mensagem"], "botoes": resposta_processada["proximos_botoes"]})
            else:
                 return jsonify({"resposta": resposta_processada})


        if pergunta_lower == "consultar medidas registadas":
            resposta_texto = calcular_imc(user_db_data)
            resposta_final = {"resposta": resposta_texto, "botoes": ["Retornar ao Menu"]}

        elif pergunta_lower == "modificar medidas":
            resposta_texto = iniciar_modificacao(user_db_data)
            if usuario_nome in estado_usuario:
                deve_fechar_conexao_nesta_rodada = False
            resposta_final = {"resposta": resposta_texto}

        elif pergunta_lower == "montar treino":
            if not user_db_data.get("peso") or not user_db_data.get("altura") or not user_db_data.get("genero") or not user_db_data.get("idade"):
                resposta_texto = iniciar_modificacao(user_db_data)
                if usuario_nome in estado_usuario:
                    deve_fechar_conexao_nesta_rodada = False
                resposta_final = {"resposta": resposta_texto}
            else:
                resposta_final = {
                    "resposta": "As suas medidas estão registadas! Para qual objetivo gostaria de um treino?",
                    "botoes": ["Emagrecimento", "Forca", "Hipertrofia", "Resistencia"]
                }

        elif pergunta_lower == "escolher novo objetivo":
            try:
                update_cursor = conn.cursor()
                update_cursor.execute("UPDATE usuarios SET treino_id = NULL WHERE nome = %s", (usuario_nome,))
                conn.commit()
                update_cursor.close()
                user_db_data["treino_id"] = None
                resposta_final = {
                    "resposta": "O seu treino e objetivo anteriores foram removidos. Qual o seu novo objetivo?",
                    "botoes": ["Emagrecimento", "Forca", "Hipertrofia", "Resistencia"]
                }
            except mysql.connector.Error as db_err:
                traceback.print_exc()
                return jsonify({"resposta": "Tive um problema ao tentar redefinir o seu treino. Tente mais tarde."}), 500

        elif pergunta_lower in ["emagrecimento", "forca", "hipertrofia", "resistencia"]:
            user_db_data["objetivo_temp"] = pergunta_lower
            treino_gerado_info = gerar_treino(user_db_data, conn)

            if isinstance(treino_gerado_info, str) and treino_gerado_info.lower().startswith("erro"):
                resposta_final = {"resposta": treino_gerado_info, "botoes": ["Escolher Novo Objetivo", "Modificar Medidas", "Retornar ao Menu"]}
            elif isinstance(treino_gerado_info, dict) and "treino_selecionado_id" in treino_gerado_info:
                update_cursor = conn.cursor()
                update_cursor.execute("UPDATE usuarios SET treino_id = %s WHERE nome = %s",
                                      (treino_gerado_info["treino_selecionado_id"], usuario_nome))
                conn.commit()
                update_cursor.close()
                user_db_data["treino_id"] = treino_gerado_info["treino_selecionado_id"]
                resposta_final = {
                    "resposta": f"Ótima escolha! O seu treino para {pergunta_lower.capitalize()} com foco em '{treino_gerado_info.get('nome_treino', 'objetivo específico').capitalize()}' foi definido. Deseja visualizar qual parte?",
                    "botoes": ["Treino A", "Treino B", "Treino C", "Ver Treino Completo", "Retornar ao Menu"]
                }
            else:
                 resposta_final = {"resposta": "Não consegui definir o seu treino. Verifique os dados ou tente outro objetivo.", "botoes": ["Escolher Novo Objetivo", "Retornar ao Menu"]}

        elif pergunta_lower == "visualizar treino":
            treino_id = user_db_data.get("treino_id")
            if not treino_id:
                resposta_final = {
                    "resposta": "Você ainda não possui um treino guardado. Deseja 'Montar Treino' agora?",
                    "botoes": ["Montar Treino", "Não, obrigado", "Retornar ao Menu"]
                }
            else:
                resposta_final = {
                    "resposta": "Qual parte do seu treino atual gostaria de visualizar?",
                    "botoes": ["Treino A", "Treino B", "Treino C", "Ver Treino Completo", "Retornar ao Menu"]
                }

        elif pergunta_lower in ["treino a", "treino b", "treino c", "ver treino completo"]:
            treino_id = user_db_data.get("treino_id")
            if not treino_id:
                resposta_final = {
                    "resposta": "Parece que não tem um treino ativo para visualizar. Que tal 'Montar Treino'?",
                    "botoes": ["Montar Treino", "Retornar ao Menu"]
                }
            else:
                json_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database', 'treino.json'))
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        todos_os_treinos = json.load(f)
                    
                    treino_encontrado = next((t for t in todos_os_treinos if t['id'] == treino_id), None)

                    if not treino_encontrado:
                        resposta_final = {"resposta": "Não foi possível encontrar os detalhes do seu treino guardado. Tente 'Montar Treino' novamente.", "botoes": ["Montar Treino", "Retornar ao Menu"]}
                    else:
                        nome_do_treino = treino_encontrado.get('nome', 'O Seu Treino Atual').capitalize()
                        divisoes_treino = treino_encontrado.get('divisao', {})
                        resposta_formatada = ""

                        if pergunta_lower == "ver treino completo":
                            resposta_formatada = f"📋 {nome_do_treino} (Completo):\n\n"
                            for dia, lista_exercicios in divisoes_treino.items():
                                resposta_formatada += f"🔸 Treino {dia}:\n" + "\n".join([f"  • {ex}" for ex in lista_exercicios]) + "\n\n"
                        else:
                            divisao_solicitada = pergunta_original.strip()[-1].upper()
                            exercicios_da_divisao = divisoes_treino.get(divisao_solicitada)
                            if exercicios_da_divisao:
                                resposta_formatada = f"🔸 {nome_do_treino} - Treino {divisao_solicitada}:\n" + "\n".join([f"  • {ex}" for ex in exercicios_da_divisao])
                            else:
                                resposta_formatada = f"Divisão {divisao_solicitada} não encontrada para este treino."
                        
                        resposta_final = {
                            "resposta": resposta_formatada.strip(),
                            "botoes": ["Treino A", "Treino B", "Treino C", "Ver Treino Completo", "Escolher Novo Objetivo", "Retornar ao Menu"]
                        }

                except FileNotFoundError:
                    traceback.print_exc()
                    resposta_final = {"resposta": "Erro: Arquivo de configuração de treinos não encontrado.", "botoes": ["Retornar ao Menu"]}
                except Exception as e:
                    traceback.print_exc()
                    resposta_final = {"resposta": "Erro ao tentar recuperar os detalhes do seu treino. Por favor, tente novamente.", "botoes": ["Retornar ao Menu"]}
        
        elif pergunta_lower == "consultar desempenho":
            mensagem_desempenho = avaliar_desempenho_checkins(usuario_nome)
            resposta_final = {
                "resposta": mensagem_desempenho,
                "botoes": ["Fazer Check-in Hoje", "Retornar ao Menu"]
            }
        
        elif pergunta_lower == "fazer check-in hoje":
            mensagem_registro = registrar_checkin(usuario_nome)
            mensagem_desempenho_atualizada = avaliar_desempenho_checkins(usuario_nome)
            resposta_combinada = f"{mensagem_registro}\n\n{mensagem_desempenho_atualizada}"
            resposta_final = {
                "resposta": resposta_combinada,
                "botoes": ["Fazer Check-in Hoje", "Retornar ao Menu"]
            }

        elif pergunta_lower == "contatar personal trainer":
            resposta_final = {"resposta": "Entendido! O seu personal trainer será notificado.", "botoes": ["Retornar ao Menu"]}
        
        elif pergunta_lower == "retornar ao menu":
            resposta_final = {
                "resposta": "Ok, a retornar ao menu principal. Como posso ajudar?",
                "botoes": ["Montar Treino", "Visualizar Treino", "Consultar Desempenho", "Consultar Medidas Registadas", "Modificar Medidas", "Contatar Personal Trainer"]
            }

        else:
            resposta_final = {"resposta": f"Desculpe, não entendi o comando: '{pergunta_original}'. Pode tentar uma das opções?", "botoes": ["Retornar ao Menu"]}

        return jsonify(resposta_final)

    except mysql.connector.Error as err:
        traceback.print_exc()
        return jsonify({"resposta": "Desculpe, estamos com problemas técnicos para aceder aos dados. Tente mais tarde."}), 500
    except Exception as e:
        traceback.print_exc()
        return jsonify({"resposta": "Ocorreu um erro inesperado no servidor. Tente novamente."}), 500
    finally:
        if db_cursor:
            try:
                db_cursor.close()
            except Exception as e:
                print(f"ERRO ao fechar db_cursor: {e}")
        if conn and conn.is_connected() and deve_fechar_conexao_nesta_rodada:
            try:
                conn.close()
            except Exception as e:
                print(f"ERRO ao fechar conn: {e}")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
