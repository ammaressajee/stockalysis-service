from app import db

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {"id": self.id, "fname": self.fname, "lname": self.lname, "email": self.email, "contact_number": self.contact_number, "message": self.message}
