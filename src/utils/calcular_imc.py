def calcular_imc(user):
    peso = user.get("peso")
    altura_m = user.get("altura")

    if peso is not None and altura_m is not None: 
        if altura_m <= 0: 
            return "Altura deve ser um valor positivo."
            
        imc = round(peso / (altura_m ** 2), 2)
        
        return f"Peso: {peso}kg, Altura: {altura_m}m, IMC: {imc}"
        
    return "Você ainda não cadastrou suas medidas (peso e altura são necessários)."