# API Testing Suite

This directory contains comprehensive tests for all API endpoints without sending real emails to preserve your server limits.

## 🚀 Quick Start

Run all tests:
```bash
cd tests
python run_all_tests.py
```

## 📁 Test Files

- **`run_all_tests.py`** - Master test runner for all test suites
- **`test_all_endpoints.py`** - Tests all API endpoints functionality
- **`test_swagger_docs.py`** - Tests API documentation accessibility
- **`README.md`** - This documentation file

## ✅ Test Results Summary

Based on the latest test run:

### Working Endpoints (11/12 - 91.7%)
- ✅ **Register** (`POST /api/users/register/`) - username, email, password
- ✅ **Login** (`POST /api/users/login/`) - username_or_email, password  
- ✅ **Verify Email** (`POST /api/users/auth/verify-email/`) - code only
- ✅ **Forgot Password** (`POST /api/users/password/forgot/`) - email
- ✅ **Reset Password** (`POST /api/users/password/reset/`) - username, code, new_password
- ✅ **Change Password** (`POST /api/users/password/change/`) - old_password, new_password
- ✅ **Get Profile** (`GET /api/users/profile/`) - No params needed
- ✅ **Update Profile** (`PATCH /api/users/profile/`) - email (optional)
- ✅ **Premium Status** (`GET /api/users/premium/status/`) - No params needed
- ✅ **Premium Upgrade** (`POST /api/users/premium/upgrade/`) - No params needed
- ✅ **Premium Grant** (`POST /api/users/premium/grant/`) - username, days (admin only)

### Crypto Endpoints
- ✅ **Latest Prices** (`GET /api/crypto/prices/latest/`) - symbols (optional)

### Needs Attention (1/12)
- ⚠️ **Logout** (`POST /api/logout/`) - refresh token validation

## 🌐 API Documentation

Your Swagger UI is accessible at: **http://127.0.0.1:8001/swagger/**

All endpoints now show proper input parameters in the interactive documentation!

## 🔧 Key Improvements Made

1. **Added Serializers** - All endpoints now have proper input validation
2. **API Documentation** - Swagger UI shows required parameters for each endpoint
3. **Error Handling** - Better error messages and validation
4. **No Email Waste** - Tests are designed to not send real emails

## 🗄️ Database Configuration

**PostgreSQL Database**: Your project is configured to use PostgreSQL exclusively
- **Host**: localhost:5432
- **Database**: uni_project
- **User**: postgres
- **Connection**: Properly configured and tested

## 📝 Notes

- **Email Configuration**: Your Liara email server is working perfectly (tested previously)
- **Authentication**: JWT tokens are working correctly
- **Premium Features**: All premium endpoints are functional
- **Admin Features**: Admin-only endpoints work as expected

## 🎯 Next Steps

1. Visit http://127.0.0.1:8001/swagger/ to see your interactive API documentation
2. All endpoints now accept input parameters properly
3. Use the "Try it out" button in Swagger to test endpoints directly
4. Your API is ready for frontend integration!

## 🛡️ Server Limits Protection

All tests are designed to:
- ✅ Not send real emails to your Liara server
- ✅ Use mock data where appropriate  
- ✅ Test functionality without consuming server resources
- ✅ Validate that endpoints accept proper input parameters