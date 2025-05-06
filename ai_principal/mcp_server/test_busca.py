from supabase_client import buscar_exames_paciente

if __name__ == "__main__":
    nome = input("Digite o nome (ou parte do nome) do paciente para buscar: ")
    exames = buscar_exames_paciente(nome)
    print(f"Exames encontrados para '{nome}':")
    for exame in exames:
        print(exame)
