# muzagregat-site

Статический сайт muzagregat.ru (Hugo). Контент — месячные чарты и квартальные Диски Музагрегата.

## Структура

- `content/chart/YYYY-MM.md` — чарт месяца: frontmatter с позициями + обзор в теле
- `content/disc/YYYY-qN.md` — квартальный Диск
- `content/method/`, `content/about/`, `content/archive/` — статичные страницы
- `layouts/` — шаблоны (движение ▲▼/NEW считается из поля `prev`, виджет плейлиста рендерится только при заполненном `playlist_yandex`)
- `scripts/convert_backfill.py` — разовый конвертер выпусков из папки проекта (уже прогнан, янв–май + Диск Q1)
- `.github/workflows/deploy.yml` — сборка и деплой на GitHub Pages при push в main
- `public/` — локальная сборка для предпросмотра (в git не попадает)

## Добавить новый выпуск

Положить `content/chart/2026-07.md` по образцу соседних (frontmatter: title, period, date, positions с rank/prev/artist/track/flags; тело = обзор месяца) → push в main → через ~2 мин выпуск на сайте. Поле `playlist_yandex` добавить, когда плейлист создан.

## Запуск (разовые шаги, руками)

1. **GitHub:** создать приватный→публичный репозиторий `muzagregat-site`, залить содержимое этой папки (`public/` не нужен), ветка `main`.
2. **Pages:** Settings → Pages → Source: **GitHub Actions**. Первый деплой запустится сам.
3. **Домены:** зарегистрировать **muzagregat.ru** (основной) и **muzagregat.com** у любого РФ-регистратора (Timeweb/reg.ru/nic.ru).
4. **DNS для .ru:** A-записи `@` → 185.199.108.153 / .109. / .110. / .111.153, CNAME `www` → `<логин>.github.io`. В Settings → Pages вписать custom domain `muzagregat.ru`, дождаться сертификата, включить Enforce HTTPS. (Файл `static/CNAME` уже в репо.)
5. **.com:** у регистратора включить редирект muzagregat.com → https://muzagregat.ru (301).
6. **Метрика:** завести счётчик Яндекс Метрики, номер вставить в `layouts/partials/head.html` (закомментированного блока нет — добавить стандартный сниппет перед `</head>`).
7. **Проверка приёмки:** открыть с телефона (РФ-IP, без VPN) `/, /chart/2026-05/, /disc/2026-q1/, /method/` — таблица без горизонтального скролла, движение и пометки на месте.

## Локальная сборка

`hugo server` из корня папки (нужен Hugo ≥0.92 extended).
