from datetime import datetime, timedelta
import os
import secrets
import random
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, jsonify, Blueprint
from sqlalchemy import or_, func
from uqnity_app.Forms import RegistrationForm, LoginForm, ReviewForm, PostForm, SettingsForm, FeedbackForm
from uqnity_app.Models import User, Event, EventOrganizer, Review, EventRegistration, Purchase, Post
from flask_login import login_user, current_user, logout_user, login_required

# 蓝图定义
main = Blueprint('main', __name__)

user_unlocked_games = {}
rapid_fire_sessions = {}

# 游戏配置 (保持不变)
PREMIUM_GAMES = {
    'never-have-i-ever': {
        'name': 'Never Have I Ever',
        'price': 2.99,
        'icon': '🙈',
        'questions': [
            "Never have I ever traveled to another continent",
            "Never have I ever broken a bone",
            "Never have I ever gone skydiving",
            "Never have I ever sung karaoke in public",
            "Never have I ever stayed up all night"
        ]
    },
    'caption-this': {
        'name': 'Caption This',
        'price': 2.99,
        'icon': '💬',
        'scenarios': [
            {'image': '🐱', 'text': 'A cat sitting at a computer looking very serious'},
            {'image': '🦒', 'text': 'A giraffe trying to hide behind a tiny tree'},
            {'image': '🐧', 'text': 'A penguin wearing sunglasses on a beach'}
        ]
    },
    'rapid-fire': {
        'name': 'Rapid Fire',
        'price': 2.99,
        'icon': '⚡',
        'questions': [
            "Coffee or tea?",
            "Morning person or night owl?",
            "Beach or mountains?"
        ]
    }
}

RAPID_FIRE_QUESTIONS = [
    {"question": "Coffee or tea?", "category": "Preferences"},
    {"question": "Morning person or night owl?", "category": "Lifestyle"},
    {"question": "Beach or mountains?", "category": "Travel"},
    {"question": "Cats or dogs?", "category": "Pets"},
    {"question": "Sweet or savory?", "category": "Food"},
    {"question": "Summer or winter?", "category": "Seasons"},
    {"question": "Books or movies?", "category": "Entertainment"},
    {"question": "Texting or calling?", "category": "Communication"},
    {"question": "Early bird or night owl?", "category": "Habits"},
    {"question": "City or countryside?", "category": "Lifestyle"},
    {"question": "Pizza or pasta?", "category": "Food"},
    {"question": "Netflix or YouTube?", "category": "Entertainment"},
    {"question": "Cooking or ordering in?", "category": "Food"},
    {"question": "Gym or outdoor exercise?", "category": "Fitness"},
    {"question": "Plan ahead or spontaneous?", "category": "Personality"},
    {"question": "Introvert or extrovert?", "category": "Personality"},
    {"question": "Music or podcasts?", "category": "Audio"},
    {"question": "Shower or bath?", "category": "Lifestyle"},
    {"question": "Drive or fly?", "category": "Travel"},
    {"question": "Online shopping or in-store?", "category": "Shopping"}
]


def page_not_found(e):
    return render_template('404.html'), 404


@main.route("/")
@main.route("/home")
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('main.login'))

    suggested_users = (
        User.query
        .filter(User.id != current_user.id)
        .limit(3)
        .all()
    )

    return render_template(
        'home.html',
        title='Home',
        suggested_users=suggested_users
    )


@main.route("/register", methods=['GET', 'POST'])
def register():
    # 导入 db 和 bcrypt 到函数内部
    from uqnity_app import db, bcrypt 
    
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, 
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You are now able to log in.", 'success')
        return redirect(url_for('main.login'))
    return render_template("register.html", title='Register', form=form)


@main.route("/login", methods=['GET', 'POST'])
def login():
    # 导入 bcrypt 到函数内部
    from uqnity_app import bcrypt 
    
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash("Login unsuccessful. Please check username and password", 'danger')
    return render_template("login.html", title="Login", form=form)


@main.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


@main.route('/game_menu')
def game_menu():
    return render_template('gameLobby.html')


@main.route('/two_truths_game')
def two_truths_game():
    return render_template('twoTruthsOneLie.html')


@main.route('/would-you-rather')
def would_you_rather():
    return render_template('would_you_rather.html')


@main.route('/story-building')
def story_building():
    return render_template('storyBuilding.html')


@main.route('/game_profile')
@login_required
def game_profile():
    return render_template('userGamingProfile.html')


@main.route('/games/never-have-i-ever')
@login_required
def premium_never_have_i_ever():
    user = {
        'name': current_user.username,
        'avatar': getattr(current_user, 'avatar', '👤')
    }
    return render_template('games/neverHaveIever.html', user=user)


@main.route('/games/rapid-fire')
@login_required
def premium_rapid_fire():
    user = {
        'name': current_user.username,
        'avatar': getattr(current_user, 'avatar', '⚡')
    }
    return render_template('games/rapid_fire.html', user=user)


@main.route('/games/caption-this')
@login_required
def premium_caption_this():
    user = {
        'name': current_user.username,
        'avatar': getattr(current_user, 'avatar', '📸')
    }
    return render_template('games/caption_this.html', user=user)


@main.route('/api/unlocked-games')
@login_required
def api_get_unlocked_games():
    user_id = current_user.id
    unlocked = user_unlocked_games.get(user_id, [])
    return jsonify({'unlockedGames': unlocked})


@main.route('/api/purchase', methods=['POST'])
@login_required
def api_purchase_premium_game():
    try:
        data = request.get_json()
        game_id = data.get('game_id')
        
        if not game_id:
            return jsonify({'error': 'No game_id provided'}), 400
        
        if game_id not in PREMIUM_GAMES:
            return jsonify({'error': 'Invalid game'}), 400
        
        user_id = current_user.id
        
        if user_id not in user_unlocked_games:
            user_unlocked_games[user_id] = []
        
        if game_id in user_unlocked_games[user_id]:
            return jsonify({'error': 'Already purchased'}), 400
        
        user_unlocked_games[user_id].append(game_id)
        
        return jsonify({
            'success': True, 
            'message': 'Game unlocked! (Demo - stored in memory)'
        })
        
    except Exception as e:
        print(f"Error in purchase: {e}")
        return jsonify({'error': str(e)}), 500


@main.route('/api/game/<game_id>/content')
@login_required
def api_get_game_content(game_id):
    try:
        user_id = current_user.id
        
        if game_id in PREMIUM_GAMES:
            unlocked = user_unlocked_games.get(user_id, [])
            if game_id not in unlocked:
                return jsonify({'error': 'Game not unlocked'}), 403
        
        if game_id not in PREMIUM_GAMES:
            return jsonify({'error': 'Invalid game'}), 404
        
        return jsonify(PREMIUM_GAMES[game_id])
        
    except Exception as e:
        print(f"Error getting game content: {e}")
        return jsonify({'error': str(e)}), 500


@main.route('/api/rapid-fire/start', methods=['POST'])
@login_required
def rapid_fire_start():
    try:
        data = request.get_json()
        player_count = data.get('playerCount', 4)
        questions_per_round = data.get('questionsPerRound', 5)
        time_limit = data.get('timeLimit', 10)
        
        selected_questions = random.sample(RAPID_FIRE_QUESTIONS, min(questions_per_round, len(RAPID_FIRE_QUESTIONS)))
        
        mock_player_names = ['Sarah', 'Mike', 'Emma', 'Jake', 'Lily', 'Tom', 'Zoe']
        players = [current_user.username] + mock_player_names[:player_count - 1]
        scores = {name: 0 for name in players}
        
        session_id = f"{current_user.id}_{datetime.utcnow().timestamp()}"
        rapid_fire_sessions[session_id] = {
            'questions': selected_questions,
            'scores': scores,
            'current_question': 0,
            'players': players
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'questions': selected_questions,
            'scores': scores
        })
        
    except Exception as e:
        print(f"Error starting Rapid Fire: {e}")
        return jsonify({'error': str(e)}), 500


@main.route('/api/rapid-fire/submit', methods=['POST'])
@login_required
def rapid_fire_submit():
    try:
        data = request.get_json()
        user_answer = data.get('answer', '')
        time_to_answer = data.get('timeToAnswer', 10)
        
        player_avatars = {
            current_user.username: '⚡',
            'Sarah': '🌟',
            'Mike': '🎯',
            'Emma': '🎨',
            'Jake': '⚡',
            'Lily': '🌸',
            'Tom': '🎪',
            'Zoe': '🦋'
        }
        
        mock_answers_list = [
            "Definitely!",
            "Not really",
            "Sometimes",
            "Absolutely!",
            "It depends",
            "For sure",
            "Maybe",
            "Of course!"
        ]
        
        answers = [{
            'playerName': current_user.username,
            'avatar': player_avatars.get(current_user.username, '👤'),
            'answer': user_answer if user_answer else "No answer",
            'timeToAnswer': time_to_answer
        }]
        
        num_other_players = random.randint(3, 5)
        other_players = ['Sarah', 'Mike', 'Emma', 'Jake', 'Lily'][:num_other_players]
        
        for player in other_players:
            answers.append({
                'playerName': player,
                'avatar': player_avatars.get(player, '😊'),
                'answer': random.choice(mock_answers_list),
                'timeToAnswer': random.randint(3, 12)
            })
        
        scores = {}
        for answer in answers:
            score = max(0, 100 - (answer['timeToAnswer'] * 5))
            scores[answer['playerName']] = scores.get(answer['playerName'], 0) + score
        
        return jsonify({
            'success': True,
            'answers': answers,
            'scores': scores
        })
        
    except Exception as e:
        print(f"Error submitting Rapid Fire answer: {e}")
        return jsonify({'error': str(e)}), 500


@main.route('/demo/unlock-all')
@login_required
def demo_unlock_all():
    user_id = current_user.id
    user_unlocked_games[user_id] = list(PREMIUM_GAMES.keys())
    flash('All games unlocked! (Demo Mode)', 'success')
    return redirect(url_for('main.game_menu'))


@main.route('/demo/quick-unlock/<game_id>')
@login_required
def demo_quick_unlock(game_id):
    user_id = current_user.id
    if user_id not in user_unlocked_games:
        user_unlocked_games[user_id] = []
    if game_id not in user_unlocked_games[user_id]:
        user_unlocked_games[user_id].append(game_id)
    return jsonify({'success': True, 'unlocked': user_unlocked_games[user_id]})


@main.route('/all_events')
def all_events():
    search_query = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()
    sort_by = request.args.get('sort', 'date')
    page = request.args.get('page', 1, type=int)
    per_page = 6
    
    query = Event.query.filter(Event.date >= datetime.now())
    
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                Event.name.ilike(search_pattern),
                Event.location.ilike(search_pattern),
                Event.details.ilike(search_pattern),
                Event.tags.ilike(search_pattern)
            )
        )
    
    if category_filter:
        query = query.filter(Event.category.ilike(f"%{category_filter}%"))
    
    if sort_by == 'date':
        query = query.order_by(Event.date.asc())
    elif sort_by == 'name':
        query = query.order_by(Event.name.asc())
    elif sort_by == 'popularity':
        query = query.order_by(Event.expected_attendance.desc())
    elif sort_by == 'rating':
        query = query.join(EventOrganizer).order_by(EventOrganizer.rating.desc())
    else:
        query = query.order_by(Event.date.asc())
    
    total_events = query.count()
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    events = pagination.items
    
    featured_events_query = Event.query.filter(Event.date >= datetime.now())
    
    if search_query:
        featured_events_query = featured_events_query.filter(
            or_(
                Event.name.ilike(search_pattern),
                Event.location.ilike(search_pattern),
                Event.details.ilike(search_pattern),
                Event.tags.ilike(search_pattern)
            )
        )

    if category_filter:
        featured_events_query = featured_events_query.filter(Event.category.ilike(f"%{category_filter}%"))

    featured_events = featured_events_query.order_by(Event.date.asc()).limit(5).all()
    
    for event in events:
        user = current_user
        event.is_registered = EventRegistration.query.filter_by(event_id=event.id, user_id=user.id).first() is not None
    
    return render_template(
        'all_events.html',
        title='All Events',
        events=events,
        total_events=total_events,
        featured_events=featured_events,
        pagination=pagination
    )


def get_related_events(current_event, limit=3):
    related_events = Event.query.filter(
        Event.id != current_event.id,
        Event.date >= datetime.now(),
        or_(*[Event.tags.like(f'%{tag}%') for tag in current_event.tags])
    ).limit(limit).all()
    
    related_event_ids = [event.id for event in related_events]
    
    while len(related_events) < 3:
        nearest_events = Event.query.filter(
            Event.date > datetime.now(), 
            Event.id != current_event.id,
            Event.id.notin_(related_event_ids)
        ).order_by(Event.date).limit(limit - len(related_events)).all()
        
        for event in nearest_events:
            if event.id not in related_event_ids:
                related_events.append(event)
                related_event_ids.append(event.id)

    for event in related_events:
        user = current_user
        event.is_registered = EventRegistration.query.filter_by(event_id=event.id, user_id=user.id).first() is not None

    return related_events


@main.route('/events/<int:event_id>')
def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    user = current_user
    is_registered = EventRegistration.query.filter_by(event_id=event.id, user_id=user.id).first() is not None
    
    event_reviews = Review.query.filter_by(event_id=event_id).all()
    organizer_reviews = Review.query.filter_by(organizer_id=event.organizer_id).all()
    
    event_review_count = len(event_reviews)
    organizer_review_count = len(organizer_reviews)
    
    related_events = get_related_events(event)
    
    return render_template('event_details.html', title=event.name, 
                           event=event, timedelta=timedelta, 
                           is_registered=is_registered, related_events=related_events, 
                           event_reviews=event_reviews, organizer_reviews=organizer_reviews,
                           event_review_count=event_review_count, organizer_review_count=organizer_review_count)


@main.route('/register_event/<int:event_id>/<int:user_id>', methods=['GET', 'POST'])
@login_required
def register_event(event_id, user_id):
    # 导入 db 到函数内部
    from uqnity_app import db 
    
    event = Event.query.get(event_id)
    user = User.query.get(user_id)

    if not event:
        return jsonify(success=False, message="Event not found"), 400

    if not user:
        return jsonify(success=False, message="User not found"), 400

    existing_registration = EventRegistration.query.filter_by(event_id=event.id, user_id=user.id).first()
    if existing_registration:
        return jsonify(success=False, message="You are already registered for this event."), 400

    registration = EventRegistration(event_id=event.id, user_id=user.id)
    db.session.add(registration)
    db.session.commit()

    return jsonify(success=True, message=f"You have successfully registered for the {event.name}!"), 200


@main.route("/my_reviews")
@login_required
def my_reviews():
    # 导入 db 到函数内部
    from uqnity_app import db 

    my_reviews = Review.query.filter_by(user_id=current_user.id)\
                             .join(Event, Review.event_id == Event.id)\
                             .join(EventOrganizer, Review.organizer_id == EventOrganizer.id)\
                             .order_by(Review.created_at.desc()).all()
    
    registered_events = db.session.query(Event).join(EventRegistration)\
                                   .filter(EventRegistration.user_id == current_user.id)\
                                   .filter(Event.date < datetime.now()).all()
    
    reviewed_event_ids = [r.event_id for r in my_reviews if r.event_id]
    events_to_review = [e for e in registered_events if e.id not in reviewed_event_ids]
    
    return render_template('my_reviews.html', 
                         title='My Reviews',
                         my_reviews=my_reviews,
                         events_to_review=events_to_review)


@main.route("/event/<int:event_id>/review", methods=['GET', 'POST'])
@login_required
def submit_review(event_id):
    # 导入 db 到函数内部
    from uqnity_app import db 

    event = Event.query.get_or_404(event_id)
    
    existing_registration = EventRegistration.query.filter_by(
        user_id=current_user.id,
        event_id=event_id,
    ).first()

    if not existing_registration:
        flash('You must be registered for this event to submit a review.', 'warning')
        return redirect(url_for('main.event_details', event_id=event_id))

    existing_review = Review.query.filter_by(
        user_id=current_user.id,
        event_id=event_id,
    ).first()
    
    if existing_review:
        flash('You have already reviewed this event!', 'info')
        return redirect(url_for('main.my_reviews'))
    
    form = ReviewForm()
    
    if form.validate_on_submit():
        event_rating = form.event_rating.data
        event_comment = form.event_comment.data.strip()
        organizer_rating = form.organizer_rating.data
        organizer_comment = form.organizer_comment.data.strip()
        
        try:
            review = Review(
                event_id=event_id,
                organizer_id=event.organizer_id,
                user_id=current_user.id,
                event_rating=event_rating,
                organizer_rating=organizer_rating,
                event_comment=event_comment,
                organizer_comment=organizer_comment
            )
            db.session.add(review)
            db.session.commit()
            
            update_ratings(event_id=event_id, organizer_id=event.organizer_id)
            
            flash('Your reviews have been submitted successfully!', 'success')
            return redirect(url_for('main.my_reviews'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error saving review: {e}")
            flash('An error occurred while submitting your reviews. Please try again.', 'danger')
    
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", 'danger')
    
    return render_template('review.html', title='Submit Review', form=form, event=event)


@main.route("/review/<int:review_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    # 导入 db 到函数内部
    from uqnity_app import db 

    review = Review.query.get_or_404(review_id)
    
    if review.user_id != current_user.id:
        flash('You do not have permission to edit this review.', 'danger')
        return redirect(url_for('main.my_reviews'))
    
    form = ReviewForm()
    
    if form.validate_on_submit():
        review.event_rating = form.event_rating.data
        review.event_comment = form.event_comment.data.strip()
        review.organizer_rating = form.organizer_rating.data
        review.organizer_comment = form.organizer_comment.data.strip()
        
        try:
            db.session.commit()
            update_ratings(event_id=review.event_id, organizer_id=review.organizer_id)
            
            flash('Your review has been updated!', 'success')
            return redirect(url_for('main.my_reviews'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating review: {e}")
            flash('An error occurred while updating your review.', 'danger')
    
    elif request.method == 'GET':
        form.event_rating.data = review.event_rating
        form.event_comment.data = review.event_comment
        form.organizer_rating.data = review.organizer_rating
        form.organizer_comment.data = review.organizer_comment
        
    event = review.event
    
    return render_template('review.html', 
                         title='Edit Review', 
                         form=form, 
                         event=event, 
                         review=review,
                         is_edit=True)


@main.route("/review/<int:review_id>/delete", methods=['POST'])
@login_required
def delete_review(review_id):
    # 导入 db 到函数内部
    from uqnity_app import db 

    review = Review.query.get_or_404(review_id)
    
    if review.user_id != current_user.id:
        flash('You do not have permission to delete this review.', 'danger')
        return redirect(url_for('main.my_reviews'))
    
    event_id = review.event_id
    organizer_id = review.organizer_id
    
    db.session.delete(review)
    db.session.commit()
    
    update_ratings(event_id=event_id, organizer_id=organizer_id)
    
    flash('Your review has been deleted.', 'success')
    return redirect(url_for('main.my_reviews'))


def update_ratings(event_id=None, organizer_id=None):
    # 导入 db 到函数内部
    from uqnity_app import db 
    
    try:
        if event_id:
            event_avg_rating = db.session.query(func.avg(Review.event_rating))\
                                    .filter(Review.event_id == event_id)\
                                    .scalar()
            
            event = Event.query.get(event_id)
            if event:
                event.event_rating = round(float(event_avg_rating), 2) if event_avg_rating else 0.0
        
        if organizer_id:
            organizer_avg_rating = db.session.query(func.avg(Review.organizer_rating))\
                                    .filter(Review.organizer_id == organizer_id)\
                                    .scalar()
            
            organizer = EventOrganizer.query.get(organizer_id)
            if organizer:
                organizer.rating = round(float(organizer_avg_rating), 2) if organizer_avg_rating else 0.0
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating ratings: {e}")


CAPTION_THIS_IMAGES = [
    {"url": "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=800", "category": "Animals"},
    {"url": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=800", "category": "Cats"},
    {"url": "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=800", "category": "Dogs"},
    {"url": "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=800", "category": "Cute"},
    {"url": "https://images.unsplash.com/photo-1425082661705-1834bfd09dca?w=800", "category": "Nature"},
    {"url": "https://images.unsplash.com/photo-1529778873920-4da4926a72c2?w=800", "category": "Cats"},
    {"url": "https://images.unsplash.com/photo-1517849845537-4d257902454a?w=800", "category": "Dogs"},
    {"url": "https://images.unsplash.com/photo-1526336024174-e58f5cdd8e13?w=800", "category": "Animals"},
    {"url": "https://images.unsplash.com/photo-1503066211613-c17ebc9daef0?w=800", "category": "Funny"},
    {"url": "https://images.unsplash.com/photo-1415369629372-26f2fe60c467?w=800", "category": "Random"}
]

caption_this_sessions = {}
used_images = []

@main.route('/api/caption-this/start', methods=['POST'])
@login_required
def caption_this_start():
    try:
        data = request.get_json()
        player_count = data.get('playerCount', 4)
        rounds_total = data.get('roundsTotal', 5)
        
        mock_player_names = ['Sarah', 'Mike', 'Emma', 'Jake', 'Lily', 'Tom', 'Zoe']
        players = [current_user.username] + mock_player_names[:player_count - 1]
        scores = {name: 0 for name in players}
        
        session_id = f"{current_user.id}_{datetime.utcnow().timestamp()}"
        caption_this_sessions[session_id] = {
            'scores': scores,
            'current_round': 0,
            'rounds_total': rounds_total,
            'players': players,
            'used_images': []
        }
        
        global used_images
        used_images = []
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'scores': scores
        })
        
    except Exception as e:
        print(f"Error starting Caption This: {e}")
        return jsonify({'error': str(e)}), 500


@main.route('/api/caption-this/next-image')
@login_required
def caption_this_next_image():
    try:
        global used_images
        
        available_images = [img for img in CAPTION_THIS_IMAGES if img['url'] not in used_images]
        
        if not available_images:
            used_images = []
            available_images = CAPTION_THIS_IMAGES
        
        selected_image = random.choice(available_images)
        used_images.append(selected_image['url'])
        
        return jsonify(selected_image)
        
    except Exception as e:
        print(f"Error getting next image: {e}")
        return jsonify({'error': str(e)}), 500


@main.route('/api/caption-this/submit-caption', methods=['POST'])
@login_required
def caption_this_submit_caption():
    try:
        data = request.get_json()
        user_caption = data.get('caption', '')
        player_count = data.get('playerCount', 4)
        
        player_avatars = {
            current_user.username: '📸',
            'Sarah': '🌟',
            'Mike': '🎯',
            'Emma': '🎨',
            'Jake': '⚡',
            'Lily': '🌸',
            'Tom': '🎪',
            'Zoe': '🦋'
        }
        
        mock_captions_list = [
            "When you realize it's Monday tomorrow",
            "Me trying to look professional in Zoom meetings",
            "That moment when you find the snacks",
            "Living my best life",
            "This is fine... everything is fine",
            "Mood: Unbothered",
            "POV: You're fabulous",
            "Just another day of being awesome",
            "Plot twist: I'm actually enjoying this",
            "When life gives you lemons...",
            "Main character energy",
            "No thoughts, head empty"
        ]
        
        captions = [{
            'playerName': current_user.username,
            'avatar': player_avatars.get(current_user.username, '👤'),
            'caption': user_caption,
            'votes': 0
        }]
        
        num_other_players = player_count - 1
        other_players = ['Sarah', 'Mike', 'Emma', 'Jake', 'Lily', 'Tom', 'Zoe'][:num_other_players]
        
        used_captions = []
        for player in other_players:
            available_captions = [c for c in mock_captions_list if c not in used_captions]
            selected_caption = random.choice(available_captions)
            used_captions.append(selected_caption)
            
            captions.append({
                'playerName': player,
                'avatar': player_avatars.get(player, '😊'),
                'caption': selected_caption,
                'votes': 0
            })
        
        random.shuffle(captions)
        
        return jsonify({
            'success': True,
            'captions': captions
        })
        
    except Exception as e:
        print(f"Error submitting caption: {e}")
        return jsonify({'error': str(e)}), 500


@main.route('/api/caption-this/submit-vote', methods=['POST'])
@login_required
def caption_this_submit_vote():
    try:
        data = request.get_json()
        voted_caption = data.get('caption', '')
        captions_list = data.get('captions', [])
        current_scores = data.get('currentScores', {})
        
        for caption_obj in captions_list:
            if caption_obj['caption'] == voted_caption:
                caption_obj['votes'] = random.randint(2, 4)
            else:
                caption_obj['votes'] = random.randint(0, 2)
        
        for caption_obj in captions_list:
            player_name = caption_obj['playerName']
            points = caption_obj['votes'] * 10
            current_scores[player_name] = current_scores.get(player_name, 0) + points
        
        return jsonify({
            'success': True,
            'captions': captions_list,
            'scores': current_scores
        })
        
    except Exception as e:
        print(f"Error submitting vote: {e}")
        return jsonify({'error': str(e)}), 500


NEVER_HAVE_STATEMENTS = [
    {"statement": "traveled to another continent", "category": "Travel"},
    {"statement": "broken a bone", "category": "Personal"},
    {"statement": "gone skydiving", "category": "Adventure"},
    {"statement": "sung karaoke in public", "category": "Entertainment"},
    {"statement": "stayed up all night", "category": "Lifestyle"},
    {"statement": "met a celebrity", "category": "Experience"},
    {"statement": "been on TV", "category": "Fame"},
    {"statement": "learned a musical instrument", "category": "Skills"},
    {"statement": "been camping", "category": "Outdoors"},
    {"statement": "eaten sushi", "category": "Food"},
    {"statement": "ridden a motorcycle", "category": "Adventure"},
    {"statement": "dyed my hair", "category": "Personal"},
    {"statement": "been in a hot air balloon", "category": "Travel"},
    {"statement": "written a poem", "category": "Creative"},
    {"statement": "been to a music festival", "category": "Entertainment"}
]

never_have_sessions = {}
never_have_used_statements = []

@main.route('/api/never-have/start', methods=['POST'])
@login_required
def never_have_start():
    try:
        data = request.get_json()
        player_count = data.get('playerCount', 4)
        rounds_total = data.get('roundsTotal', 7)
        
        session_id = f"{current_user.id}_{datetime.utcnow().timestamp()}"
        never_have_sessions[session_id] = {
            'player_count': player_count,
            'rounds_total': rounds_total,
            'current_round': 0,
            'all_results': []
        }
        
        global never_have_used_statements
        never_have_used_statements = []
        
        return jsonify({'success': True, 'session_id': session_id})
        
    except Exception as e:
        print(f"Error starting Never Have I Ever: {e}")
        return jsonify({'error': str(e)}), 500


@main.route('/api/never-have/next-round')
@login_required
def never_have_next_round():
    try:
        global never_have_used_statements
        
        available = [s for s in NEVER_HAVE_STATEMENTS if s['statement'] not in never_have_used_statements]
        
        if not available:
            never_have_used_statements = []
            available = NEVER_HAVE_STATEMENTS
        
        selected = random.choice(available)
        never_have_used_statements.append(selected['statement'])
        
        return jsonify(selected)
        
    except Exception as e:
        print(f"Error getting next round: {e}")
        return jsonify({'error': str(e)}), 500


@main.route('/api/never-have/submit', methods=['POST'])
@login_required
def never_have_submit():
    try:
        data = request.get_json()
        have_done = data.get('haveDone', False)
        statement = data.get('statement', {})
        session_id = data.get('session_id')
        
        session = never_have_sessions.get(session_id, {
            'current_round': 0,
            'all_results': []
        })
        
        player_avatars = {
            current_user.username: '🙈',
            'Sarah': '🌟',
            'Mike': '🎯',
            'Emma': '🎨',
            'Jake': '⚡',
            'Lily': '🌸',
            'Tom': '🎪',
            'Zoe': '🦋'
        }
        
        responses = [{
            'playerName': current_user.username,
            'avatar': player_avatars.get(current_user.username, '👤'),
            'haveDone': have_done
        }]
        
        other_players = ['Sarah', 'Mike', 'Emma', 'Jake', 'Lily', 'Tom', 'Zoe'][:random.randint(3, 5)]
        
        for player in other_players:
            responses.append({
                'playerName': player,
                'avatar': player_avatars.get(player, '😊'),
                'haveDone': random.choice([True, False])
            })
        
        session['current_round'] += 1
        
        session['all_results'].append({
            'statement': statement,
            'responses': responses
        })
        
        if session_id:
            never_have_sessions[session_id] = session
        
        return jsonify({
            'success': True,
            'responses': responses,
            'currentRound': session['current_round']
        })
        
    except Exception as e:
        print(f"Error submitting response: {e}")
        return jsonify({'error': str(e)}), 500


@main.route('/api/never-have/final-scores')
@login_required
def never_have_final_scores():
    try:
        players = ['Sarah', 'Mike', 'Emma', current_user.username]
        scores = {name: random.randint(50, 150) for name in players}
        
        return jsonify({
            'scores': scores,
            'allRoundResults': []
        })
        
    except Exception as e:
        print(f"Error getting final scores: {e}")
        return jsonify({'error': str(e)}), 500


@main.route("/posts", methods=["GET"])
def posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("posts.html", posts=posts)


@main.route("/posts/new", methods=["GET", "POST"])
@login_required
def new_post():
    # 导入 db 到函数内部
    from uqnity_app import db 
    
    form = PostForm()

    if form.validate_on_submit():
        image_file = None
        if form.image.data:
            image_file = form.image.data.filename

        post = Post(
            title=form.title.data,
            content=form.content.data,
            image_file=image_file,
            author=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for("main.posts"))

    return render_template("new_post.html", title="New Post", form=form)


@main.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    # 导入 db 到函数内部
    from uqnity_app import db 

    form = SettingsForm(obj=current_user)

    if form.validate_on_submit():
        form.populate_obj(current_user)
        db.session.commit()
        flash("Your settings have been updated successfully!", "success")
        return redirect(url_for("main.settings"))

    return render_template("settings.html", title="Settings", form=form, user=current_user)


CANDIDATES = [
    {"id": 1011, "name": "Evy",    "hint": "Both of you like House music!"},
    {"id": 1012, "name": "Oliver", "hint": "Both of you like exploring new food!"},
    {"id": 1013, "name": "Chloe",  "hint": "You both joined UQ in 2024"},
]

INBOUND_REQUESTS = [
    {"id": 5001, "from_name": "Leah"},
    {"id": 5002, "from_name": "Samuel"},
]

FRIENDS = [
    {"id": 3, "name": "Elijah", "fresh": False},
    {"id": 4, "name": "Lily",   "fresh": False},
]

ROOMS = [{"id": 201, "name": "COMP1100 study group"}]

CHANNELS = [
    {"id": 301, "name": "BSA"},
    {"id": 302, "name": "UQMPS"},
    {"id": 303, "name": "UQ BARS"},
    {"id": 304, "name": "UQ Bakeology"},
    {"id": 305, "name": "WACC"},
]

MESSAGES = {
    3: [{"who": "them", "text": "How many interviews do we need?"},
        {"who": "me",   "text": "8 in total"}],
    4: [{"who": "them", "text": "NOoooo"},
        {"who": "me",   "text": "Yep this can't be real"}],
}

ROOM_MSGS = {201: [{"who": "them", "text": "I thought it's 5"}]}

CHAN_MSGS = {
    301: [{"who": "them", "text": "New event this Saturday!!!"}],
    302: [{"who": "them", "text": "Welcome to UQMPS"}],
    303: [{"who": "them", "text": "Tonight: BARS meetup"}],
    304: [{"who": "them", "text": "Sourdough tips incoming"}],
    305: [{"who": "them", "text": "Careers panel next week"}],
}

CHAN_FEED = {
    301: [{"author":"BSA (Admin)","text":"Gala Night – remember...","stamp":"9:02 AM"},
          {"author":"BSA (Admin)","text":"New event this Saturday!!!","stamp":"9:05 AM"}],
    302: [{"author":"UQMPS (Admin)","text":"Project showcase!","stamp":"9:20 AM"}],
    303: [{"author":"BARS (Admin)","text":"Friday drinks 🍻","stamp":"9:40 AM"}],
    304: [{"author":"Bakeology","text":"Bake sale recipe drop","stamp":"9:10 AM"}],
    305: [{"author":"WACC","text":"Accounting intro talk","stamp":"9:16 AM"}],
}


@main.route("/chats")
@login_required
def chats_root():
    return redirect(url_for("main.chats_private"))


@main.route("/chats/private")
@login_required
def chats_private():
    return render_template("chat_private.html", friends=FRIENDS)


@main.route("/chats/rooms")
@login_required
def chats_rooms():
    return render_template("chat_rooms.html", rooms=ROOMS)


@main.route("/chats/channels")
@login_required
def chats_channels():
    return render_template("chat_channels.html", channels=CHANNELS)


@main.route("/find")
@login_required
def find_friends():
    return render_template("find_friends.html", users=CANDIDATES)


@main.post("/api/friend_request")
@login_required
def api_friend_request():
    target_id = request.form.get("target_id", type=int)
    u = next((x for x in CANDIDATES if x["id"] == target_id), None)
    if not u:
        return jsonify({"status": "error", "message": "No such user"}), 404
    return jsonify({"status": "ok", "message": f"Friend request sent to {u['name']}."})


@main.get("/api/notifications")
@login_required
def api_notifications():
    items = [{"id": r["id"], "from_name": r["from_name"],
              "text": f"{r['from_name']}: Request to add you as a friend"} for r in INBOUND_REQUESTS]
    return jsonify({"items": items})


@main.post("/api/notif/accept")
@login_required
def api_notif_accept():
    name = request.form.get("name")
    if not name:
        return jsonify({"ok": False}), 400
   
    new_id = max([f["id"] for f in FRIENDS] + [10000]) + 1
    FRIENDS.append({"id": new_id, "name": name, "fresh": True})
    MESSAGES.setdefault(new_id, [])
    
    global INBOUND_REQUESTS
    INBOUND_REQUESTS = [r for r in INBOUND_REQUESTS if r["from_name"] != name]
    return jsonify({"ok": True, "friend": {"id": new_id, "name": name}})


@main.post("/api/notifications/clear")
@login_required
def api_notifications_clear():
    INBOUND_REQUESTS.clear()
    return jsonify({"ok": True})


@main.get("/api/state/friends")
@login_required
def api_state_friends():
    return jsonify({"friends": FRIENDS})


@main.get("/api/messages/<kind>/<int:target_id>")
@login_required
def api_messages(kind, target_id):
    if kind == "friend":
        return jsonify({"items": MESSAGES.get(target_id, [])})
    if kind == "room":
        return jsonify({"items": ROOM_MSGS.get(target_id, [])})
    return jsonify({"items": CHAN_MSGS.get(target_id, [])})


@main.get("/api/channel/feed/<int:cid>")
@login_required
def api_channel_feed(cid):
    return jsonify({"items": CHAN_FEED.get(cid, [])})


@main.post("/api/message/send")
@login_required
def api_message_send():
    kind = request.form.get("kind")
    target_id = request.form.get("id", type=int)
    text = (request.form.get("text") or "").strip()
    if not text:
        return jsonify({"ok": False}), 400

    if kind == "friend":
        MESSAGES.setdefault(target_id, []).append({"who": "me", "text": text})
        for f in FRIENDS:
            if f["id"] == target_id:
                f["fresh"] = False
                break
    elif kind == "room":
        ROOM_MSGS.setdefault(target_id, []).append({"who": "me", "text": text})
    else:
        CHAN_MSGS.setdefault(target_id, []).append({"who": "me", "text": text})

    return jsonify({"ok": True, "last": text})


@main.route("/user/<string:username>")
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()

    return render_template(
        "user_profile.html",
        title=f"{user.username}'s Profile",
        user=user,
        posts=posts
    )


@main.route('/help_support', methods=['GET', 'POST'])
def help_support():
    if request.method == 'POST':
        rating = request.form.get('rating')
        appreciate = request.form.get('appreciate')
        improve = request.form.get('improve')
        comments = request.form.get('comments')
        
        print(f"Rating: {rating}")
        print(f"Appreciate: {appreciate}")
        print(f"Improve: {improve}")
        print(f"Comments: {comments}")
        
        flash('Thank you for your feedback! We appreciate your input.', 'success')
        return redirect(url_for('main.help_support'))
    
    return render_template('help_support.html', title='Help & Support')