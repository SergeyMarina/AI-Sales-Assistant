#!/usr/bin/env bash
# Локальная установка: не меняет домашнюю папку и настройки Codex.
set -euo pipefail
PRODAZHI_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRODAZHI_PYTHON="${PRODAZHI_PYTHON:-python3}"
cd "$PRODAZHI_ROOT"
"$PRODAZHI_PYTHON" - "$PRODAZHI_ROOT" <<'PYTHON'
import ast
import json
import os
from pathlib import Path
import sys
if sys.version_info < (3, 9):
    raise SystemExit("Нужен Python 3.9 или новее")
root = Path(sys.argv[1])
for script in (root / "scripts").glob("*.py"):
    ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
config_path = root / "config.json"
if config_path.exists():
    json.loads(config_path.read_text(encoding="utf-8"))
    print("Существующий config.json сохранён")
else:
    config = json.loads((root / "config.example.json").read_text(encoding="utf-8"))
    for block, fields in (("pisma", ("ot_kogo_imya", "ot_kogo_kompaniya", "ot_kogo_telefon", "podpis")),
                          ("pochta", ("login", "parol", "imap_host", "smtp_host", "ot_kogo"))):
        for field in fields:
            config[block][field] = ""
    config["pochta"]["papka_chernovikov"] = None
    config["istochniki"]["rmsp_dt_category"] = None
    # Создание с закрытыми правами, без перезаписи при повторной установке.
    fd = os.open(config_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(config, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print("Создан config.json: заполните портрет и подпись")
for folder in ("data", "out"):
    (root / folder).mkdir(exist_ok=True)
print("Python и синтаксис скриптов проверены")
PYTHON
"$PRODAZHI_PYTHON" "$PRODAZHI_ROOT/scripts/report.py" --help >/dev/null
printf '\nГотово. Откройте эту папку в Codex и напишите: $prodazhi портрет\n'
