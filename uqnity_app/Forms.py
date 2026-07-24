from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField, 
    TextAreaField, RadioField, HiddenField, IntegerField, SelectField
)
from wtforms.validators import (
    DataRequired, Length, Email, EqualTo, ValidationError, 
    NumberRange, Optional
)
from uqnity_app.Models import User


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        """Check if username already exists"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        """Check if email already exists"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is registered. Please login instead.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ReviewForm(FlaskForm):
    # Event review fields
    event_rating = RadioField(
        'Event Rating',
        choices=[(5, '5'), (4, '4'), (3, '3'), (2, '2'), (1, '1')],
        coerce=int,
        validators=[DataRequired(message="Please select an event rating")]
    )

    event_comment = TextAreaField(
        'Event Comment',
        validators=[
            DataRequired(),
            Length(min=10, max=1000, message="Event comment must be between 10 and 1000 characters")
        ]
    )

    # Organizer review fields
    organizer_rating = RadioField(
        'Organizer Rating',
        choices=[(5, '5'), (4, '4'), (3, '3'), (2, '2'), (1, '1')],
        coerce=int,
        validators=[DataRequired(message="Please select an organizer rating")]
    )

    organizer_comment = TextAreaField(
        'Organizer Comment',
        validators=[
            DataRequired(),
            Length(min=10, max=1000, message="Organizer comment must be between 10 and 1000 characters")
        ]
    )

    current_step = HiddenField('Current Step', validators=[Optional()])
    submit = SubmitField('Submit Reviews')

    def validate_event_comment(self, event_comment):
        """Filter inappropriate words from event comment"""
        banned_words = ['hate', 'stupid', 'idiot']
        for word in banned_words:
            if word.lower() in event_comment.data.lower():
                raise ValidationError('Please keep your review constructive and appropriate.')

    def validate_organizer_comment(self, organizer_comment):
        """Filter inappropriate words from organizer comment"""
        banned_words = ['hate', 'stupid', 'idiot']
        for word in banned_words:
            if word.lower() in organizer_comment.data.lower():
                raise ValidationError('Please keep your review constructive and appropriate.')


class FeedbackForm(FlaskForm):
    """User Feedback and Support Form for Help & Support page"""
    
    rating = IntegerField(
        'App Rating (1-5)',
        validators=[Optional(), NumberRange(min=1, max=5, message='Rating must be between 1 and 5.')]
    )
    
    appreciate = TextAreaField(
        'What do you appreciate most about our app?',
        validators=[Optional(), Length(max=500, message='Maximum 500 characters allowed.')]
    )
    
    improve = TextAreaField(
        'How can we improve the app?',
        validators=[Optional(), Length(max=500, message='Maximum 500 characters allowed.')]
    )
    
    comments = TextAreaField(
        'Your further comments',
        validators=[Optional(), Length(max=500, message='Maximum 500 characters allowed.')]
    )
    
    submit = SubmitField('Submit Feedback')


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    image = FileField("Upload Image (Optional)")
    submit = SubmitField("Post")


class SettingsForm(FlaskForm):
    # Personal Info
    full_name = StringField("Full Name", validators=[DataRequired()])
    email = StringField("Email Address", validators=[Email()])
    phone_number = StringField("Phone Number")
    account_type = SelectField("Account Type", choices=[("Student","Student"),("Staff","Staff")])
    avatar = FileField("Change Avatar")

    # Bio
    bio_description = TextAreaField("Bio Description", validators=[Optional()])

    # Notifications
    new_match = BooleanField("New Match Found")
    study_match = BooleanField("Study Match Found")
    events_suggestion = BooleanField("Events Suggestion")
    events_reminder = BooleanField("Events Reminder")
    events_update = BooleanField("Events Updates")
    messages = BooleanField("Messages")

    # Social Links
    facebook = StringField("Facebook")
    instagram = StringField("Instagram")
    discord = StringField("Discord")

    # Academic
    program = StringField("Program")
    campus = StringField("Campus")
    file_upload = FileField("File Upload")

    # Matching
    matching_details = TextAreaField("Matching Details")

    submit = SubmitField("Save")