---
name: prodazhi
description: "Ведёт B2B-лидогенерацию по реестрам ФНС от портрета клиента до черновиков. Используй для запросов «продажи», «лидогенерация» и запуска шагов конвейера."
---

# AI-отдел продаж в Codex

Работай из корня проекта, где лежат AGENTS.md, scripts/ и config.example.json.
Если config.json отсутствует, выполни `bash install.sh`. Настоящие доступы к почте в чат не выводи.
По запросу пользователя выбери шаг и прочитай соответствующий SKILL.md рядом с этим навыком:

| Шаг | Навык |
|---|---|
| портрет, ICP | [prodazhi-portret](../prodazhi-portret/SKILL.md) |
| список, выборка | [prodazhi-spisok](../prodazhi-spisok/SKILL.md) |
| отсев | [prodazhi-otsev](../prodazhi-otsev/SKILL.md) |
| обогащение | [prodazhi-obogashchenie](../prodazhi-obogashchenie/SKILL.md) |
| сигналы, диагностика | [prodazhi-signaly](../prodazhi-signaly/SKILL.md) |
| письма | [prodazhi-pismo](../prodazhi-pismo/SKILL.md) |
| черновики | [prodazhi-chernoviki](../prodazhi-chernoviki/SKILL.md) |

При запросе всего конвейера соблюдай этот порядок. Уже выполненные шаги проверь по базе, без необходимости не повторяй сетевой сбор.
Если шаг не указан, покажи доступные шаги. При первом запуске начни с портрета: Татарстан и перевозки в примере — только демо.
Команды `$prodazhi портрет`, `$prodazhi список` — сообщения в Codex, не команды терминала.
Стоп-лист: `python3 scripts/stoplist.py --db data/leads.db --add ИНН --reason "просили не писать"`.
Письма автоматически не отправлять. Перед IMAP APPEND подготовь dry-run и проверь разрешение пользователя для конкретного ящика и набора писем.
