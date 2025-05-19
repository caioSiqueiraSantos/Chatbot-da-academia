# htdocs/src/utils/modificar_medidas.py
import mysql.connector

# Dicionário global para manter o estado da conversa por usuário
estado_usuario = {}

def iniciar_modificacao(user_data):
    """
    Inicia o fluxo de modificação de medidas, verificando se o usuário já tem medidas.
    Define o estado inicial do usuário no dicionário global.
    """
    usuario_nome = user_data['nome']

    # Verifica se peso, altura e genero existem nos dados do usuário
    medidas_completas = bool(user_data.get('peso') is not None and user_data.get('altura') is not None and user_data.get('genero') is not None)

    if not medidas_completas:
        # Se faltam medidas, inicia o fluxo pela coleta de peso
        estado_usuario[usuario_nome] = {'etapa': 'coletar_peso'} 
        return "Vejo que ainda não temos suas medidas completas. Vamos registrá-las!\\nQual seu peso atual? (em kg, ex: 70.5)"
    else:
        # Se já tem medidas, pergunta se deseja atualizar
        estado_usuario[usuario_nome] = {'etapa': 'confirmar_atualizacao'} 
        return "Você já possui medidas registradas. Deseja atualizar?"

def processar_fluxo(usuario_nome, mensagem_usuario, conn):
    """
    Processa a mensagem do usuário com base no estado atual do fluxo de modificação de medidas.
    Atualiza o estado e, se necessário, os dados do usuário no banco de dados.
    'conn' é a conexão com o banco de dados, necessária para o UPDATE.
    """
    estado_atual_do_usuario = estado_usuario.get(usuario_nome)

    # Verifica se o estado existe (deve existir se esta função foi chamada)
    if not estado_atual_do_usuario:
        # Isso indica um erro lógico no app.py ou estado perdido
        return "Ops! Algo deu errado com o processo de modificação de medidas. Tente novamente."

    etapa = estado_atual_do_usuario['etapa']
    mensagem_lower = mensagem_usuario.strip().lower()
    resposta_para_usuario = "" # Inicializa a resposta que será retornada

    # --- Lógica para cada etapa do fluxo ---
    if etapa == 'confirmar_atualizacao':
        if mensagem_lower == "sim":
            # Se confirmar, vai para a coleta de peso
            estado_atual_do_usuario['etapa'] = 'coletar_peso'
            resposta_para_usuario = "Ótimo! Qual seu peso atual? (em kg, ex: 70.5)"
        elif mensagem_lower == "não" or mensagem_lower == "nao":
            # Se não confirmar, limpa o estado
            # Verifica se veio do fluxo de montar treino e notifica que precisa dos dados
            if estado_atual_do_usuario.get('origem_fluxo') == 'montar_treino':
                resposta_para_usuario = "Entendido. No entanto, para montar um treino personalizado, preciso das suas medidas (peso, altura e gênero). Se desejar, inicie o processo 'Modificar Medidas' novamente."
            else:
                resposta_para_usuario = "Ok, suas medidas não foram alteradas."
            del estado_usuario[usuario_nome] # Limpa o estado
        else:
            # Se a resposta não for Sim/Não, repete a pergunta
            resposta_para_usuario = "Por favor, responda 'Sim' ou 'Não'."
            # Não muda a etapa, espera uma resposta válida
            
    elif etapa == 'coletar_peso':
        try:
            # Tenta converter a mensagem para float (aceita vírgula ou ponto)
            peso = float(mensagem_usuario.replace(',', '.'))
            # Validação básica do valor do peso
            if not 10 <= peso <= 300: 
                raise ValueError("Peso fora da faixa esperada.")
            # Armazena o peso temporariamente no estado
            estado_atual_do_usuario['peso_temp'] = peso
            # Avança para a próxima etapa
            estado_atual_do_usuario['etapa'] = 'coletar_altura'
            resposta_para_usuario = "Certo! Qual sua altura atual? (em metros, ex: 1.75)"
        except ValueError:
            # Se a conversão ou validação falhar
            resposta_para_usuario = "Peso inválido. Por favor, digite um número válido para o peso em kg (ex: 70.5)."

    elif etapa == 'coletar_altura':
        try:
            # Tenta converter a mensagem para float (aceita vírgula ou ponto)
            altura_m = float(mensagem_usuario.replace(',', '.'))
            # Validação básica do valor da altura
            if not 0.5 <= altura_m <= 2.5: 
                raise ValueError("Altura fora da faixa esperada.")
            # Armazena a altura temporariamente no estado
            estado_atual_do_usuario['altura_temp_m'] = altura_m
            # Avança para a próxima etapa
            estado_atual_do_usuario['etapa'] = 'coletar_genero'
            resposta_para_usuario = "Ok! Qual seu gênero? (Masculino, Feminino, outro)"
        except ValueError:
            # Se a conversão ou validação falhar
            resposta_para_usuario = "Altura inválida. Por favor, digite um número válido para a altura em metros (ex: 1.75)."

    elif etapa == 'coletar_genero':
        genero = mensagem_usuario.strip()
        # Validação simples do gênero
        if not genero or len(genero) > 50: 
            resposta_para_usuario = "Gênero inválido. Por favor, informe seu gênero (Masculino, Feminino, outro)."
        else:
            # Se o gênero é válido, tenta salvar no banco
            peso_coletado = estado_atual_do_usuario.get('peso_temp')
            altura_coletada_m = estado_atual_do_usuario.get('altura_temp_m')

            # Verifica se os dados temporários foram coletados
            if peso_coletado is None or altura_coletada_m is None:
                # Indica um erro se os dados temporários não estiverem presentes
                estado_usuario.pop(usuario_nome, None) # Limpa o estado
                resposta_para_usuario = "Ocorreu um erro, peso ou altura não foram registrados corretamente. Tente novamente."
            else:
                try:
                    # Atualiza o banco de dados com as novas medidas e gênero
                    cursor = conn.cursor()
                    sql_update = "UPDATE usuarios SET peso = %s, altura = %s, genero = %s WHERE nome = %s"
                    cursor.execute(sql_update, (peso_coletado, altura_coletada_m, genero, usuario_nome))
                    conn.commit() # Confirma a transação
                    cursor.close()

                    # Verifica se o fluxo original era "Montar Treino"
                    if estado_atual_do_usuario.get('origem_fluxo') == 'montar_treino':
                        # Se sim, direciona o usuário para a próxima etapa do fluxo de treino (pedir objetivo)
                        # Remove a origem para não causar loop se o objetivo for inválido na próxima etapa
                        estado_usuario.pop(usuario_nome, None) # Limpa o estado atual de modificação
                        # Retorna a mensagem que inicia a próxima etapa do fluxo de treino
                        # Esta mensagem será interceptada pelo app.py para definir o estado 'aguardando_objetivo_treino'
                        return "Suas medidas foram atualizadas com sucesso! Agora, para montar seu treino, preciso saber qual o seu objetivo. Por favor, digite um dos seguintes: emagrecimento, forca, hipertrofia, resistencia."
                    else:
                        # Se não veio do fluxo de treino, apenas confirma a atualização e limpa o estado
                        estado_usuario.pop(usuario_nome, None) # Limpa o estado
                        resposta_para_usuario = "Suas medidas foram atualizadas com sucesso!"
                except Exception as e:
                    print(f"Erro ao atualizar medidas no banco para {usuario_nome}: {e}") 
                    estado_usuario.pop(usuario_nome, None) # Limpa o estado em caso de erro no BD
                    resposta_para_usuario = "Desculpe, não consegui atualizar suas medidas no momento. Tente novamente."
    
    # Retorna a resposta para o usuário (exceto quando redireciona para o fluxo de treino)
    return resposta_para_usuario

