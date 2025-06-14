# System Rezerwacji Sprzętu

Projekt aplikacji webowej służącej do zarządzania rezerwacjami sprzętu sportowego, napisany w Pythonie z użyciem Flask.

---

## Spis treści
- [Opis projektu](#opis-projektu)
- [Technologie](#technologie)
- [Funkcjonalności](#funkcjonalności)
- [Instrukcja uruchomienia](#instrukcja-uruchomienia)

---

## Opis projektu

Aplikacja umożliwia:

- Rejestrację i logowanie użytkowników
- Dodawanie, edycję i usuwanie sprzętu (dla administratora)
- Przeglądanie listy sprzętu
- Rezerwowanie dostępnego sprzętu
- Anulowanie rezerwacji (przez właściciela lub administratora)

---

## Technologie

- Python 3.x  
- Flask – framework webowy  
- SQLite – baza danych  
- SQLAlchemy – ORM do pracy z bazą danych  
- Flask-Login – zarządzanie sesjami i użytkownikami  
- Bootstrap – stylizacja frontendowa  

---

## Funkcjonalności

- Bezpieczne logowanie z haszowaniem haseł  
- Rozdzielenie ról: użytkownik i administrator  
- Formularze rezerwacji sprzętu z walidacją dat  
- Obsługa przesyłania zdjęć sprzętu  
- Przejrzysty i responsywny interfejs użytkownika  

---

## Instrukcja uruchomienia

1. **Sklonuj repozytorium**
```bash
git clone https://github.com/Sebastian-Nieli/62319.git
cd 62319
```

2. **Utwórz środowisko wirtualne i je aktywuj**

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```
3. **Zainstaluj wymagane biblioteki**

```bash
pip install -r requirements.txt
```
4. **Uruchom aplikację**

```bash
python app.py
```
5. **Otwórz przeglądarkę i przejdź do**

http://localhost:5000
