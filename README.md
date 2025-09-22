# Crypto Trading Platform Backend

A Django REST API backend for a cryptocurrency trading platform with real-time price updates, user authentication, and premium features.

## 🚀 Features

- **User Authentication**: Registration, login, email verification, password reset
- **Premium Subscriptions**: Premium user features with additional data access
- **Crypto Price API**: Real-time cryptocurrency prices from CoinGecko
- **WebSocket Support**: Real-time price updates via WebSocket connections
- **Comprehensive API**: RESTful API with OpenAPI/Swagger documentation
- **PostgreSQL Database**: Robust database design with proper migrations
- **Celery Integration**: Background tasks for price updates
- **Email Service**: Email verification and notifications via Liara

## 🏗️ Tech Stack

- **Backend**: Django 5.2.5, Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT tokens (django-rest-framework-simplejwt)
- **API Documentation**: drf-spectacular (OpenAPI/Swagger)
- **WebSockets**: Django Channels
- **Background Tasks**: Celery
- **Cache/Message Broker**: Redis
- **Email Service**: Liara SMTP
- **External API**: CoinGecko API for crypto prices

## 📋 Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Redis (for WebSocket and Celery)
- Git

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd uni_project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your actual configuration values
   ```

5. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb your_database_name
   
   # Run migrations
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Populate Sample Crypto Data**
   ```bash
   python manage.py shell -c "
   from crypto.models import CryptoAsset
   CryptoAsset.objects.get_or_create(symbol='BTC', external_id='bitcoin', defaults={'name': 'Bitcoin'})
   CryptoAsset.objects.get_or_create(symbol='ETH', external_id='ethereum', defaults={'name': 'Ethereum'})
   CryptoAsset.objects.get_or_create(symbol='ADA', external_id='cardano', defaults={'name': 'Cardano'})
   "
   ```

## 🚀 Running the Application

1. **Start the development server**
   ```bash
   python manage.py runserver
   ```

2. **Access the application**
   - API Base URL: `http://127.0.0.1:8000/api/`
   - Swagger Documentation: `http://127.0.0.1:8000/swagger/`
   - Admin Panel: `http://127.0.0.1:8000/admin/`

3. **Optional: Start Redis and Celery (for WebSocket and background tasks)**
   ```bash
   # Start Redis server
   redis-server
   
   # Start Celery worker (in separate terminal)
   celery -A backend worker --loglevel=info
   ```

## 📡 API Endpoints

### User Management (`/api/users/`)
- `POST /register/` - User registration
- `POST /login/` - User authentication
- `POST /verify-email/` - Email verification
- `POST /request-password-reset/` - Request password reset
- `POST /reset-password/` - Reset password with code

### Cryptocurrency (`/api/crypto/`)
- `GET /symbols/` - Get all available crypto symbols
- `GET /prices/latest/` - Get latest crypto prices
- `GET /prices/latest/?symbols=BTC,ETH` - Get prices for specific symbols

### Authentication
All API endpoints (except registration and login) require authentication using Bearer tokens:
```
Authorization: Bearer <your-access-token>
```

## 🏗️ Project Structure

```
uni_project/
├── backend/                 # Django project settings
│   ├── settings.py         # Main settings
│   ├── urls.py             # URL configuration
│   └── celery.py           # Celery configuration
├── users/                  # User management app
│   ├── models.py           # User, verification models
│   ├── views.py            # Authentication views
│   ├── serializers.py      # API serializers
│   └── urls.py             # User routes
├── crypto/                 # Cryptocurrency app
│   ├── models.py           # Crypto assets and prices
│   ├── views.py            # Crypto API views
│   ├── tasks.py            # Celery tasks
│   ├── consumers.py        # WebSocket consumers
│   └── urls.py             # Crypto routes
├── tests/                  # Test suite
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

Or run specific test files:
```bash
python tests/run_all_tests.py
```

## 🔧 Configuration

### Environment Variables

Key environment variables in `.env`:

- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `DB_*`: PostgreSQL database configuration
- `REDIS_URL`: Redis connection URL
- `MAIL_*`: Email service configuration (Liara)
- `CRYPTO_API_URL`: CoinGecko API base URL

### Database Configuration

The project uses PostgreSQL exclusively. Ensure your PostgreSQL server is running and the database is created before running migrations.

### Email Configuration

Email verification uses Liara email service. Configure your Liara SMTP credentials in the environment variables.

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Set `DEBUG=False` and use strong `SECRET_KEY`
2. **Database**: Use production PostgreSQL instance
3. **Static Files**: Configure static file serving
4. **Redis**: Set up Redis for production
5. **Celery**: Configure Celery with proper broker
6. **Email**: Ensure email service is properly configured

### Docker Deployment (Optional)

You can containerize this application using Docker. Create appropriate Dockerfile and docker-compose.yml for your deployment needs.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Known Issues

- WebSocket functionality requires Redis to be running
- Email verification requires proper SMTP configuration
- Rate limiting not implemented (consider adding for production)

## 📞 Support

For support or questions, please open an issue in the GitHub repository.

## 🎯 Future Enhancements

- [ ] Add rate limiting
- [ ] Implement trading functionality
- [ ] Add portfolio management
- [ ] Enhanced price charts
- [ ] Mobile app API optimization
- [ ] Advanced authentication (2FA)
- [ ] Integration with more crypto exchanges

---

**Note**: This is a educational/demonstration project. For production use, additional security measures and optimizations should be implemented.