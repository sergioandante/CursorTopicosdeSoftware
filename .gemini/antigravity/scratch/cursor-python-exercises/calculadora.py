def suma(a, b):
    return a + b

def resta(a, b):
    return a - b

def multiplicacion(a, b):
    return a * b

def division(a, b):
    if b == 0:
        return "Error: División por cero no permitida"
    return a / b

def main():
    operaciones = {
        "suma": suma,
        "resta": resta,
        "multiplicacion": multiplicacion,
        "division": division
    }

    print("--- Calculadora Simple ---")
    print("Operaciones disponibles: suma, resta, multiplicacion, division")
    print("Escribe 'salir' para terminar.")

    while True:
        op = input("\nIntroduce la operación: ").lower().strip()
        
        if op == "salir":
            print("¡Adiós!")
            break
        
        if op not in operaciones:
            print("Operación no válida. Inténtalo de nuevo.")
            continue
            
        try:
            num1 = float(input("Introduce el primer número: "))
            num2 = float(input("Introduce el segundo número: "))
            
            resultado = operaciones[op](num1, num2)
            print(f"Resultado: {resultado}")
        except ValueError:
            print("Error: Por favor, introduce números válidos.")

if __name__ == "__main__":
    main()
