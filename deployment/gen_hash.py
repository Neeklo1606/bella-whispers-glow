from passlib.context import CryptContext
p = CryptContext(schemes=["bcrypt"], deprecated="auto")
print(p.hash("Admin123!"))
