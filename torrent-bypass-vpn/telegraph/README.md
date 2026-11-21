# Публикация гайда в Telegraph

Здесь лежит та же статья, свёрстанная под [Telegraph](https://telegra.ph): только поддерживаемые теги, без таблиц.

**Пошаговая инструкция по развёртыванию: [TELEGRAPH.md](../../TELEGRAPH.md).**

| Файл | Что это |
| --- | --- |
| `article.html` | исходный текст статьи — правьте здесь |
| `build.py` | пересобирает `content.json` и `preview.html` из `article.html` |
| `content.json` | готовое содержимое страницы для Telegraph API |
| `preview.html` | превью страницы, открывается в браузере |
| `images.json` | прямые ссылки на картинки из папки `../img` этого репозитория |
| `publish.py` | публикует и обновляет страницу (Python 3.8+, без дополнительных пакетов) |

## Коротко

```bash
python3 publish.py --author "Название VPN"   # опубликовать
python3 publish.py --list                    # страницы аккаунта и их пути
python3 publish.py --edit <путь>             # обновить страницу
python3 publish.py --login                   # ссылка для правки в браузере
python3 build.py                             # пересобрать после правки article.html
```

На Windows вместо `python3` пишите `py`. Файл `telegraph_token.txt` исключён из git: не публикуйте его, по токену можно редактировать ваши страницы.
