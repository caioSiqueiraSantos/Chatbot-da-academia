def gerar_treino(user):
    objetivo = "ganhar massa"  # futuramente do banco
    idade = user.get("idade")
    genero = user.get("genero")

    if objetivo == "ganhar massa":
        return "Treino A: Supino 4x10, Rosca direta 4x8\nTreino B: Agachamento 4x12, Remada 4x10"
    elif objetivo == "perder peso":
        return "Treino cardio HIIT + circuito funcional"
    else:
        return "Treino geral para saúde e bem-estar"