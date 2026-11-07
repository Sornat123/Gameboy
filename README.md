# Gameboy – platforma z grami i backend logowania

## Skład zespołu

Projekt na ćwiczenia z Programowania Front-end, realizowany solo.

| Imię i nazwisko | Numer albumu | Login GitHub |
|---|---|---|
| Dominik Sornat | 56116 | Sornat123 |

## Opis

Projekt składa się z dwóch części w jednym repozytorium:
- `gameboy_web` – gry (Snake, Tetris, Labirynt, Kółko i krzyżyk) uruchamiane w przeglądarce przez pygbag (WebAssembly)
- `gameboy_backend` – backend logowania i zapisu wyników (FastAPI + SQLite)

## Technologie
- Python 3.9 lub nowszy
- pygame-ce i pygbag – gry i ich uruchamianie w przeglądarce
- FastAPI + Uvicorn – API backendu (dokumentacja pod /docs)
- SQLAlchemy + SQLite – baza danych (plik gameboy.db tworzy się sam przy pierwszym starcie)
- JWT (python-jose) oraz passlib + bcrypt – logowanie i hashowanie haseł
- Pydantic – walidacja danych
- Przeglądarka z obsługą WebAssembly (Chrome, Firefox, Safari)

Wszystkie biblioteki są w pliku `requirements.txt` w głównym katalogu.

## Instalacja

    git clone https://github.com/Sornat123/Gameboy.git
    cd Gameboy
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

## Uruchomienie (dwa osobne terminale, w obu aktywne venv)

Terminal 1 – backend (port 8001):

    cd gameboy_backend
    uvicorn main:app --port 8001

Dokumentacja API: http://localhost:8001/docs

Terminal 2 – gry (port 8000), z głównego katalogu repozytorium:

    pygbag gameboy_web

Gry otworzą się w przeglądarce pod adresem http://localhost:8000

## Role użytkowników
- admin – pełne uprawnienia i funkcje administracyjne
- user – zalogowany gracz, jego wyniki są zapisywane
- guest – gracz bez logowania, wyniki nie są zapisywane

## Konto administratora
1. Zarejestruj zwykłego użytkownika (przez /docs lub stronę index.html).
2. W pliku `gameboy_backend/make_admin.py` wpisz jego login w zmiennej target_username.
3. Uruchom:

       cd gameboy_backend
       python make_admin.py

## Uwagi
- Katalog `build` generuje pygbag automatycznie, nie ma go w repozytorium.
- Baza `gameboy.db` nie jest w repozytorium, tworzy się automatycznie.
- Pliki `api_client.py` i `login_window.py.py` w backendzie to stary klient desktopowy (wymaga dodatkowo pygame i requests), nie jest potrzebny do działania.
