# Gameboy Backend – technologie i poradnik uruchomienia

Backend logowania i zapisu wyników dla platformy z grami (folder `gameboy_web` w tym samym repozytorium). Ogólny opis całego projektu jest w README w głównym katalogu repozytorium.

## Technologie
- Python 3.9 lub nowszy
- FastAPI – framework API (z automatyczną dokumentacją pod /docs)
- Uvicorn – serwer uruchamiający aplikację
- SQLAlchemy + SQLite – baza danych (plik gameboy.db tworzy się sam przy pierwszym starcie)
- JWT (python-jose) – tokeny logowania
- passlib + bcrypt – bezpieczne hashowanie haseł
- Pydantic – walidacja danych

## Role użytkowników
- admin – pełne uprawnienia i dodatkowe funkcje administracyjne
- user – zalogowany gracz, jego wyniki są zapisywane
- guest – gracz bez logowania, wyniki nie są zapisywane

## Uruchomienie backendu (port 8001)

    git clone https://github.com/Sornat123/Gameboy.git
    cd Gameboy/gameboy_backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    uvicorn main:app --port 8001 --reload

Dokumentacja i testowanie API w przeglądarce: http://localhost:8001/docs

## Konto administratora
1. Zarejestruj zwykłego użytkownika (przez /docs lub stronę index.html).
2. Otwórz make_admin.py i wpisz jego login w zmiennej target_username.
3. Uruchom (z aktywnym venv, w folderze gameboy_backend):

       python make_admin.py

## Uruchomienie platformy z grami (port 8000)
W osobnym terminalu, w głównym katalogu repozytorium (Gameboy):

    source gameboy_backend/venv/bin/activate
    pygbag gameboy_web

Gry otworzą się w przeglądarce pod adresem http://localhost:8000

## Uwagi
- Baza gameboy.db nie jest w repozytorium – tworzy się automatycznie.
- Pliki api_client.py i login_window.py.py to stary klient desktopowy (wymaga dodatkowo pygame i requests), nie jest potrzebny do działania serwera.to stary klient desktopowy (wymaga dodatkowo pygame i requests), nie jest potrzebny do działania serwera.
