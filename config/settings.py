from dotenv import load_dotenv
import os

load_dotenv()

# =========================
# CONFIGURAÇÕES DO BASTION
# =========================
BASTION = {
    "host": "189.124.128.115",
    "port": 5226,
    "username": "folivares.psne",
    "key_file": r"D:\Codex\keys\privatekey_alaresinternet",
}

# 🔐 Senha da chave SSH (passphrase)
PASSPHRASE = os.getenv("BASTION_PASSPHRASE")


# =========================
# CONFIGURAÇÕES DO TARGET
# =========================
TARGET = {
    "username": "folivares.psne",
}

# 🔐 Senha do equipamento (Huawei)
TARGET_PASSWORD = os.getenv("TARGET_PASSWORD")