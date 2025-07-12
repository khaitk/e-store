# E-Store Microservices

## Architect

```
e-store/
├── docker-compose.yml      # Docker Compose
├── nginx/                  # Nginx
├── product/                # (Python/FastAPI)
│   ├── Dockerfile
│   ├── app/
│   │   ├── api/
│   │   ├── db/
│   │   ├── models/
│   │   └── main.py
│   └── requirements.txt
├── payment/                # Payment (Python/FastAPI + Stripe)
│   ├── Dockerfile
│   ├── app/
│   │   ├── api/
│   │   ├── db/
│   │   ├── models/
│   │   ├── services/
│   │   └── main.py
│   └── requirements.txt
└── coupon/                 # Coupon (Node.js/Express)
    ├── Dockerfile
    ├── src/
    │   ├── index.js
    │   ├── routes/
    │   ├── models/
    │   └── controllers/
    └── package.json
```