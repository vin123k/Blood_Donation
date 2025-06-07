from . import db
from flask_login import UserMixin

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    first_name=db.Column(db.String(100))
    last_name=db.Column(db.String(100))
    email=db.Column(db.String(100))
    age=db.Column(db.Integer)
    phone=db.Column(db.String(15))
    state=db.Column(db.String(15))
    city=db.Column(db.String(15))
    blood_group=db.Column(db.String(10))
    password=db.Column(db.String(100))
    def __repr__(self):
        return f"<User {self.id} | {self.email} | {self.password}>"
                                                              
class Messages(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    sender_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    receiver_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    message=db.Column(db.String(10000),nullable=False)
    timestamp=db.Column(db.DateTime,default=db.func.current_timestamp())

    def __init__(self, sender_id, receiver_id, message):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.message = message
    
class BloodStock(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    blood_group=db.Column(db.String(5))
    category=db.Column(db.String(20))
    amount=db.Column(db.Integer)

class Vendor(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    first_name=db.Column(db.String(50))
    last_name=db.Column(db.String(50))
    contact = db.Column(db.String(20))
    email=db.Column(db.String(50))
    password_hash = db.Column(db.String(150), nullable=False)



class Donor(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50),db.ForeignKey('user.email'))
    category=db.Column(db.String(50))
    date=db.Column(db.String(50))
    time=db.Column(db.String(50))
    seen=db.Column(db.Boolean(),default=False)
    verfied=db.Column(db.Boolean(),default=False)

    user = db.relationship('User', backref='donations')


    

