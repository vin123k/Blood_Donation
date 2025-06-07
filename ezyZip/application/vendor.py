from flask import Flask, Blueprint, render_template, redirect, url_for, flash,request
from werkzeug.security import generate_password_hash,check_password_hash
from .models import Vendor, Donor, BloodStock, User
from flask_login import login_user,login_required
from . import db
from sqlalchemy.orm import joinedload


vendor=Blueprint('vendor1',__name__)

@vendor.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        contact=request.form.get('contact')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        print("first:", first_name)
        print("last:", last_name)
        print("email:", email)

        vendor = Vendor.query.filter_by(email=email).first()

        if vendor:
            flash("Email already exists", category='error')
        elif password != confirm_password:
            flash("Passwords do not match", category='error')
        else:
            new_vendor = Vendor(
                first_name=first_name,
                last_name=last_name,
                contact=contact,
                email=email,
                password_hash=generate_password_hash(password)
            )
            db.session.add(new_vendor)
            db.session.commit()
            flash("Account created successfully", category='success')
            login_user(new_vendor, remember=False)
            return redirect(url_for('vendor1.home'))
    return render_template('vendor-signup.html')
@vendor.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        vendor = Vendor.query.filter_by(email=email).first()

        print("email:", email)
        print("password:", password)

        if vendor:
            if check_password_hash(vendor.password_hash, password):
                print("Logged in")
                flash("Logged in successfully", category='success')
                login_user(vendor, remember=False)
                return redirect(url_for('vendor1.home'))  # replace with your route
            else:
                print("Stored password:", vendor.password_hash)
                print("Entered password:", password)
                flash("Incorrect password", category='error')
        else:
            print("Vendor does not exist")
            flash("Email not registered", category='error')
    return render_template('vendor-login.html')
@vendor.route('/')
def home():
    #Finds list of people who want to donate
    return render_template('vendor.html')
@vendor.route('/unseen')
def find():
    unseen_list = Donor.query.filter_by(seen=False).all()
    # unseen_list = Donor.query.options(joinedload(Donor.user)).filter_by(seen=False).all()
    return render_template('unseen_donors.html', donors=unseen_list)
    return "done"

# @vendor.route('/verify')
# @login_required
# def verify():
#     # Verifies 
#     # If blood is fit for donation, email to be sent to the donor

#     return "done"

@vendor.route('/verify_donor')
def verify_donor():
    donors = Donor.query.filter_by(seen=False).all()
    return render_template('verify_donor.html', donors=donors)

@vendor.route('/process_verification/<int:donor_id>', methods=['POST'])
def process_verification(donor_id):
    donor = Donor.query.get_or_404(donor_id)

    seen = request.form.get('seen') == 'true'
    verified = request.form.get('verified') == 'true'

    donor.seen = seen
    donor.verfied = verified

    # Update stock if both are true
    if seen and verified:
        quantity_map = {
            'platelets': 200,
            'whole_blood': 450,
            'red_blood': 330,
            'plasma': 600
        }
        
        category = donor.category.strip().lower()
        print("category ",category)
        quantity_to_add = quantity_map.get(category)
        print("quantity to add ",quantity_to_add)
        user = User.query.filter_by(email=donor.email).first()
        if user:
            blood_group = user.blood_group
        stock = BloodStock.query.filter_by(category=donor.category,blood_group=blood_group).first()
        print(stock)
        if stock:
            stock.amount += quantity_to_add

    db.session.delete(donor)
    db.session.commit()

    flash(f'Donor {donor.email} processed and removed.', 'success')
    return render_template('thank.html')


