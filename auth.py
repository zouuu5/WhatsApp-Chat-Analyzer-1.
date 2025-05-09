import streamlit as st
import pickle
import os
import hashlib
import time
from datetime import datetime, timedelta

# Create a directory to store user data if it doesn't exist
if not os.path.exists("user_data"):
    os.makedirs("user_data")

# File to store user credentials
USER_DB = "user_data/users.pkl"

def load_users():
    """Load user database from file"""
    if os.path.exists(USER_DB):
        with open(USER_DB, "rb") as f:
            return pickle.load(f)
    return {}  # Return empty dict if file doesn't exist

def save_users(users):
    """Save user database to file"""
    with open(USER_DB, "wb") as f:
        pickle.dump(users, f)

def hash_password(password):
    """Create a SHA-256 hash of the password"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password, email):
    """Create a new user account"""
    users = load_users()
    
    # Check if username already exists
    if username in users:
        return False, "Username already exists"
    
    # Create new user entry
    users[username] = {
        "password_hash": hash_password(password),
        "email": email,
        "created_at": datetime.now(),
        "last_login": None,
        "analysis_history": []
    }
    
    save_users(users)
    return True, "Account created successfully"

def authenticate(username, password):
    """Authenticate user credentials"""
    users = load_users()
    
    if username not in users:
        return False, "Invalid username or password"
    
    if users[username]["password_hash"] != hash_password(password):
        return False, "Invalid username or password"
    
    # Update last login time
    users[username]["last_login"] = datetime.now()
    save_users(users)
    
    return True, "Login successful"

def record_analysis(username, file_name, analysis_type):
    """Record user analysis for history tracking"""
    if not username or username == "Guest":
        return
    
    users = load_users()
    if username in users:
        users[username]["analysis_history"].append({
            "file_name": file_name,
            "analysis_type": analysis_type,
            "timestamp": datetime.now()
        })
        save_users(users)

def init_session_state():
    """Initialize session state variables for authentication"""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "login_time" not in st.session_state:
        st.session_state.login_time = None

def login_user(username):
    """Set session state for logged in user"""
    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.login_time = datetime.now()

def logout_user():
    """Clear session state on logout"""
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.login_time = None

def get_user_history(username):
    """Get analysis history for a user"""
    users = load_users()
    if username in users:
        return users[username]["analysis_history"]
    return []

def get_session_duration():
    """Get current session duration in minutes"""
    if st.session_state.login_time:
        delta = datetime.now() - st.session_state.login_time
        return round(delta.total_seconds() / 60, 1)
    return 0