"""Единый поиск локального конфига; справка без почтовых секретов."""
import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def find_config(path=None):
    # Явный путь не заменяется незаметно другим профилем.
    if path is not None:
        return str(Path(path).expanduser().resolve())
    configured = os.environ.get("AIOP_CONFIG")
    if configured:
        return str(Path(configured).expanduser().resolve())
    return str(ROOT / "config.json")


def main():
    parser = argparse.ArgumentParser(description="Портрет клиента без почтовых секретов")
    parser.add_argument("--config")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    try:
        with open(find_config(args.config), encoding="utf-8") as stream:
            config = json.load(stream)
    except (OSError, ValueError) as exc:
        parser.exit(1, "Не удалось прочитать конфиг: %s\n" % exc)
    fields = ("portret_klienta", "vilki", "otsev", "istochniki", "puti")
    print(json.dumps({key: config.get(key, {}) for key in fields}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
