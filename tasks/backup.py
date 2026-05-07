from netmiko import ConnectHandler
from config.settings import BASTION, TARGET, PASSPHRASE, TARGET_PASSWORD
from datetime import datetime
import time
import os
import re


# =========================
# PEGA HOSTNAME (Huawei / Nokia / Juniper)
# =========================
def get_hostname(output):
    # Huawei
    match = re.search(r"<(.*?)>", output)
    if match:
        return match.group(1)

    # Nokia
    match = re.search(r"@([A-Za-z0-9\-_]+)#", output)
    if match:
        return match.group(1)

    # Juniper
    match = re.search(r"@([A-Za-z0-9\-_]+)>", output)
    if match:
        return match.group(1)

    return "UNKNOWN"


# =========================
# DETECTA VENDOR
# =========================
def detect_vendor(output):
    output = output.lower()

    if "huawei" in output or "vrp" in output:
        return "huawei"

    if "timos" in output or "nokia" in output:
        return "nokia"

    if "junos" in output or "juniper" in output:
        return "juniper"

    return "unknown"


# =========================
# LE OUTPUT COMPLETO (SEM CORTAR)
# =========================
def read_full_output(conn, timeout=120):
    output = ""
    last_data_time = time.time()

    while True:
        time.sleep(1)
        chunk = conn.read_channel()

        if chunk:
            output += chunk
            last_data_time = time.time()

            # paginação (Huawei e outros)
            if "---- more ----" in chunk.lower() or "more" in chunk.lower():
                conn.write_channel(" ")

        if time.time() - last_data_time > 8:
            break

        if time.time() - last_data_time > timeout:
            break

    return output


# =========================
# BACKUP PRINCIPAL
# =========================
def run_backup(target_ip):

    print(f"\n🔌 Conectando no bastion para {target_ip}...")

    bastion = {
        "device_type": "terminal_server",
        "host": BASTION["host"],
        "username": BASTION["username"],
        "use_keys": True,
        "key_file": BASTION["key_file"],
        "passphrase": PASSPHRASE,
        "port": BASTION["port"],
    }

    conn = ConnectHandler(**bastion)

    time.sleep(3)
    conn.read_channel()

    print(f"➡️ Acessando {target_ip}...")

    conn.write_channel(f"ssh {TARGET['username']}@{target_ip}\n")
    time.sleep(2)

    output = conn.read_channel()

    # aceitar host
    if "yes/no" in output.lower():
        conn.write_channel("yes\n")
        time.sleep(2)
        output = conn.read_channel()

    # senha
    for _ in range(10):
        if "password" in output.lower():
            conn.write_channel(TARGET_PASSWORD + "\n")
            break
        time.sleep(1)
        output += conn.read_channel()

    time.sleep(5)
    output = conn.read_channel()

    # =========================
    # GARANTE CLI (IMPORTANTE JUNIPER)
    # =========================
    conn.write_channel("cli\n")
    time.sleep(1)
    conn.read_channel()

    hostname = get_hostname(output)
    print(f"📛 Hostname: {hostname}")

    # =========================
    # DETECTA VENDOR
    # =========================
    print("🔎 Detectando vendor...")

    conn.write_channel("display version\n")
    time.sleep(2)
    out1 = read_full_output(conn)

    conn.write_channel("show version\n")
    time.sleep(2)
    out2 = read_full_output(conn)

    detect_output = out1 + out2

    vendor = detect_vendor(detect_output)

    print(f"🏷️ Vendor: {vendor}")

    if vendor == "unknown":
        print("❌ Vendor não reconhecido. Pulando...")
        conn.disconnect()
        return

    # =========================
    # COMANDOS POR VENDOR
    # =========================
    if vendor == "huawei":
        commands = [
            "screen-length 0 temporary",
            "display version",
            "display current-configuration"
        ]

    elif vendor == "nokia":
        commands = [
            "environment more false",
            "show version",
            "show system information",
            "admin show configuration configure full-context"
        ]

    elif vendor == "juniper":
        commands = [
            "set cli screen-length 0",
            "show version",
            "show configuration | display set"
        ]

    # =========================
    # EXECUTA COMANDOS
    # =========================
    output_total = ""

    for cmd in commands:
        print(f"⚙️ Executando: {cmd}")

        conn.write_channel(cmd + "\n")
        time.sleep(2)

        output = read_full_output(conn)

        output_total += f"\n\n### {cmd} ###\n{output}"

    conn.disconnect()

    # =========================
    # SALVA ARQUIVO
    # =========================
    os.makedirs("backups", exist_ok=True)

    filename = f"backups/{hostname}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(output_total)

    print(f"✅ Backup salvo: {filename}")


# =========================
# EXECUÇÃO MULTI IP
# =========================
if __name__ == "__main__":

    quantidade = int(input("Quantos equipamentos: "))

    ips = []

    for i in range(quantidade):
        ip = input(f"IP {i+1}: ")
        ips.append(ip)

    print("\n🚀 Iniciando coleta automática...")

    for ip in ips:
        try:
            print(f"\n🔧 Processando {ip}...")
            run_backup(ip)
        except Exception as e:
            print(f"❌ Erro em {ip}: {e}")

    print("\n✅ Finalizado!")