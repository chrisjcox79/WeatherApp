from flask import request
from wtforms import Form, StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, InputRequired


class CreateForm(Form):
    """ Custom form
    """
    searchCity = StringField('View forcast of city:', validators=[InputRequired("Please enter the city you want to check weather updates")])
    count = IntegerField("Days")
    submit = SubmitField("Submit")



def getSearchForcastForm(count):
    """ creates a form object and apply formatting.
    """
    form = CreateForm(request.form)
    form.searchCity(style="width: 400px;", class_="form-group")
    form.count(style="color: blue; font-size: 46px;")
    form.count.default = count
    form.count.label = "Days" if count > 1 else "Day" 
    form.count.data = count
    return form