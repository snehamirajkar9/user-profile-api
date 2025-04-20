# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import jwt
import datetime
from functools import wraps
import os
from dotenv import load_dotenv
from .models import db, User  # ✅ import db and User from models.py

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'supersecretkey')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///userprofile.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # ✅ Initialize db with app

# Decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except Exception as e:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'User already exists'}), 400
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/profile/<username>', methods=['GET'])
@token_required
def get_profile(current_user, username):
    if current_user.username != username:
        return jsonify({'message': 'Unauthorized access'}), 403
    return jsonify({
        'username': current_user.username,
        'email': current_user.email
    })

@app.route('/profile/<username>', methods=['POST'])
@token_required
def update_profile(current_user, username):
    if current_user.username != username:
        return jsonify({'message': 'Unauthorized access'}), 403
    data = request.get_json()
    current_user.email = data.get('email', current_user.email)
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'})

@app.route('/update_password', methods=['POST'])
@token_required
def update_password(current_user):
    data = request.get_json()
    if not current_user.check_password(data['current_password']):
        return jsonify({'message': 'Current password is incorrect'}), 400
    current_user.set_password(data['new_password'])
    db.session.commit()
    return jsonify({'message': 'Password updated successfully'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')
