# Gameboy – platforma z grami i backend logowania

## Skład zespołu

Projekt na ćwiczenia z Programowania Front-end, realizowany solo.

| Imię i nazwisko | Numer albumu | Login GitHub |
|---|---|---|
| Dominik Sornat | 56116 | Sornat123 |

## Opis

Projekt składa się z dwóch części w jednym repozytorium:
- `gameboy_web` – gry (Snake, Tetris, Labirynt, Kółko i krzyżyk) uruchamiane w przeglądarce przez pygbag (WebAssembly)
- `gameboy_backend` – backend logowania i zapisu wyników (FastAPI + SQLite) oraz strona główna projektu (`index.html`)

## Technologie
- Python 3.9 lub nowszy
- pygame-ce i pygbag – gry i ich uruchamianie w przeglądarce
- FastAPI + Uvicorn – API backendu (dokumentacja pod /docs)
- SQLAlchemy + SQLite – baza danych (plik gameboy.db tworzy się sam przy pierwszym starcie)
- JWT (python-jose) oraz passlib + bcrypt – logowanie i hashowanie haseł
- Pydantic – walidacja danych
- Przeglądarka z obsługą WebAssembly (Chrome, Firefox, Safari)

Wszystkie biblioteki są w pliku `requirements.txt` w głównym katalogu.

## Instalacja (macOS / Linux)

    git clone https://github.com/Sornat123/Gameboy.git
    cd Gameboy
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

Instalacja na Windowsie jest opisana w sekcji „Windows” niżej.

## Uruchomienie (kolejność ma znaczenie)

Potrzebne są dwa terminale, w obu z aktywnym venv (`source venv/bin/activate` w głównym katalogu repozytorium).

**1. Backend (port 8001)**, terminal 1:

    cd gameboy_backend
    uvicorn main:app --port 8001

Pod adresem http://localhost:8001 widać tylko komunikat, że backend działa, a pod http://localhost:8001/docs dokumentację API. To nie jest strona projektu.

**2. Gry (port 8000)**, terminal 2, z głównego katalogu repozytorium:

    pygbag gameboy_web

**3. Strona główna projektu.** Gdy oba serwery działają, otwórz w przeglądarce plik `gameboy_backend/index.html` (dwuklik w Finderze lub Eksploratorze albo, na macOS, komenda `open gameboy_backend/index.html`).

Na tej stronie można się zarejestrować lub zalogować, a potem przejść do tabeli wyników albo kliknąć „Przejdź do Gier”, co otwiera platformę z grami pod adresem http://localhost:8000.

## Windows

Komendy z sekcji wyżej są pisane pod macOS i Linux. Na Windowsie różnią się trzy rzeczy:

| Czynność | Windows |
|---|---|
| Python | `python` zamiast `python3` |
| Aktywacja venv | `venv\Scripts\activate` zamiast `source venv/bin/activate` |
| Otwarcie strony projektu | `start gameboy_backend\index.html` zamiast `open ...` (albo dwuklik w Eksploratorze) |

Instalacja na Windowsie:

    git clone https://github.com/Sornat123/Gameboy.git
    cd Gameboy
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt

Uruchomienie (dwa osobne terminale, w obu z aktywnym venv):

Terminal 1 (backend, port 8001):

    cd gameboy_backend
    uvicorn main:app --port 8001

Terminal 2 (gry, port 8000), z głównego katalogu repozytorium:

    pygbag gameboy_web

Potem otwórz `gameboy_backend\index.html`. Python musi być zainstalowany z zaznaczoną opcją „Add Python to PATH”. Jeśli PowerShell blokuje aktywację venv, użyj zwykłego cmd albo wpisz jednorazowo `Set-ExecutionPolicy -Scope Process RemoteSigned`.

## Role użytkowników
- admin – pełne uprawnienia i funkcje administracyjne
- user – zalogowany gracz, jego wyniki są zapisywane
- guest – gracz bez logowania, wyniki nie są zapisywane

## Konto administratora
1. Zarejestruj zwykłego użytkownika na stronie `index.html`.
2. W pliku `gameboy_backend/make_admin.py` wpisz jego login w zmiennej target_username.
3. Uruchom (z aktywnym venv):

       cd gameboy_backend
       python make_admin.py

## Uwagi
- Katalog `build` generuje pygbag automatycznie, nie ma go w repozytorium.
- Baza `gameboy.db` nie jest w repozytorium, tworzy się automatycznie.
- Pliki `api_client.py` i `login_window.py.py` w backendzie to stary klient desktopowy (wymaga dodatkowo pygame i requests), nie jest potrzebny do działania.
