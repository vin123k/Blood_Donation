from flask import render_template,Blueprint,request
from .models import User

views=Blueprint('views',__name__)

@views.route('/',methods=['GET','POST'])
def func():
    return render_template('home1.html')

