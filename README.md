# 🎟️ TicketHub API

FastAPI aplikacija za upravljanje "tickets" resursima s autentifikacijom, cachingom, rate limitingom i testiranjem.

---

## 🚀 Features

- ✅ REST API za preuzimanje i pretraživanje ticketa
- ✅ JWT autentifikacija
- ✅ Rate limiting (SlowAPI)
- ✅ Caching (in-memory + Redis)
- ✅ Health check endpoint
- ✅ Test suite (pytest + httpx)

---

## 🛠️ Tehnologije

- Python 3.13
- FastAPI
- httpx (async HTTP klijent)
- Redis (opcionalno za caching)
- PyJWT (jose)
- SlowAPI (rate limiting)
- Pytest (testiranje)
- Docker (Dockerfile + docker-compose)

---

## 📦 Instalacija

### 1️⃣ Kloniraj repozitorij
```bash
git clone <repo-url>
cd ticket_hub
```

### 2️⃣ Kreiraj virtualno okruženje i instaliraj ovisnosti
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3️⃣ Pokreni aplikaciju
```bash
uvicorn src.main:app --reload
```

Aplikacija je sada dostupna na: [http://localhost:8000](http://localhost:8000)

### 4️⃣ (Opcionalno) Pokreni s Dockerom
```bash
docker build -t tickethub-api .
docker run -d -p 8000:8000 tickethub-api
```
Ili s docker-compose:
```bash
docker-compose up --build
```

---

## 🔐 Autentifikacija

Koristi DummyJSON user za login:
```
POST /auth/login
{
  "username": "emilys",
  "password": "emilyspass"
}
```

Response:
```json
{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
```
Token koristiti za zaštićene rute (Authorization header):
```
Authorization: Bearer <JWT>
```

---

## 📚 API Rute

| Metoda | Ruta                     | Opis                                  |
|--------|--------------------------|---------------------------------------|
| GET    | `/tickets`               | Lista ticketa s paginacijom/filtrima |
| GET    | `/tickets/{id}`          | Detalji ticketa po ID-u              |
| GET    | `/tickets/search?q=...`  | Pretraga ticketa po nazivu           |
| GET    | `/stats`                 | Statistika ticketa                   |
| GET    | `/health`                | Health check                         |
| POST   | `/auth/login`            | Login i JWT token                    |

---

## 🧪 Testiranje

Pokreni sve testove:
```bash
pytest
```

---

## 🚦 Lintanje

```bash
flake8 src/
```

---

## 📄 License

MIT © 2025 Abysalto AI Academy

