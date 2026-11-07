import requests

class APIClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.username = None

    def login(self, username, password):
        """Wysyła żądanie logowania do API."""
        try:
            response = requests.post(f"{self.base_url}/api/auth/login", json={
                "username": username,
                "password": password
            })
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token") or data.get("access_token")
                self.user_id = data.get("user_id") or data.get("id")
                self.username = username
                return True, "Zalogowano pomyślnie!"
            else:
                error_msg = response.json().get("message", "Błąd logowania")
                return False, error_msg
        except requests.exceptions.RequestException as e:
            return False, f"Błąd połączenia z serwerem: {e}"

    def submit_score(self, game_name, score):
        """Wysyła wynik gry do bazy danych przez API."""
        if not self.token:
            return False, "Brak aktywnej sesji (nie jesteś zalogowany)"
        
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = requests.post(f"{self.base_url}/api/scores", json={
                "game": game_name,
                "score": score,
                "user_id": self.user_id
            }, headers=headers)
            
            if response.status_code in [200, 201]:
                return True, "Wynik został zapisany!"
            else:
                return False, "Nie udało się zapisać wyniku."
        except requests.exceptions.RequestException as e:
            return False, f"Błąd sieci: {e}"