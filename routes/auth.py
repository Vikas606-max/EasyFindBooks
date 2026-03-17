from flask import Blueprint, request, jsonify
from model.user import User
from db import db
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)