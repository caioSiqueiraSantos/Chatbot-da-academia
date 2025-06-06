import mysql.connector

estado_usuario = {}

def iniciar_modificacao(user_data):
    usuario_nome = user_data['nome']
    medidas_completas = bool(user_data.get('peso') is not None and 
                             user_data.get('altura') is not None and 
                             user_data.get('genero') is not None)

    if not medidas_completas:
        estado_usuario[usuario_nome] = {'etapa': 'coletar_peso', 'origem_fluxo': user_data.get('origem_fluxo')}
        return "Vejo que ainda não temos suas medidas completas. Vamos registá-las!\nQual seu peso atual? (em kg, ex: 70.5)"
    else:
        estado_usuario[usuario_nome] = {'etapa': 'confirmar_atualizacao', 'origem_fluxo': user_data.get('origem_fluxo')}
        return "Você já possui medidas registadas. Deseja atualizar?"

def processar_fluxo(usuario_nome, mensagem_usuario, conn):
    estado_atual_do_usuario = estado_usuario.get(usuario_nome)

    if not estado_atual_do_usuario:
        return "Ops! Algo deu errado com o processo de modificação de medidas. Tente novamente."

    etapa = estado_atual_do_usuario['etapa']
    mensagem_lower = mensagem_usuario.strip().lower()
    
    if etapa == 'confirmar_atualizacao':
        if mensagem_lower == "sim":
            estado_atual_do_usuario['etapa'] = 'coletar_peso'
            return "Ótimo! Qual seu peso atual? (em kg, ex: 70.5)"
        elif mensagem_lower == "não" or mensagem_lower == "nao":
            resposta_para_usuario = "Ok, suas medidas não foram alteradas."
            if estado_atual_do_usuario.get('origem_fluxo') == 'montar_treino':
                resposta_para_usuario = "Entendido. No entanto, para montar um treino personalizado, preciso das suas medidas (peso, altura e gênero). Se desejar, inicie o processo 'Modificar Medidas' novamente."
            del estado_usuario[usuario_nome]
            return resposta_para_usuario
        else:
            return "Por favor, responda 'Sim' ou 'Não'."
            
    elif etapa == 'coletar_peso':
        try:
            peso = float(mensagem_usuario.replace(',', '.'))
            if not 10 <= peso <= 300: 
                raise ValueError("Peso fora da faixa esperada.")
            estado_atual_do_usuario['peso_temp'] = peso
            estado_atual_do_usuario['etapa'] = 'coletar_altura'
            return "Certo! Qual sua altura atual? (em metros, ex: 1.75)"
        except ValueError:
            return "Peso inválido. Por favor, digite um número válido para o peso em kg (ex: 70.5)."

    elif etapa == 'coletar_altura':
        try:
            altura_m = float(mensagem_usuario.replace(',', '.'))
            if not 0.5 <= altura_m <= 2.5: 
                raise ValueError("Altura fora da faixa esperada.")
            estado_atual_do_usuario['altura_temp_m'] = altura_m
            estado_atual_do_usuario['etapa'] = 'coletar_genero'
            return {
                "mensagem": "Ok! Qual seu gênero?",
                "proximos_botoes": ["Masculino", "Feminino"]
            }
        except ValueError:
            return "Altura inválida. Por favor, digite um número válido para a altura em metros (ex: 1.75)."

    elif etapa == 'coletar_genero':
        genero_selecionado = mensagem_usuario.strip()
        
        if genero_selecionado.lower() not in ["masculino", "feminino"]:
            return {
                "mensagem": "Opção de gênero inválida. Por favor, selecione 'Masculino' ou 'Feminino'.",
                "proximos_botoes": ["Masculino", "Feminino"]
            }
        
        peso_coletado = estado_atual_do_usuario.get('peso_temp')
        altura_coletada_m = estado_atual_do_usuario.get('altura_temp_m')

        if peso_coletado is None or altura_coletada_m is None:
            estado_usuario.pop(usuario_nome, None)
            return "Ocorreu um erro, peso ou altura não foram registados corretamente. Tente novamente."
        
        try:
            cursor = conn.cursor()
            sql_update = "UPDATE usuarios SET peso = %s, altura = %s, genero = %s WHERE nome = %s"
            cursor.execute(sql_update, (peso_coletado, altura_coletada_m, genero_selecionado, usuario_nome))
            conn.commit()
            cursor.close()

            origem_do_fluxo = estado_atual_do_usuario.get('origem_fluxo')
            estado_usuario.pop(usuario_nome, None) 

            if origem_do_fluxo == 'montar_treino':
                return {
                    "mensagem": "Suas medidas foram atualizadas com sucesso! Agora, para montar seu treino, qual o seu objetivo?",
                    "proximos_botoes": ["Emagrecimento", "Forca", "Hipertrofia", "Resistencia"]
                }
            else:
                return "Suas medidas foram atualizadas com sucesso!"
        except Exception as e:
            print(f"Erro ao atualizar medidas no banco para {usuario_nome}: {e}") 
            estado_usuario.pop(usuario_nome, None)
            return "Desculpe, não consegui atualizar suas medidas no momento. Tente novamente."
    
    return "Ops! Etapa desconhecida no fluxo de modificação de medidas."
