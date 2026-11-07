from database import SessionLocal
import models


db = SessionLocal()


target_username = "Dominik.Sornat.admin"

user = db.query(models.User).filter(models.User.username == target_username).first()

if user:
    user.role = "admin"
    db.commit()
    print(f"Sukces! Użytkownik '{target_username}' ma teraz uprawnienia administratora (role = admin).")
else:
    print(f"Błąd: Nie znaleziono użytkownika o loginie '{target_username}'. Najpierw go zarejestruj!")

db.close()