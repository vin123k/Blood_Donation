from flask import Flask, render_template, Blueprint,request,redirect,url_for,flash
from flask_login import login_required,current_user
from .models import Donor,BloodStock
from . import db
import smtplib
from email.message import EmailMessage

donate=Blueprint('donate',__name__)

def send_mail1():
    # Email details
    sender_email = "itsananya.37@gmail.com"   # Replace with your email
    sender_password = "pxbx mqlu yeqz fjdg"         # Replace with your app password or real password (better to use environment variables)

    # Create the email message
    msg = EmailMessage()
    msg['Subject'] = "Blood Donation Request Received"
    msg['From'] =  sender_email # You can change the display name
    msg['To'] = "vinayak21csu116@ncuindia.edu"

    # Email body
    msg.set_content(f"""\
Dear Recipient,

There is someone who wants to donate blood. 

Kindly check the portal for more details regarding the donor's information. 
We appreciate your prompt attention to this noble cause and encourage you to reach out to the donor at your earliest convenience.

Thank you for being a vital part of this life-saving network.

Best regards,
Itsanya Blood Donation Team
""")

    try:
        # Set up the SMTP server (using Gmail's SMTP server here as an example)
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.send_message(msg)
    except Exception as e:
        print("Failed to send email:", e)
    

@donate.route('/donate',methods=['GET','POST'])
@login_required
def donate1():
    if request.method == 'POST':
        category = request.form.get('category')
        date = request.form.get('date')
        time = request.form.get('time')
        print(f"Category: {category}, Date: {date}, Time: {time}")
        new_donor = Donor(
            email=current_user.email,
            category=category,
            date=date,
            time=time
        )

        print("hello")
        print(current_user.email)

        db.session.add(new_donor)
        db.session.commit()
        send_mail1()
        # amount_map = {
        #     'Whole': 450,
        #     'Red Blood': 330,
        #     'Platelets': 200,
        #     'Plasma': 600
        # }
        # amount = amount_map.get(category, 0)

        # # Find the corresponding BloodStock entry for the user's blood group and category
        # stock = BloodStock.query.filter_by(blood_group=current_user.blood_group, category=category).first()

        # if stock:
        #     # Update the amount
        #     stock.amount += amount
        #     db.session.commit()

        #     flash(f"Blood stock updated! {amount} units added to {category}.", category='success')
        # else:
        #     flash(f"No matching blood stock found for {category}.", category='error')

        # flash("Your donation request has been submitted!", category='success')
        return render_template('contact.html')
    return render_template('donate.html')
