estado_usuario = {}

def iniciar_modificacao(user_data):
    usuario_nome = user_data['nome']

    medidas_existem = bool(user_data.get('peso') and user_data.get('altura'))

    if not medidas_existem:
        estado_usuario[usuario_nome] = {'etapa': 'coletar_peso'} 
        return "Vejo que ainda não temos suas medidas. Vamos registrá-las!\nQual seu peso atual? (em kg, ex: 70.5)"
    else:
        estado_usuario[usuario_nome] = {'etapa': 'confirmar_atualizacao'} 
        return "Você já possui medidas registradas. Deseja atualizar?"

def processar_fluxo(usuario_nome, mensagem_usuario, conn):
    """
    Processa a mensagem do usuário com base no estado atual do fluxo de modificação de medidas.
    'conn' é a conexão com o banco de dados, necessária para o UPDATE.
    """
    estado_atual_do_usuario = estado_usuario.get(usuario_nome)

    if not estado_atual_do_usuario:
        return "Ops! Algo deu errado com o processo de modificação de medidas. Tente novamente."

    etapa = estado_atual_do_usuario['etapa']
    mensagem_lower = mensagem_usuario.strip().lower()

    if etapa == 'confirmar_atualizacao':
        if mensagem_lower == "sim":
            estado_atual_do_usuario['etapa'] = 'coletar_peso'
            return "Qual seu peso atual? (em kg, ex: 70.5)"
        elif mensagem_lower == "não":
            estado_usuario.pop(usuario_nome, None) 
            return "Tudo bem, suas medidas não foram alteradas."
        else:
            return "Por favor, responda com 'Sim' ou 'Não'. Deseja atualizar suas medidas?"

    elif etapa == 'coletar_peso':
        try:
            peso = float(mensagem_usuario)
            if not (0 < peso < 500): 
                raise ValueError("Peso fora do intervalo razoável.")
            estado_atual_do_usuario['peso_temp'] = peso
            estado_atual_do_usuario['etapa'] = 'coletar_altura'
            return "Qual sua altura? (em metros, ex: 1.75)"
        except ValueError:
            return "Peso inválido. Por favor, digite um número válido para o peso (ex: 70.5)."

    elif etapa == 'coletar_altura':
        try:
            altura_m = float(mensagem_usuario)
            if not (0.5 < altura_m < 2.5):
                raise ValueError("Altura fora do intervalo razoável.")
            estado_atual_do_usuario['altura_temp_m'] = altura_m
            estado_atual_do_usuario['etapa'] = 'coletar_genero'
            return "Qual seu gênero? (Masculino / Feminino / Outro)"
        except ValueError:
            return "Altura inválida. Por favor, digite um número válido para a altura em metros (ex: 1.75)."

    elif etapa == 'coletar_genero':
        genero = mensagem_usuario.strip()
        if not genero or len(genero) > 50: 
            return "Gênero inválido. Por favor, informe seu gênero."

        peso_coletado = estado_atual_do_usuario.get('peso_temp')
        altura_coletada_m = estado_atual_do_usuario.get('altura_temp_m')

        if peso_coletado is None or altura_coletada_m is None:
            estado_usuario.pop(usuario_nome, None)
            return "Ocorreu um erro, peso ou altura não foram registrados corretamente. Tente novamente."

        try:
            cursor = conn.cursor()
            sql_update = "UPDATE usuarios SET peso = %s, altura = %s, genero = %s WHERE nome = %s"
            cursor.execute(sql_update, (peso_coletado, altura_coletada_m, genero, usuario_nome))
            conn.commit()
            estado_usuario.pop(usuario_nome, None)
            return "Suas medidas foram atualizadas com sucesso!"
        except Exception as e:
            print(f"Erro ao atualizar medidas no banco para {usuario_nome}: {e}") 
            estado_usuario.pop(usuario_nome, None) 
            return "Desculpe, ocorreu un erro ao tentar salvar suas medidas. Tente novamente mais tarde."

    estado_usuario.pop(usuario_nome, None)
    return "Ops! Me perdi no processo. Vamos tentar 'Modificar medidas' desde o início?"