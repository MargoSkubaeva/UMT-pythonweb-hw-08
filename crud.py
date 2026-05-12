from sqlalchemy.orm import Session
from models import Contact
from schemas import ContactCreate

def get_contacts(db: Session):
    return db.query(Contact).all()

def get_contact(db: Session, contact_id: int):
    return db.query(Contact).filter(Contact.id == contact_id).first()

def create_contact(db: Session, contact: ContactCreate):
    db_contact = Contact(**contact.model_dump())

    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)

    return db_contact

def delete_contact(db: Session, contact_id: int):
    contact = get_contact(db, contact_id)

    if contact:
        db.delete(contact)
        db.commit()

    return contact