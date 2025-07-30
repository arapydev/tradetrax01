from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware

from . import models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- Configuración de CORS ---
origins = [
    "http://localhost",
    "http://localhost:5173", # La dirección de nuestro frontend con Vite
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --------------------------

# --- Dependencia para la Sesión de Base de Datos ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoints ---

@app.post("/accounts/", response_model=schemas.Account)
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    db_account = models.Account(**account.model_dump())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@app.get("/accounts/", response_model=List[schemas.Account])
def get_accounts(db: Session = Depends(get_db)):
    accounts = db.query(models.Account).all()
    return accounts

@app.delete("/accounts/{account_id}", status_code=204)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    account_query = db.query(models.Account).filter(models.Account.id == account_id)
    
    if account_query.first() is None:
        raise HTTPException(status_code=404, detail="Account not found")
        
    account_query.delete(synchronize_session=False)
    db.commit()
    return

@app.put("/accounts/{account_id}", response_model=schemas.Account)
def update_account(account_id: int, account_update: schemas.AccountCreate, db: Session = Depends(get_db)):
    account_query = db.query(models.Account).filter(models.Account.id == account_id)
    db_account = account_query.first()

    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    # Actualiza los campos del objeto de la base de datos con los datos de la petición
    for key, value in account_update.model_dump().items():
        setattr(db_account, key, value)
    
    db.commit()
    db.refresh(db_account)
    return db_account
    
@app.get("/")
def health_check():
    # Este endpoint ahora es más simple, ya que no necesita conectarse
    # a la base de datos para probar la conexión.
    return {"status": "ok"}