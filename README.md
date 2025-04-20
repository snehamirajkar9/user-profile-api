# User Profile API

A secure user profile management API built with Flask.

## Features

- Token-based auth (JWT)
- Profile updates
- Password change with bcrypt
- Logging

## Run Locally

```bash
docker build -t user-profile-api .
docker run -p 5000:5000 user-profile-api
