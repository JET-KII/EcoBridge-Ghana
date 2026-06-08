from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import PasswordField, SelectField, SelectMultipleField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

from .models import Profile, User


class RegisterForm(FlaskForm):
    display_name = StringField("Full Name / Company Name", validators=[DataRequired(), Length(max=150)])
    role = SelectField(
        "Registration Type",
        validators=[DataRequired()],
        choices=[
            (User.Role.COLLECTOR.value, "Collector"),
            (User.Role.AGENCY.value, "Recycling Agency"),
        ],
    )
    phone = StringField("Phone", validators=[DataRequired(), Length(max=30)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    region = StringField("Region", validators=[DataRequired(), Length(max=100)])
    city = StringField("City", validators=[DataRequired(), Length(max=100)])
    area = StringField("Area", validators=[DataRequired(), Length(max=100)])
    waste_types = SelectMultipleField("Waste Types", coerce=int, validators=[DataRequired()])
    description = TextAreaField("Short Description", validators=[DataRequired(), Length(min=30, max=1000)])
    image = FileField(
        "Profile Photo / Logo",
        validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp"], "Images only.")],
    )
    submit = SubmitField("Create Account")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class ProfileForm(FlaskForm):
    display_name = StringField("Full Name / Company Name", validators=[DataRequired(), Length(max=150)])
    phone = StringField("Phone", validators=[DataRequired(), Length(max=30)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    region = StringField("Region", validators=[DataRequired(), Length(max=100)])
    city = StringField("City", validators=[DataRequired(), Length(max=100)])
    area = StringField("Area", validators=[DataRequired(), Length(max=100)])
    waste_types = SelectMultipleField("Waste Types", coerce=int, validators=[DataRequired()])
    description = TextAreaField("Short Description", validators=[DataRequired(), Length(min=30, max=1000)])
    status = SelectField(
        "Listing Status",
        validators=[Optional()],
        choices=[
            (Profile.Status.APPROVED.value, "Active"),
            (Profile.Status.SUSPENDED.value, "Suspended"),
        ],
    )
    image = FileField(
        "Profile Photo / Logo",
        validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp"], "Images only.")],
    )
    submit = SubmitField("Save Profile")


class ContactForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField("Phone", validators=[Optional(), Length(max=30)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(min=20, max=2000)])
    submit = SubmitField("Send Message")


class SearchForm(FlaskForm):
    location = StringField("Location", validators=[Optional(), Length(max=100)])
    user_type = SelectField(
        "User Type",
        choices=[
            ("", "All"),
            (User.Role.COLLECTOR.value, "Collectors"),
            (User.Role.AGENCY.value, "Recycling Agencies"),
        ],
        validators=[Optional()],
    )
    waste_type = SelectField("Waste Type", choices=[("", "All waste types")], validators=[Optional()])
    submit = SubmitField("Search")
