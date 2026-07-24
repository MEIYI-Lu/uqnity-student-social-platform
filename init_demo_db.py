from datetime import datetime, timedelta

from uqnity_app import create_app, db, bcrypt
from uqnity_app.Models import User, Post, EventOrganizer, Event


app = create_app()


def create_demo_database():
    with app.app_context():
        # Create all tables defined in the current SQLAlchemy models.
        db.create_all()

        # Safety check:
        # Do not overwrite or modify an existing populated database.
        if User.query.first() is not None or Event.query.first() is not None:
            print("Database already contains data.")
            print("No existing data was changed.")
            return

        # -------------------------
        # Demo users
        # -------------------------
        demo_password = bcrypt.generate_password_hash(
            "Demo123!"
        ).decode("utf-8")

        meiyi_demo = User(
            username="demo",
            name="Demo User",
            email="demo@example.com",
            password=demo_password,
            image_file="default.jpg",
            bio="Demo account for exploring UQnity.",
            program="Bachelor of Computer Science",
            campus="St Lucia",
            interests="Technology, AI, Events",
        )

        oliver = User(
            username="oliver",
            name="Oliver Green",
            email="oliver@example.com",
            password=demo_password,
            image_file="default.jpg",
            bio="Food lover, culture explorer, and university foodie.",
            program="Bachelor of Arts",
            campus="St Lucia",
            interests="Food, Photography, Travel",
        )

        evy = User(
            username="evy",
            name="Evy Liu",
            email="evy@example.com",
            password=demo_password,
            image_file="default.jpg",
            bio="Music enthusiast who enjoys meeting new people.",
            program="Bachelor of Music",
            campus="St Lucia",
            interests="Music, Events, Sound Design",
        )

        db.session.add_all([meiyi_demo, oliver, evy])
        db.session.flush()

        # -------------------------
        # Demo posts
        # -------------------------
        posts = [
            Post(
                title="Welcome to UQnity!",
                content=(
                    "This is a demo post showing how students can "
                    "share updates and connect with the community."
                ),
                author=meiyi_demo,
            ),
            Post(
                title="Best cafés near campus ☕",
                content=(
                    "What are your favourite places to study "
                    "and grab coffee around campus?"
                ),
                author=oliver,
            ),
            Post(
                title="Music meetup 🎵",
                content=(
                    "Looking for students interested in a casual "
                    "music meetup this weekend!"
                ),
                author=evy,
            ),
        ]

        db.session.add_all(posts)

        # -------------------------
        # Demo event organiser
        # -------------------------
        organizer = EventOrganizer(
            name="UQnity Student Community",
            profile_image="default_org.jpg",
            rating=4.8,
            description="Demo organiser for UQnity community events.",
        )

        db.session.add(organizer)
        db.session.flush()

        # -------------------------
        # Demo future events
        #
        # Keep at least 4 future events because the current
        # event-details logic tries to display 3 related events.
        # -------------------------
        now = datetime.now()

        events = [
            Event(
                name="AI & Technology Meetup",
                banner_image="default_event.jpg",
                details=(
                    "Meet students interested in artificial intelligence, "
                    "technology and software development."
                ),
                reasons_to_attend=[
                    "Meet students with similar interests",
                    "Discuss technology projects",
                    "Build your network",
                ],
                category="Tech & Innovation",
                tags=["AI", "Technology", "Networking"],
                date=now + timedelta(days=7),
                location="St Lucia Campus",
                duration=120,
                registration_required=True,
                expected_attendance=80,
                rating=4.7,
                organizer_id=organizer.id,
            ),
            Event(
                name="Student Social Night",
                banner_image="default_event.jpg",
                details=(
                    "A relaxed social event for students to meet "
                    "new friends from different programs."
                ),
                reasons_to_attend=[
                    "Meet new friends",
                    "Relax after classes",
                    "Join the student community",
                ],
                category="Social Events",
                tags=["Social", "Friends", "Community"],
                date=now + timedelta(days=14),
                location="UQ Union Complex",
                duration=180,
                registration_required=False,
                expected_attendance=120,
                rating=4.5,
                organizer_id=organizer.id,
            ),
            Event(
                name="Career Networking Evening",
                banner_image="default_event.jpg",
                details=(
                    "Connect with other students and practise "
                    "professional networking in a friendly environment."
                ),
                reasons_to_attend=[
                    "Practise networking",
                    "Meet students from different disciplines",
                    "Share career ideas",
                ],
                category="Networking",
                tags=["Career", "Networking", "Students"],
                date=now + timedelta(days=21),
                location="Advanced Engineering Building",
                duration=120,
                registration_required=True,
                expected_attendance=100,
                rating=4.6,
                organizer_id=organizer.id,
            ),
            Event(
                name="Campus Sustainability Day",
                banner_image="default_event.jpg",
                details=(
                    "A community event focused on sustainability "
                    "and environmental awareness."
                ),
                reasons_to_attend=[
                    "Learn about sustainability",
                    "Join community activities",
                    "Meet environmentally minded students",
                ],
                category="Sustainability & Environment",
                tags=["Sustainability", "Environment", "Community"],
                date=now + timedelta(days=28),
                location="Great Court",
                duration=240,
                registration_required=False,
                expected_attendance=150,
                rating=4.8,
                organizer_id=organizer.id,
            ),
        ]

        db.session.add_all(events)
        db.session.commit()

        print()
        print("Demo database created successfully.")
        print()
        print("Demo login:")
        print("Username: demo")
        print("Password: Demo123!")
        print()


if __name__ == "__main__":
    create_demo_database()