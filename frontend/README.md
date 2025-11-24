# Credit Guardian - Frontend

React + Vite frontend за Credit Guardian API.

## Функции
- 📊 Dashboard със статистики
- 🔍 Търсене и проверка на кредитори
- 🧮 ГПР калкулатор
- 📄 Анализ на кредитни договори (PDF/DOCX/TXT)

## Локално разработване

```powershell
cd frontend
npm install
npm run dev
```

Отваря на `http://localhost:3000`

API proxy към `http://localhost:8000` (вж. `vite.config.js`)

## Production Build

```powershell
npm run build
npm run preview
```

## Docker

```powershell
docker compose up -d frontend
```

Frontend достъпен на `http://localhost:3000`

## API Integration

Axios клиент в `src/api/client.js` с endpoints:
- `GET /stats` - статистики
- `GET /creditor/{name}` - данни за кредитор
- `POST /gpr/calculate` - изчисляване на ГПР
- `POST /contract/analyze` - анализ на договор (multipart/form-data)

## Environment Variables

`.env` (опционално):
```
VITE_API_URL=http://localhost:8000
```

## Архитектура

```
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard.jsx
│   │   ├── CreditorSearch.jsx
│   │   ├── GPRCalculator.jsx
│   │   └── ContractAnalyzer.jsx
│   ├── api/
│   │   └── client.js
│   ├── App.jsx
│   ├── App.css
│   └── main.jsx
├── index.html
├── vite.config.js
├── package.json
├── Dockerfile
└── nginx.conf
```

## S3 Storage (Backend)

Опционално: backend може да качва PDF в AWS S3.

Конфигурация в `.env`:
```
AWS_S3_BUCKET=credit-guardian-contracts
AWS_REGION=eu-central-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

Backend script: `utils/s3_storage.py`

Ако S3 не е конфигуриран, файлове се обработват временно локално.
