# =========================
# IMPORT
# =========================
from tasks.backup import run_backup


# =========================
# COLETA DE IPS
# =========================
def coletar_ips():
    while True:
        try:
            quantidade = int(input("Quantos equipamentos: "))
            break
        except:
            print("Digite um número válido!")

    ips = []

    for i in range(quantidade):
        ip = input(f"IP {i+1}: ")
        ips.append(ip)

    return ips


# =========================
# MAIN
# =========================
def main():

    ips = coletar_ips()

    print("\n🚀 Iniciando coleta automática...\n")

    for ip in ips:
        try:
            print(f"\n🔌 Processando {ip}...")
            run_backup(ip)  # 🔥 agora sem commands
        except Exception as e:
            print(f"❌ Erro em {ip}: {e}")

    print("\n✅ Finalizado!")


# =========================
# EXECUÇÃO
# =========================
if __name__ == "__main__":
    main()