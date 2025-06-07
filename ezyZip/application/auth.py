from flask import render_template,Blueprint,request,redirect,url_for,flash,session
from .models import User,Messages
from . import db
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_required,login_user,current_user
import smtplib
from email.message import EmailMessage
from flask_session import Session
import random
import time
import pandas as pd
import itertools
from .models import BloodStock
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

auth=Blueprint('auth',__name__)
s = URLSafeTimedSerializer('your_secret_key')

def send_email(to_email, subject, body):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'itsananya.37@gmail.com'
    sender_password = 'pxbx mqlu yeqz fjdg'

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()

@auth.route('/login',methods=['GET','POST'])
def login():   
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()
        print("email ",email)
        print("password ",password)
        if user:
            if check_password_hash(user.password,password):
                print('Logged in')
                flash('Logged in successfully',category='success')
                login_user(user,remember=False)
                session.permanent = False
                return redirect(url_for('views.func'))
            else:
                print("user ",user.password)
                print("pass ",password)
                print("incorrect passowrd")
                flash('The password is wrong',category='error')
        else:
            print('The user does not exist')
            flash('The user does not exist',category='error')
    return render_template('login1.html')

@auth.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        first_name=request.form.get('firstname')
        print(first_name)
        last_name=request.form.get('lastname')
        email=request.form.get('email')
        age=request.form.get('age')
        phone=request.form.get('phone')
        state=request.form.get('state')
        city=request.form.get('city')
        blood_group=request.form.get('blood group')
        password1=request.form.get('password1')
        password2=request.form.get('password2')
        user=User.query.filter_by(email=email).first()
        if user:
            flash('User already exists',category='error')
        elif len(first_name)<2:
            flash('Name is too short',category='error')
        elif len(last_name)<2:
            flash('Name is too short',category='error')
        elif not validate_email(email):
            flash('Invalid email address.', category='error')
        elif not validate_phone(phone):
            flash('Invalid phone number. It must be exactly 10 digits.', category='error')
        elif not validate_password(password1):
            flash('Password must be at least 7 characters long, and contain at least 1 uppercase, 1 lowercase, 1 number, and 1 special character.', category='error')
        elif password1!=password2:
           flash("Both password do not match", category='error')
        # elif age<0:
        #     flash("Invalid age ",category='error')
        else:
            user_data = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'age': age,
                'phone': phone,
                'state': state,
                'city': city,
                'blood_group': blood_group,
                'password': generate_password_hash(password1, method='pbkdf2:sha256')
            }
            token = s.dumps(user_data, salt='email-confirm')

            confirm_url = url_for('auth.confirm_email', token=token, _external=True)
            body = f"Hi {first_name},\n\nPlease click the link below to confirm your email address:\n\n{confirm_url}\n\nThank you!"

            send_email(email, 'Confirm Your Email', body)

            flash('A confirmation email has been sent. Please check your inbox.', category='success')
            return redirect(url_for('auth.login'))
            
            #   new_user=User(first_name=first_name,last_name=last_name,email=email,age=age,phone=phone,state=state,city=city,blood_group=blood_group,password=generate_password_hash(
            #     password1, method='pbkdf2:sha256'))
            #   db.session.add(new_user)
            #   db.session.commit()
            #   flash('Your account has been created',category='success')
            #   login_user(new_user,remember=False)
            #   send_mail(email)
            #   return redirect(url_for('views.func'))

       
       
            
        
               
        
        # print("firstname"+firstname)
        # print("lastname"+lastname)
        # print("email"+email)
        # print("age"+age)
        # print("phone "+phone)
        # print("state "+state)
        # print("city "+city)
        # print("blood_group "+ blood_group)
        # print("password1 "+password1)
        # print("password2 "+password2)


    return render_template('signup1.html')

def validate_phone(phone):
    return bool(re.fullmatch(r'\d{10}', phone))
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.fullmatch(pattern, email))


def validate_password(password):
    if len(password) < 7:
        return False
    if not re.search(r'[A-Z]', password):  # At least one uppercase letter
        return False
    if not re.search(r'[a-z]', password):  # At least one lowercase letter
        return False
    if not re.search(r'[0-9]', password):  # At least one digit
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):  # At least one special character
        return False
    return True

@auth.route('/confirm/<token>')
def confirm_email(token):
    try:
        user_data = s.loads(token, salt='email-confirm', max_age=3600)
    except Exception as e:
        flash('The confirmation link is invalid or has expired.', category='error')
        return redirect(url_for('auth.signup'))

    # existing_user = User.query.filter_by(email=user_data['email']).first()
    # if existing_user:
    #     flash('Account already exists. Please login.', category='info')
    #     return redirect(url_for('auth.login'))

    new_user = User(
        first_name=user_data['first_name'],
        last_name=user_data['last_name'],
        email=user_data['email'],
        age=user_data['age'],
        phone=user_data['phone'],
        state=user_data['state'],
        city=user_data['city'],
        blood_group=user_data['blood_group'],
        password=user_data['password']
    )
    db.session.add(new_user)
    db.session.commit()

    #flash('Your email is confirmed and your account has been created! Please login.', category='success')
    # login_user(new_user,remember=False)
    # # send_mail(User.email)
    # return redirect(url_for('views.func'))
    return render_template('confirm_success.html')

# @auth.route('/test')
# def test():
#     # Read and clean Excel data
#     df = pd.read_excel('application\Blood Donation Questionnaire  (Responses) (1).xlsx')
#     df.columns = df.columns.str.strip()
    
#     grouped_df = df.groupby(
#         ['Your Blood Group', 'How much you want to donate?'],
#         as_index=False
#     )['Amount'].sum()

#     grouped_df.columns = ['blood_group', 'category', 'amount']

#     category_mapping = {
#         'Whole Blood- (450–500 ml)': 'whole_blood',
#         'Double Red Cells-   (330–400 ml of red cells)': 'red_blood',
#         'Platelets (Apheresis)-  (200–300 ml of platelets)': 'platelets',
#         'Plasma (Apheresis)-   (600–800 ml of plasma)': 'plasma'
#     }

#     grouped_df['category'] = grouped_df['category'].replace(category_mapping)

#     all_blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
#     all_categories = ['whole_blood', 'red_blood', 'platelets', 'plasma']

#     all_combinations = pd.DataFrame(
#         list(itertools.product(all_blood_groups, all_categories)),
#         columns=['blood_group', 'category']
#     )
#     all_combinations['amount'] = 0

#     # Merge to get final table
#     final_df = pd.merge(all_combinations, grouped_df,
#                         on=['blood_group', 'category'], how='left')
#     final_df['amount'] = final_df['amount_y'].fillna(0).astype(int)
#     final_df = final_df[['blood_group', 'category', 'amount']]

#     # Add to DB using app context
#     for _, row in final_df.iterrows():
#         blood_stock = BloodStock(
#             blood_group=row['blood_group'],
#             category=row['category'],
#             amount=row['amount']
#         )
#         db.session.add(blood_stock)

#     db.session.commit()

#     return "Data successfully added to BloodStock table!"

        

 
def valid_mail(email):
   otp=generate_opt()
   session['otp']=otp
   session['email']=email
   send_otp(email,otp)
   return url_for('auth.valid_otp')







   

def generate_opt():
   return str(random.randint(100000,600000))

@auth.route('/valid',methods=['GET','POST'])
def valid_otp(email,otp):
  if request.method=='POST':
    otp=request.form.get('OTP')
    if otp in session and session['otp']==otp:
       return True
    else:
       return False


        
    
  return render_template('forgot_otp.html')
   
   

def send_otp(email,otp):
    SMTP_SERVER = "smtp.gmail.com"  # Replace with your SMTP server
    SMTP_PORT = 587  # Use 465 for SSL, 587 for TLS
    EMAIL_ADDRESS = "itsananya.37@gmail.com"  # Sender's email
    EMAIL_PASSWORD = "pxbx mqlu yeqz fjdg"
    msg = EmailMessage()
    msg["From"] = "Blood donation"  # Custom sender name
    msg["To"] = email  # Receiver's email
    msg["Subject"] = "OTP for password change"
    msg.set_content(f"Your OTP is : {otp}")

# Send email
    try:
     with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()  # Secure the connection
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
     print(f"Error: {e}")
   

@auth.route('/forgot',methods=['GET','POST'])
def forgot():
   
   if request.method=='POST':
      email=request.form.get('email')
      email=User.query.filter_by(email=email).first()
      if email:
         otp=generate_opt()
         session['otp']=otp
         session['email']=email.email
         send_otp(email.email,otp)
         return redirect(url_for('auth.forgot1'))
      else:
         flash('This email ID does not exist',category='error')
   return render_template('forgot_email.html')

@auth.route('/forgot1',methods=['GET','POST'])
def forgot1():
   if request.method=='POST':
      otp=request.form.get('OTP')
      if 'otp' in session and session['otp'] == otp:
            return redirect(url_for('auth.forgot2'))
      else:
         flash('Incorrect OTP',category='error')
         
   return render_template('forgot_otp.html')

@auth.route('/forgot2',methods=['GET','POST'])
def forgot2():
   email=session['email']
   user=User.query.filter_by(email=email).first()
   if request.method=='POST':
      password1=request.form.get('password1')
      password2=request.form.get('password2')
      hashed=generate_password_hash(password1)
      user.password=hashed
      db.session.commit()
      session.pop('email',None)
      session.pop('otp',None)
      flash("The password has been reset",category='success')
      return redirect(url_for('auth.login'))
   return render_template('forgot.html')
#    if 'email' not in session:  
#       flash("Session expired. Please restart the password reset process.", category="error")
#       return redirect(url_for('auth.forgot'))
#    print("session is ",session['email'])
#    if request.method=='POST':
#     #   print(session.get('email'))
#       password1=request.form.get('password1')
#       password2=request.form.get('password2')
#       print(password1)
#       if(password1!=password2):
#          flash('Both the passwords do not match',category='error')
#       else:
#          print('hello')
#          email=session.get('email')
#          user=User.query.filter_by(email=email).first()
#          print('hello1')
#          hashed_password=generate_password_hash(password1)
#          if user:
#             user.password=hashed_password
#             db.session.commit()
#             session.pop('email',None)
#             session.pop('otp',None)
#             flash('Your password has been reset',category="success")
#             return redirect(url_for('auth.login'))
#          flash('Some error. Please try later. ',category="error")


#    return render_template('forgot.html')
      




@auth.route('/find_donors',methods=['GET','POST'])
@login_required
def find_donors():
    #Specifies the blood and type of donation
    # Check if it is available or not
    
    if request.method=='POST':
        blood_group=request.form.get('blood_group')
        print("Hello",blood_group)
        session['group']=blood_group
        return redirect(url_for('auth.select_type'))
        # people = User.query.filter_by(blood_group=blood_group).all()  # Query matching blood group
        # return render_template('Withblood_group.html', people=people)
    return render_template('Choose_bloodgroup.html')

@auth.route('/select_type',methods=['GET','POST'])
@login_required
def select_type():
   if request.method == 'POST':
        component = request.form.get('blood_component')
        blood_group = session.get('group')  # Get from session
        print("Selected component:", component)
        print("Selected blood group:", blood_group)

        # Check if such a blood group and component exists with amount > 0
        stock = BloodStock.query.filter_by(blood_group=blood_group, category=component).first()
        print(stock.amount)
        
        if stock and stock.amount > 0:
            message = f"{component} is available for blood group {blood_group}."
            return render_template('available.html', 
                       message=message,
                       blood_group=blood_group,
                       blood_component=component)
        else:
            message = f"No {component} available for blood group {blood_group}."
            return render_template(
           'unavailable.html',
            blood_group=blood_group,
            blood_component=component
)


        


   return render_template('Choose_type.html')
   
@auth.route('/show_donors', methods=['GET'])
@login_required
def show_donors():
    blood_group = request.args.get('group')
    people = []

    if blood_group:
        people = User.query.filter_by(blood_group=blood_group).all()

    return render_template('Withblood_group.html', people=people, blood_group=blood_group)



# @auth.route('/message/<int:receiver_id>',methods=['GET','POST'])
# @login_required
# def message(receiver_id):
#     reciever=User.query.get(receiver_id)
#     messages = Messages.query.filter(
#         ((Messages.sender_id == current_user.id) & (Messages.receiver_id == receiver_id)) |
#         ((Messages.sender_id == receiver_id) & (Messages.receiver_id == current_user.id))
#     ).order_by(Messages.timestamp).all()

#     if request.method=='POST':
#         text=request.form['message']
#         new_message=Messages(current_user.id,receiver_id,text)
#         db.session.add(new_message)
#         db.session.commit()
#         return redirect(url_for('auth.message',receiver_id=receiver_id))
#     return render_template('messages.html', receiver=receiver_id, messages=messages, receiver_id=receiver_id)


@auth.route('/message/<int:receiver_id>', methods=['GET', 'POST'])
@login_required
def message(receiver_id):
    receiver = User.query.get(receiver_id)  # Fetch the User object
    
    if not receiver:
        flash("User not found!", "danger")
        return redirect(url_for('auth.chat_history'))
    
    messages = Messages.query.filter(
        ((Messages.sender_id == current_user.id) & (Messages.receiver_id == receiver_id)) |
        ((Messages.sender_id == receiver_id) & (Messages.receiver_id == current_user.id))
    ).order_by(Messages.timestamp).all()

    if request.method == 'POST':
        text = request.form['message']
        new_message = Messages(sender_id=current_user.id, receiver_id=receiver_id, message=text)
        db.session.add(new_message)
        db.session.commit()
        recieve=User.query.get(receiver_id)
        if recieve:
         mail=recieve.email
         send_mail_message(mail)
        return redirect(url_for('auth.message', receiver_id=receiver_id))
    
    
    

    return render_template('messages.html', receiver=receiver, messages=messages)



# @auth.route('/chat-history')
# @login_required
# def chat_history():
#     chat_partners = db.session.query(
#         User.id, User.first_name, db.func.max(Messages.timestamp).label('last_message_time')
#     ).join(
#         Messages, (Messages.sender_id == User.id) | (Messages.receiver_id == User.id)
#     ).filter(
#         (Messages.sender_id == current_user.id) | (Messages.receiver_id == current_user.id)
#     ).group_by(User.id, User.id).order_by(db.func.max(Messages.timestamp).desc()).all()

#     return render_template('chat_history.html', chat_partners=chat_partners)
@auth.route('/chat-history')
@login_required
def chat_history():
    chat_partners = db.session.query(
        User.id, User.first_name, db.func.max(Messages.timestamp).label('last_message_time')
    ).join(
        Messages, (Messages.sender_id == User.id) | (Messages.receiver_id == User.id)
    ).filter(
        (Messages.sender_id == current_user.id) | (Messages.receiver_id == current_user.id),
        User.id != current_user.id  # Exclude the current user
    ).group_by(User.id, User.first_name).order_by(db.func.max(Messages.timestamp).desc()).all()

    return render_template('chat_history.html', chat_partners=chat_partners)

def send_mail(mail_id):
    SMTP_SERVER = "smtp.gmail.com"  # Replace with your SMTP server
    SMTP_PORT = 587  # Use 465 for SSL, 587 for TLS
    EMAIL_ADDRESS = "itsananya.37@gmail.com"  # Sender's email
    EMAIL_PASSWORD = "pxbx mqlu yeqz fjdg"
    msg = EmailMessage()
    user=User.query.filter_by(email=mail_id).first()
    msg["From"] = "Blood donation"  # Custom sender name
    msg["To"] = mail_id  # Receiver's email
    msg["Subject"] = "Welcome to [Your App Name] – A Step Towards Saving Lives!"
    # msg.set_content("")
    user_name=user.first_name
    msg.set_content(f"""\
Dear {user_name},

Thank you for signing up with [Your App Name]! You are now part of a community dedicated to saving lives by connecting blood donors with those in need.

As a registered user, you can:
✔ Find blood donors of a specific blood group
✔ Connect with donors via their contact details
✔ Send and receive messages within the app
✔ Be listed as a potential donor to help save lives

Your willingness to participate can make a huge impact. We encourage you to explore the app and be ready to lend a helping hand whenever needed.

If you have any questions or need assistance, feel free to reach out to our support team.

Together, we can save lives!

Best regards,  
[Your App Name] Team  
[Your Contact Information]
""")

# Send email
    try:
     with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()  # Secure the connection
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
     print(f"Error: {e}")

def send_mail_message(mail_id):
    SMTP_SERVER = "smtp.gmail.com"  # Replace with your SMTP server
    SMTP_PORT = 587  # Use 465 for SSL, 587 for TLS
    EMAIL_ADDRESS = "itsananya.37@gmail.com"  # Sender's email
    EMAIL_PASSWORD = "pxbx mqlu yeqz fjdg"
    msg = EmailMessage()
    user=User.query.filter_by(email=mail_id).first()
    msg["From"] = "Blood donation"  # Custom sender name
    msg["To"] = mail_id  # Receiver's email
    # msg["Subject"] = "Someone needs blood"
    # msg.set_content("")
    msg["Subject"] = "Urgent: You Have a New Blood Request Message"
    user_name=user.first_name
    msg.set_content(f"""\
Dear {user_name},

You have received a new message from someone in need of blood.  

Please check your messages in the [Your App Name] app to view the request and respond if you are available to help. Your generosity could save a life!  

Thank you for being part of our life-saving community.  

Best regards,  
[Your App Name] Team  
[Your Contact Information]
""")

# Send email
    try:
     with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()  # Secure the connection
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
     print(f"Error: {e}")

@auth.route('bot')
def bot():
   return render_template('bot.html')

@auth.route('/pay')
def pay():
    return render_template('pay.html')

