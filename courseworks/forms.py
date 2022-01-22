from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.fields.datetime import DateField
from wtforms.fields.numeric import FloatField, IntegerField
from wtforms.validators import URL, DataRequired, Length, Email, EqualTo, ValidationError

class LoginForm(FlaskForm):
    username = StringField('User Email',
                           validators=[DataRequired(),
                                       Email(),
                                       ])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    user_email = StringField('User Email',
                           validators=[DataRequired(),
                                       Email(),
                                       ])
    user_first_name = StringField('First Name', validators=[DataRequired()])
    user_last_name = StringField('Last Name', validators=[DataRequired()])
    user_password = PasswordField('Password', validators=[DataRequired()])
    university_id = StringField('University ID')
    university_name = StringField('University Name')
    university_city = StringField('University City')
    university_state = StringField('University State')
    university_address = StringField('University Address')
    university_pincode = IntegerField('University Pincode')
    university_establishment_date = IntegerField('University Establishment Date')
    submit = SubmitField('Register')

class Submit_Assignment(FlaskForm):
    material = StringField('Material/Doc Link',
                           default='Submit Material Link',
                           validators=[DataRequired(), URL()])
    submit = SubmitField('Submit')

class Marks_Assignment(FlaskForm):
    marks = FloatField('Marks Obtained', validators=[DataRequired()])
    submit = SubmitField('Submit')

class Create_Assignment(FlaskForm):
    assignment_name = StringField('Assignment Name', validators=[DataRequired()])
    total_marks = FloatField('Total Marks', validators=[DataRequired()])
    assignment_posted_date = DateField('Post Date', validators=[DataRequired()])
    assignment_due_date = DateField('Due Date', validators=[DataRequired()])
    submit = SubmitField('Submit')
