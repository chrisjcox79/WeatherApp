from flask import request
from flask_wtf import FlaskForm, RecaptchaField 
from wtforms import Form, StringField, IntegerField, SubmitField 
from wtforms.fields.html5 import EmailField 
from wtforms import TextAreaField 
from wtforms import validators 
from wtforms.validators import DataRequired, InputRequired 


class CreateForm(Form):
    """ Custom form for weather search
    """
    searchCity = StringField('Search for weather forcast of city:', validators=[InputRequired("Please enter the city you want to check weather updates")])
    count = IntegerField("Days")
    submit = SubmitField("Submit")



def getSearchForcastForm(count):
    """ creates a form object and apply formatting.
    """
    form = CreateForm(request.form)
    form.searchCity(style="width: 400px;", class_="form-group glyphicon glyphicon-plus")
    form.count(style="color: blue; font-size: 46px;")
    form.count.default = count
    form.count.label = "Days" if count > 1 else "Day" 
    form.count.data = count
    return form


class MessagingForm(FlaskForm):
    """ Form for messaging app.
    """
    fullName = StringField("Full Name", validators=[InputRequired("Please enter your name")])
    email = EmailField("Email (optional)") #, [validators.Email("Enter valid email address")])
    message = TextAreaField("Message", validators=[InputRequired("Please enter your message")])
    recaptcha = RecaptchaField()

        
        