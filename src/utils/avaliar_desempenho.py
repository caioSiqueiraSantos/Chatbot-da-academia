from datetime import date

user_checkins = {}

def avaliar_desempenho_checkins(usuario_nome):
    if usuario_nome in user_checkins:
        checkins_do_usuario = user_checkins[usuario_nome]
        num_checkins = len(checkins_do_usuario)
        
        if num_checkins == 0:
            return "Você ainda não fez nenhum check-in. Que tal começar hoje?"
        elif num_checkins == 1:
            return f"Você fez 1 check-in até agora. Continue assim, {usuario_nome}!"
        else:
            return f"Você já fez {num_checkins} check-ins! Ótimo trabalho, {usuario_nome}!"
    else:
        return "Você ainda não fez nenhum check-in. Que tal começar hoje?"

def registrar_checkin(usuario_nome):
    hoje_str = date.today().isoformat() 

    if usuario_nome not in user_checkins:
        user_checkins[usuario_nome] = []

    if hoje_str not in user_checkins[usuario_nome]:
        user_checkins[usuario_nome].append(hoje_str)
        return f"Check-in de hoje ({hoje_str}) registado com sucesso, {usuario_nome}!"
    else:
        return f"Você já fez check-in hoje ({hoje_str}), {usuario_nome}! Volte amanhã para um novo check-in."
