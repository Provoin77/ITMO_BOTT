Проект запускается одной командой - docker compose up --build, непосредственно из корня проекта (за исключением добавления своих API ключей в .env).

Сервис, основан на использовании бесплатных ключей Google Search, OpenChat 3.5, Render (облако) - в данный момент отключён.

Запросы и ответы происходят в формате:

Запрос от пользователя:
{
  "query": "В каком году Университет ИТМО был включён в число Национальных исследовательских университетов России?\n1. 2007\n2. 2009\n3. 2011\n4. 2015",
  "id": 2
}

Пример ответа (JSON):
{
  "id": 2,
  "answer": 2,
  "reasoning": "Университет ИТМО был включён в число Национальных исследовательских университетов России в 2009 году. Это подтверждается официальными данными Министерства образования и науки РФ.",
  "sources": ["https://www.itmo.ru", "https://минобрнауки.рф"]
}
