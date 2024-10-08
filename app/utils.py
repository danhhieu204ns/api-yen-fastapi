from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password, hassed_password):
    return pwd_context.verify(plain_password, hassed_password)