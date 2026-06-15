# Демо-сценарии использования Methodist Agent

## Сценарий 1: Создание рабочей программы

**Запрос методиста:**
> "Создай рабочую программу по дисциплине 'Bazy dannykh' dlya gruppy PI-301, 144 chasa, napravlenie 09.03.04 Programmnaya inzheneriya"

**Что делает агент:**
1. Загружает skill `docx-creation/curriculum`
2. Загружает шаблон `templates/curriculum/template.docx`
3. Запрашивает недостающие данные (компетенции, содержание)
4. Заполняет шаблон
5. Сохраняет как `RP_Bazy_dannykh_PI-301.docx`

**Команда CLI:**
```cmd
python -m src.main chat
> Sozday rabochuyu programmu po discipline "Bazy dannykh" dlya gruppy PI-301, 144 chasa
```

**Или прямое создание:**
```cmd
python -m src.main create curriculum --subject "Bazy dannykh" --hours 144
```

---

## Сценарий 2: Поиск методических материалов

**Запрос методиста:**
> "Naydi metodichku po differencialnym uravneniyam dlya VT"

**Что делает агент:**
1. Использует Web Search Agent
2. Ищет через DuckDuckGo/SerpAPI
3. Возвращает список ссылок с описаниями
4. Предлагает скачать подходящие файлы

**Команда CLI:**
```cmd
python -m src.main search "metodichka differencialnye uravneniya VT"
```

**Результат:**
```
Rezultaty poiska:
1. Metodicheskie ukazaniya po differencialnym uravneniyam - [URL]
2. Rabochaya programma - Diff. uravneniya - [URL]
3. Kontrolnye zadaniya - [URL]
```

---

## Сценарий 3: Адаптация документа под новый ФГОС

**Запрос методиста:**
> "Adaptiruy etu rabochuyu programmu pod FGOS 3++"

**Что делает агент:**
1. Загружает старый документ
2. Загружает skill `document-adaptation/fgos-update`
3. Проверяет текущие ссылки на ФГОС
4. Обновляет нормативные ссылки
5. Проверяет форматирование по новым требованиям
6. Сохраняет новую версию

**Команда CLI:**
```cmd
python -m src.main adapt "RP_staryy.docx" --template "FGOS3++_shablon.docx"
```

---

## Сценарий 4: Создание ведомости успеваемости

**Запрос методиста:**
> "Sozdai vedomost dlya gruppy PI-301, disciplina 'Bazy dannykh', semestr 5"

**Что делает агент:**
1. Загружает skill `xlsx-creation/grade-sheet`
2. Загружает шаблон `templates/schedule/grade_sheet.xlsx`
3. Заполняет заголовки
4. Создает таблицу с формулами
5. Применяет форматирование
6. Сохраняет как `Vedomost_PI-301_Bazy_dannykh.xlsx`

**Команда CLI:**
```cmd
python -m src.main chat
> Sozdai vedomost dlya gruppy PI-301 po Bazam dannykh, semestr 5
```

---

## Сценарий 5: Чтение и конвертация PDF

**Запрос методиста:**
> "Prochitay etot PDF i perevedi v Word"

**Что делает агент:**
1. PDF Reader Agent извлекает текст
2. Если PDF сканированный — запускает OCR
3. Извлекает таблицы в DataFrame
4. Конвертирует в DOCX
5. Сохраняет результат

**Команда CLI:**
```cmd
python -m src.main pdf extract "document.pdf" --output "document.docx"
```

**Или с OCR:**
```cmd
python -m src.main pdf ocr "scan.pdf" --output "scan.docx"
```

---

## Сценарий 6: Создание презентации

**Запрос методиста:**
> "Sozdai prezentaciyu na temu 'Normalnye formy bazy dannykh' dlya lekcii"

**Что делает агент:**
1. Загружает skill `pptx-creation/lecture`
2. Загружает шаблон `templates/presentation/lecture.pptx`
3. Генерирует структуру слайдов через LLM
4. Заполняет слайды
5. Применяет стили
6. Сохраняет как `Lekciya_Normalnye_formy_BD.pptx`

**Команда CLI:**
```cmd
python -m src.main chat
> Sozdai prezentaciyu na temu "Normalnye formy bazy dannykh"
```

---

## Сценарий 7: System Tray быстрые действия

**Действие:**
Клик по иконке в трее → "Sozdat dokument" → "Rabochaya programma"

**Что происходит:**
1. Открывается диалог tkinter
2. Методист вводит название дисциплины
3. Агент создает документ
4. Показывает уведомление "Dokument sozdan"
5. Открывает папку с результатом

---

## Сценарий 8: Batch обработка

**Запрос методиста:**
> "Obnovi vse rabochie programmy v papke '2023' pod novyy shablon"

**Что делает агент:**
1. Находит все DOCX в указанной папке
2. Для каждого документа:
   - Загружает
   - Применяет новый шаблон
   - Обновляет ссылки
   - Сохраняет в папку `2024/`
3. Генерирует отчет о проделанной работе

**Команда CLI:**
```cmd
python -m src.main chat
> Obnovi vse docx v papke "C:\Docs\2023" pod shablon "C:\Templates\new.docx"
```

---

## Сценарий 9: Генерация отчета по данным

**Запрос методиста:**
> "Sozdai otchyot po uspevaemosti na osnove vedomosti"

**Что делает агент:**
1. Загружает XLSX с ведомостью
2. Анализирует данные (pandas)
3. Вычисляет статистику (средний балл, процент сдавших)
4. Создает графики
5. Генерирует DOCX отчет

**Команда CLI:**
```cmd
python -m src.main chat
> Sozdai analitiku po vedomosti "Vedomost.xlsx"
```

---

## Сценарий 10: Помощь с компетенциями

**Запрос методиста:**
> "Pomogi sformulirovat kompetencii dlya discipline 'Iskusstvennyy intellekt'"

**Что делает агент:**
1. Загружает skill `curriculum-design/competencies`
2. Ищет примеры компетенций в интернете
3. Генерирует формулировки через LLM
4. Проверяет соответствие ФГОС
5. Возвращает список компетенций

**Команда CLI:**
```cmd
python -m src.main chat
> Sformuliruy kompetencii dlya discipline "Iskusstvennyy intellekt"
```

---

*Demo v1.0.0 | Windows-first AI Agent for Education*
