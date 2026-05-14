from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, timedelta

from database import SessionLocal, engine
from models import Base, Contact
from schemas import ContactCreate, ContactResponse
import crud

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Contacts API"}


# -------------------------
# GET ALL CONTACTS
# -------------------------
@app.get("/contacts", response_model=list[ContactResponse])
def get_contacts(db: Session = Depends(get_db)):
    return crud.get_contacts(db)


# -------------------------
# GET CONTACT BY ID
# -------------------------
@app.get("/contacts/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = crud.get_contact(db, contact_id)

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    return contact


# -------------------------
# CREATE CONTACT
# -------------------------
@app.post("/contacts", response_model=ContactResponse)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    return crud.create_contact(db, contact)


# -------------------------
# UPDATE CONTACT
# -------------------------
@app.put("/contacts/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int,
    body: ContactCreate,
    db: Session = Depends(get_db)
):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()

    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    contact.first_name = body.first_name
    contact.last_name = body.last_name
    contact.email = body.email
    contact.phone_number = body.phone_number
    contact.birthday = body.birthday
    contact.additional_data = body.additional_data

    db.commit()
    db.refresh(contact)

    return contact


# -------------------------
# DELETE CONTACT
# -------------------------
@app.delete("/contacts/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = crud.delete_contact(db, contact_id)

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    return {"message": "Contact deleted"}


# -------------------------
# SEARCH CONTACTS
# -------------------------
@app.get("/search/", response_model=list[ContactResponse])
def search_contacts(
    query: str,
    db: Session = Depends(get_db)
):
    contacts = db.query(Contact).filter(
        or_(
            Contact.first_name.ilike(f"%{query}%"),
            Contact.last_name.ilike(f"%{query}%"),
            Contact.email.ilike(f"%{query}%")
        )
    ).all()

    return contacts


# -------------------------
# UPCOMING BIRTHDAYS
# -------------------------
@app.get("/birthdays/", response_model=list[ContactResponse])
def upcoming_birthdays(db: Session = Depends(get_db)):
    today = datetime.today().date()
    next_week = today + timedelta(days=7)

    contacts = db.query(Contact).all()

    upcoming = []

    for contact in contacts:
        birthday_this_year = contact.birthday.replace(year=today.year)

        if today <= birthday_this_year <= next_week:
            upcoming.append(contact)

    return upcoming