# Technologie potrzebne do uruchomienia projektu (gameboy_web)

## Środowisko
- Python 3.9 lub nowszy
- Przeglądarka z obsługą WebAssembly (Chrome, Firefox, Safari)
- Projekt powstał na macOS (MacBook M4)

## Biblioteki Pythona
- pygbag 0.9.3 – pakuje grę do WebAssembly i uruchamia ją w przeglądarce
- pygame-ce – biblioteka do gier (w przeglądarce pygbag dołącza ją automatycznie, lokalnie jest potrzebna tylko do uruchomienia przez `python main.py`)
- Pozostałe importy to biblioteka standardowa Pythona (asyncio, random, os, sys, collections, enum, importlib, platform) oraz własne moduły projektu

## Instalacja i uruchomienie
```bash
git clone https://github.com/Sornat123/Gameboy.git
python3 -m venv venv
source venv/bin/activate
pip install -r gameboy_web/requirements.txt
pygbag gameboy_web
```
Po uruchomieniu gra jest dostępna w przeglądarce pod adresem http://localhost:8000

## Uwagi
- Katalog `build` nie jest w repozytorium, pygbag generuje go automatycznie przy uruchomieniu.
- Gry: Snake, Tetris, Labirynt, Kółko i krzyżyk (uruchamiane z menu w main.py).
