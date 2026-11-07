# Gameboy Backend – poradnik

Szczegóły backendu (FastAPI). Pełna instrukcja uruchomienia całego projektu jest w `README.md`.

## Co robi backend
- rejestracja i logowanie użytkowników (hasła hashowane bcrypt, logowanie przez tokeny JWT)
- zapis wyników graczy i tabela wyników (gry: snake, tetris, labirynt, kółko i krzyżyk)
- role: admin, user, guest (gość nie ma zapisywanych wyników)

## Uruchomienie samego backendu (port 8001)

    git clone https://github.com/Sornat123/Gameboy.git
    cd Gameboy
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd gameboy_backend
    uvicorn main:app --port 8001 --reload

- http://localhost:8001 – komunikat, że backend działa
- http://localhost:8001/docs – dokumentacja API do testowania w przeglądarce

## Strona projektu
Stroną, od której zaczyna się korzystanie z projektu, jest plik `gameboy_backend/index.html`. Otwiera się go w przeglądarce, gdy działa backend (port 8001) i gry (port 8000, `pygbag gameboy_web`).

## Konto administratora
1. Zarejestruj użytkownika na stronie `index.html`.
2. W `gameboy_backend/make_admin.py` wpisz jego login w zmiennej target_username.
3. Uruchom w folderze `gameboy_backend` (z aktywnym venv):

       python make_admin.py

## Uwagi
- Baza `gameboy.db` tworzy się sama przy pierwszym starcie.
- Pliki `api_client.py` i `login_window.py.py` to stary klient desktopowy, niepotrzebny do działania serwera.
