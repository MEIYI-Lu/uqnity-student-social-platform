from datetime import datetime
from uqnity_app import db, login_manager
from flask_login import UserMixin
from sqlalchemy import CheckConstraint

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --------------------------
# User model
# --------------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    program = db.Column(db.String(100), nullable=True)
    campus = db.Column(db.String(100), nullable=True)
    interests = db.Column(db.String(200), nullable=True)

    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


# --------------------------
# Post model
# --------------------------
from datetime import datetime
from uqnity_app import db

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(120), nullable=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # ✅ 新增
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)




# --------------------------
# Event Organizer, Event, Registration, Review, Purchase models
# --------------------------
class EventOrganizer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    profile_image = db.Column(db.String(100), nullable=True, default='default_org.jpg')
    rating = db.Column(db.Float, default=0.0)
    description = db.Column(db.Text)
    events = db.relationship('Event', backref='organizer', lazy=True)

    def __repr__(self):
        return f"EventOrganizer('{self.name}', Rating={self.rating})"


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    banner_image = db.Column(db.String(100), nullable=True, default='default_event.jpg')
    details = db.Column(db.Text, nullable=False)
    reasons_to_attend = db.Column(db.JSON, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    tags = db.Column(db.JSON, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.Integer, nullable=True)
    dress_code = db.Column(db.String(100), nullable=True)
    age_requirement = db.Column(db.String(100), nullable=True)
    parking = db.Column(db.String(100), nullable=True)
    registration_required = db.Column(db.Boolean, default=False)
    expected_attendance = db.Column(db.Integer, nullable=True)
    rating = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    organizer_id = db.Column(db.Integer, db.ForeignKey('event_organizer.id'), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "category IN ('Music', 'Technology', 'Food', 'Arts', 'Fitness', 'Literature', 'Culture', 'Entertainment', "
            "'Academic & Professional Development', 'Social Events', 'Sports & Recreation', 'Community Engagement', "
            "'Networking', 'Workshops & Training', 'Diversity & Inclusion', 'Sustainability & Environment', "
            "'Health & Well-being', 'Tech & Innovation', 'Entrepreneurship & Startups', 'Festivals & Celebrations')",
            name='check_category_valid'
        ),
    )

    def __repr__(self):
        return f"Event('{self.name}', Date={self.date}, Organizer={self.organizer_id}, Category={self.category})"


class EventRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User', backref=db.backref('registrations', lazy=True))
    event = db.relationship('Event', backref=db.backref('registrations', lazy=True))

    def __repr__(self):
        return f"EventRegistration(User={self.user_id}, Event={self.event_id}, Date={self.registration_date})"


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('event_organizer.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_rating = db.Column(db.Integer, nullable=False)
    organizer_rating = db.Column(db.Integer, nullable=False)
    event_comment = db.Column(db.Text, nullable=True)
    organizer_comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    event = db.relationship('Event', backref=db.backref('reviews', lazy=True), foreign_keys=[event_id])
    organizer = db.relationship('EventOrganizer', backref=db.backref('reviews', lazy=True), foreign_keys=[organizer_id])
    user = db.relationship('User', backref=db.backref('reviews', lazy=True))

    def __repr__(self):
        return f"Review(User={self.user_id}, EventRating={self.event_rating}, OrganizerRating={self.organizer_rating})"


class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.String(50), nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Purchase {self.game_id} by user {self.user_id}>'
