import sys
import os

# Add the current directory to path so we can import models
sys.path.append(os.getcwd())

try:
    from models.database import SessionLocal, User
    from passlib.context import CryptContext
    
    # Try using a different backend for bcrypt if the default one is buggy on 3.13
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    db = SessionLocal()
    
    email = "admin@example.com"
    password = "password123"
    
    # Check if user exists
    user = db.query(User).filter(User.email == email).first()
    if not user:
        hashed_pw = pwd_context.hash(password)
        new_user = User(email=email, hashed_password=hashed_pw)
        db.add(new_user)
        db.commit()
        print(f"User {email} created successfully.")
    else:
        print(f"User {email} already exists.")
    
    db.close()
except Exception as e:
    print(f"Error: {e}")
    # Fallback to manual check if passlib is totally broken
    print("Trying fallback without passlib...")
    try:
        # Note: This is NOT secure but for a local dev test it unblocks the user
        from models.database import SessionLocal, User
        db = SessionLocal()
        # Just use a simple hash or plain text if we had to, but let's try to fix the lib
        print("Manual account creation failed due to library issues. Please register via the app if possible.")
        db.close()
    except:
        pass
