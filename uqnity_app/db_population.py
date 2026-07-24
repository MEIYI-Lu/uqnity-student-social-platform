from datetime import datetime, timedelta
from uqnity_app import app, db
from uqnity_app.Models import Event, EventOrganizer, EventRegistration, Review, User
from werkzeug.security import generate_password_hash
import random
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

with app.app_context():  # Push the app context here
    # Clear tables except existing users (Be careful with this on production!)
    db.session.query(Review).delete()
    db.session.query(EventRegistration).delete()
    db.session.query(Event).delete()
    db.session.query(EventOrganizer).delete()
    db.session.commit()

    # Get existing users (don't modify them)
    existing_users = User.query.all()
    print(f"Found {len(existing_users)} existing users in database")

    # Create additional users
    new_users_data = [
        {'username': 'sarah_chen', 'email': 'sarah.chen@uq.net.au', 'password': 'password123'},
        {'username': 'james_wong', 'email': 'james.wong@uq.net.au', 'password': 'password123'},
        {'username': 'emily_brown', 'email': 'emily.brown@uq.net.au', 'password': 'password123'},
        {'username': 'michael_patel', 'email': 'michael.patel@uq.net.au', 'password': 'password123'},
        {'username': 'olivia_smith', 'email': 'olivia.smith@uq.net.au', 'password': 'password123'},
        {'username': 'daniel_nguyen', 'email': 'daniel.nguyen@uq.net.au', 'password': 'password123'},
        {'username': 'sophia_anderson', 'email': 'sophia.anderson@uq.net.au', 'password': 'password123'},
        {'username': 'liam_taylor', 'email': 'liam.taylor@uq.net.au', 'password': 'password123'},
        {'username': 'ava_wilson', 'email': 'ava.wilson@uq.net.au', 'password': 'password123'},
        {'username': 'noah_lee', 'email': 'noah.lee@uq.net.au', 'password': 'password123'},
        {'username': 'mia_garcia', 'email': 'mia.garcia@uq.net.au', 'password': 'password123'},
        {'username': 'ethan_martinez', 'email': 'ethan.martinez@uq.net.au', 'password': 'password123'},
    ]
    
    new_users = []
    """for user_data in new_users_data:
        hashed_password = bcrypt.generate_password_hash(user_data['password']).decode('utf-8')
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            password=hashed_password
        )
        new_users.append(user)
        db.session.add(user)"""
    
    db.session.commit()
    print(f"Created {len(new_users)} new users!")
    
    # Combine existing and new users for registrations and reviews
    all_users = existing_users + new_users

    # Create Event Organizers (combining both sets)
    uq_union = EventOrganizer(
        name="UQ Union", 
        rating=4.8, 
        description="The UQ Union is the peak student body that organizes social, cultural, and advocacy events for UQ students."
    )
    student_services = EventOrganizer(
        name="UQ Student Services", 
        rating=4.7, 
        description="Student Services provides a wide range of support, resources, and events to help UQ students thrive academically and personally."
    )
    uq_sports = EventOrganizer(
        name="UQ Sports", 
        rating=4.6, 
        description="UQ Sports organizes various sports events and fitness activities to help students stay active and healthy."
    )
    uq_engineering_society = EventOrganizer(
        name="UQ Engineering Society", 
        rating=4.5, 
        description="The UQ Engineering Society connects students with engineering events, workshops, and career opportunities."
    )
    uq_music_society = EventOrganizer(
        name="UQ Music Society", 
        rating=4.9, 
        description="The UQ Music Society promotes music-related activities, performances, and workshops for students and staff."
    )
    uq_sustainability_club = EventOrganizer(
        name="UQ Sustainability Club", 
        rating=4.6, 
        description="The UQ Sustainability Club focuses on environmental causes, sustainability events, and eco-friendly initiatives."
    )
    uq_career_services = EventOrganizer(
        name="UQ Career Services", 
        rating=4.7, 
        description="UQ Career Services helps students find internships, jobs, and develop essential career skills for the future."
    )
    uq_art_gallery = EventOrganizer(
        name="UQ Art Gallery", 
        rating=4.8, 
        description="The UQ Art Gallery showcases art exhibitions and creative events for students to explore and appreciate art."
    )
    uq_health_wellbeing = EventOrganizer(
        name="UQ Health & Wellbeing", 
        rating=4.7, 
        description="UQ Health & Wellbeing organizes events that promote mental health, wellness, and self-care practices among students."
    )
    uq_computer_science_club = EventOrganizer(
        name="UQ Computer Science Club",
        rating=4.8,
        description="Tech talks, hackathons, and coding workshops for computer science enthusiasts."
    )
    uq_business_school = EventOrganizer(
        name="UQ Business School Society",
        rating=4.6,
        description="Professional development and networking opportunities for business students at UQ."
    )
    uq_multicultural_society = EventOrganizer(
        name="UQ Multicultural Society",
        rating=4.4,
        description="Celebrating diversity through cultural festivals, food events, and international student support."
    )
    uq_debating_society = EventOrganizer(
        name="UQ Debating Society",
        rating=4.3,
        description="Developing public speaking and critical thinking skills through competitive debates and workshops."
    )
    uq_medical_society = EventOrganizer(
        name="UQ Medical Students Society",
        rating=4.6,
        description="Supporting medical students through academic events, wellness initiatives, and social gatherings."
    )
    uq_environmental_collective = EventOrganizer(
        name="UQ Environmental Collective",
        rating=4.4,
        description="Promoting sustainability and environmental awareness through workshops and campus initiatives."
    )

    # Add organizers to the database
    organizers = [uq_union, student_services, uq_sports, uq_engineering_society, uq_music_society, 
                  uq_sustainability_club, uq_career_services, uq_art_gallery, uq_health_wellbeing,
                  uq_computer_science_club, uq_business_school, uq_multicultural_society, 
                  uq_debating_society, uq_medical_society, uq_environmental_collective]
    
    db.session.add_all(organizers)
    db.session.commit()
    print(f"Created {len(organizers)} organizers!")

    # Create Events - mix of past and future events
    base_date = datetime.now()
    
    events = [
        # PAST EVENTS (for reviews)
        Event(
            name="O-Week: UQ Welcome Party",
            banner_image="oweek_welcome.jpg",
            details="Kickstart your university journey with the UQ Union's O-Week Welcome Party! Music, food, and entertainment all day.",
            tags=['orientation', 'party', 'social', 'welcome'],
            date=base_date - timedelta(days=60),
            location="Great Court, St Lucia",
            duration=4,
            dress_code="Casual, comfortable attire",
            age_requirement="18+",
            parking="Free parking available at the UQ multi-story car park",
            registration_required=True,
            expected_attendance=1000,
            organizer_id=uq_union.id,
            reasons_to_attend=["Meet new people", "Free food and drinks", "Exciting performances and music"],
            category="Entertainment"
        ),
        Event(
            name="UQ Sports Day",
            banner_image="sports_day.jpg",
            details="Join UQ Sports for a day of competitive fun with various sporting activities and games.",
            tags=['sports', 'competition', 'fitness'],
            date=base_date - timedelta(days=45),
            location="UQ Sports Fields",
            duration=6,
            dress_code="Sportswear",
            age_requirement="All ages welcome",
            parking="Available near the sports fields",
            registration_required=True,
            expected_attendance=500,
            organizer_id=uq_sports.id,
            reasons_to_attend=["Stay fit and healthy", "Compete in fun games", "Meet other sports enthusiasts"],
            category="Sports & Recreation"
        ),
        Event(
            name="Tech Innovation Hackathon",
            banner_image="hackathon.jpg",
            details="24-hour hackathon focused on building solutions for campus sustainability. Form teams, code, and compete for prizes worth $5,000!",
            tags=['technology', 'coding', 'competition', 'sustainability'],
            date=base_date - timedelta(days=30),
            location="UQ Advanced Engineering Building",
            duration=1440,
            dress_code="Casual - bring comfortable clothes",
            age_requirement="All ages",
            parking="Limited parking, public transport recommended",
            registration_required=True,
            expected_attendance=120,
            organizer_id=uq_computer_science_club.id,
            reasons_to_attend=["Prize pool of $5,000", "Free meals and snacks", "Industry mentors", "Portfolio building opportunity"],
            category="Tech & Innovation"
        ),
        Event(
            name="UQ International Food Festival",
            banner_image="food_festival.jpg",
            details="Celebrate UQ's diversity with delicious food from all over the world, brought to you by the International Students Society.",
            tags=['food', 'international', 'festival', 'cultural'],
            date=base_date - timedelta(days=25),
            location="UQ Campus Quad",
            duration=5,
            dress_code="Casual, bring your appetite!",
            age_requirement="All ages welcome",
            parking="Limited parking; public transport recommended",
            registration_required=False,
            expected_attendance=1500,
            organizer_id=uq_multicultural_society.id,
            reasons_to_attend=["Taste food from around the world", "Experience different cultures", "Enjoy a fun, social atmosphere"],
            category="Food"
        ),
        Event(
            name="Resume Building Workshop",
            banner_image="resume_workshop.jpg",
            details="Learn how to craft the perfect resume with guidance from UQ Career Services and industry professionals.",
            tags=['career', 'workshop', 'resume', 'job search'],
            date=base_date - timedelta(days=20),
            location="UQ Careers Centre",
            duration=2,
            dress_code="Smart casual",
            age_requirement="All students welcome",
            parking="Parking available at the UQ parking garage",
            registration_required=True,
            expected_attendance=100,
            organizer_id=uq_career_services.id,
            reasons_to_attend=["Improve your resume", "Get tips from industry experts", "Stand out in the job market"],
            category="Academic & Professional Development"
        ),
        Event(
            name="Medical Students Trivia Night",
            banner_image="trivia_night.jpg",
            details="Test your general knowledge and medical trivia in teams of 6. Prizes for top teams, raffles, and a great night out.",
            tags=['social', 'trivia', 'medical', 'fundraiser'],
            date=base_date - timedelta(days=15),
            location="Red Room Bar",
            duration=180,
            dress_code="Casual",
            age_requirement="18+",
            parking="Street parking available",
            registration_required=True,
            expected_attendance=120,
            organizer_id=uq_medical_society.id,
            reasons_to_attend=["Fun team competition", "Great prizes", "Support student wellness", "Meet other med students"],
            category="Social Events"
        ),
        Event(
            name="Mental Health Awareness Week",
            banner_image="mental_health_week.jpg",
            details="Join UQ Health & Wellbeing for a week dedicated to promoting mental health awareness and self-care strategies.",
            tags=['mental health', 'wellbeing', 'self-care', 'workshop', 'awareness'],
            date=base_date - timedelta(days=10),
            location="UQ Health Centre",
            duration=5,
            dress_code="Casual, comfortable attire",
            age_requirement="All students welcome",
            parking="Available at the UQ Health Centre parking",
            registration_required=True,
            expected_attendance=300,
            organizer_id=uq_health_wellbeing.id,
            reasons_to_attend=["Promote mental health awareness", "Engage in self-care practices", "Support the UQ community"],
            category="Health & Well-being"
        ),
        Event(
            name="Indigenous Art Exhibition",
            banner_image="indigenous_art.jpg",
            details="Celebrating Indigenous Australian artists with a special exhibition featuring contemporary and traditional artworks.",
            tags=['art', 'culture', 'indigenous', 'exhibition'],
            date=base_date - timedelta(days=8),
            location="UQ Art Museum",
            duration=180,
            dress_code="Casual",
            age_requirement="All ages",
            parking="Available at P2 car park",
            registration_required=False,
            expected_attendance=100,
            organizer_id=uq_art_gallery.id,
            reasons_to_attend=["Unique cultural experience", "Meet the artists", "Free guided tours", "Support Indigenous art"],
            category="Arts"
        ),
        Event(
            name="Biotechnology Industry Night",
            banner_image="biotech_night.jpg",
            details="Network with leading biotechnologits and companies in Brisbane. Panel discussions, company presentations, and informal networking.",
            tags=['biotechnology', 'networking', 'industry', 'career'],
            date=base_date - timedelta(days=5),
            location="UQ Forgan Smith Building",
            duration=180,
            dress_code="Business casual",
            age_requirement="18+",
            parking="Limited parking available",
            registration_required=True,
            expected_attendance=200,
            organizer_id=uq_engineering_society.id,
            reasons_to_attend=["Meet industry professionals", "Learn about career pathways", "Free food and drinks", "Exclusive job opportunities"],
            category="Networking"
        ),
        Event(
            name="Sustainability Week at UQ",
            banner_image="sustainability_week.jpg",
            details="Learn how to make a difference in the environment with workshops and activities organized by the UQ Sustainability Club.",
            tags=['sustainability', 'environment', 'eco-friendly', 'workshops'],
            date=base_date - timedelta(days=3),
            location="UQ Sustainability Hub",
            duration=4,
            dress_code="Casual, eco-friendly attire",
            age_requirement="All students welcome",
            parking="Public transport recommended",
            registration_required=True,
            expected_attendance=300,
            organizer_id=uq_environmental_collective.id,
            reasons_to_attend=["Learn about sustainability", "Get involved in eco-initiatives", "Help make a change for the planet"],
            category="Sustainability & Environment"
        ),
        
        # FUTURE EVENTS
        Event(
            name="Yoga & Mindfulness Workshop",
            banner_image="yoga_workshop.jpg",
            details="De-stress with a guided yoga session followed by mindfulness meditation. Perfect for exam preparation and mental wellness.",
            tags=['wellness', 'fitness', 'mindfulness', 'health'],
            date=base_date + timedelta(days=5),
            location="UQ Sport Centre Studio 2",
            duration=90,
            dress_code="Activewear",
            age_requirement="All ages",
            parking="Available at P11 car park",
            registration_required=True,
            expected_attendance=40,
            organizer_id=uq_health_wellbeing.id,
            reasons_to_attend=["Professional yoga instructor", "Stress relief techniques", "Free yoga mat provided", "Relaxation and mental wellness"],
            category="Health & Well-being"
        ),
        Event(
            name="Semester Welcome BBQ",
            banner_image="welcome_bbq.jpg",
            details="Join us for the semester kickoff BBQ at the Great Court! Free food, live music, and a chance to meet fellow students.",
            tags=['social', 'food', 'music', 'networking'],
            date=base_date + timedelta(days=8),
            location="UQ Great Court",
            duration=180,
            dress_code="Casual",
            age_requirement="18+",
            parking="Available at P10 car park",
            registration_required=True,
            expected_attendance=300,
            organizer_id=uq_union.id,
            reasons_to_attend=["Free food and drinks", "Live music performances", "Meet new friends", "Campus tour for new students"],
            category="Social Events"
        ),
        Event(
            name="Coffee & Connections: Networking Breakfast",
            banner_image="networking_breakfast.jpg",
            details="Early morning networking over breakfast. Connect with alumni, professionals, and peers in an informal setting.",
            tags=['networking', 'business', 'professional', 'breakfast'],
            date=base_date + timedelta(days=11),
            location="UQ Business School Atrium",
            duration=120,
            dress_code="Business casual",
            age_requirement="All ages",
            parking="Available at P10 car park",
            registration_required=True,
            expected_attendance=70,
            organizer_id=uq_business_school.id,
            reasons_to_attend=["Meet industry professionals", "Free breakfast", "Informal networking", "Alumni connections"],
            category="Networking"
        ),
        Event(
            name="Women in STEM Panel",
            banner_image="women_stem.jpg",
            details="Inspiring panel discussion with successful women in STEM careers. Discuss challenges, opportunities, and pathways to success.",
            tags=['diversity', 'STEM', 'women', 'panel discussion'],
            date=base_date + timedelta(days=14),
            location="UQ Prentice Building",
            duration=120,
            dress_code="Business casual",
            age_requirement="All ages",
            parking="Available at P11 car park",
            registration_required=True,
            expected_attendance=100,
            organizer_id=uq_engineering_society.id,
            reasons_to_attend=["Inspiring role models", "Career insights", "Networking opportunity", "Q&A session"],
            category="Diversity & Inclusion"
        ),
        Event(
            name="Career Expo 2025",
            banner_image="career_expo.jpg",
            details="Connect with 80+ employers from various industries. Bring your resume, dress professionally, and explore opportunities.",
            tags=['career', 'networking', 'professional', 'jobs'],
            date=base_date + timedelta(days=20),
            location="UQ Sport & Fitness Centre",
            duration=300,
            dress_code="Business professional",
            age_requirement="All ages",
            parking="Available at P11 car park",
            registration_required=False,
            expected_attendance=800,
            organizer_id=uq_career_services.id,
            reasons_to_attend=["80+ top employers", "On-spot interviews", "Resume review stations", "Professional headshots"],
            category="Academic & Professional Development"
        ),
        Event(
            name="Outdoor Rock Climbing Trip",
            banner_image="rock_climbing.jpg",
            details="Day trip to Kangaroo Point Cliffs for outdoor rock climbing. All equipment provided, professional instructors.",
            tags=['sports', 'outdoor', 'adventure', 'fitness'],
            date=base_date + timedelta(days=21),
            location="Kangaroo Point Cliffs",
            duration=360,
            dress_code="Activewear and closed-toe shoes",
            age_requirement="18+",
            parking="Bus transport from campus",
            registration_required=True,
            expected_attendance=30,
            organizer_id=uq_sports.id,
            reasons_to_attend=["Professional instruction", "All equipment provided", "Transport included", "Adventure and fitness"],
            category="Sports & Recreation"
        ),
        Event(
            name="Climate Action Workshop",
            banner_image="climate_workshop.jpg",
            details="Learn practical ways to reduce your carbon footprint. Workshop includes composting basics, sustainable fashion, and advocacy.",
            tags=['environment', 'sustainability', 'workshop', 'climate'],
            date=base_date + timedelta(days=22),
            location="UQ Sustainability Hub",
            duration=120,
            dress_code="Casual",
            age_requirement="All ages",
            parking="Bicycle parking encouraged",
            registration_required=True,
            expected_attendance=60,
            organizer_id=uq_environmental_collective.id,
            reasons_to_attend=["Practical sustainability tips", "Free eco-friendly starter kit", "Connect with like-minded students", "Make a difference"],
            category="Sustainability & Environment"
        ),
        Event(
            name="Python for Data Science Bootcamp",
            banner_image="python_bootcamp.jpg",
            details="Intensive weekend bootcamp covering Python basics, data analysis with Pandas, and machine learning fundamentals.",
            tags=['technology', 'data science', 'python', 'workshop'],
            date=base_date + timedelta(days=27),
            location="UQ General Purpose South Building",
            duration=480,
            dress_code="Casual - bring laptop",
            age_requirement="All ages",
            parking="Available at P10 car park",
            registration_required=True,
            expected_attendance=50,
            organizer_id=uq_computer_science_club.id,
            reasons_to_attend=["Learn in-demand skills", "Hands-on projects", "Free course materials", "Certificate of completion"],
            category="Workshops & Training"
        ),
        Event(
            name="Debating Championship Finals",
            banner_image="debating_finals.jpg",
            details="Watch the top debating teams compete in the semester championship. Topic: 'The future of AI in education.'",
            tags=['debate', 'academic', 'competition', 'public speaking'],
            date=base_date + timedelta(days=28),
            location="UQ Michie Building Lecture Theatre",
            duration=120,
            dress_code="Casual",
            age_requirement="All ages",
            parking="Available at P2 car park",
            registration_required=False,
            expected_attendance=80,
            organizer_id=uq_debating_society.id,
            reasons_to_attend=["High-level intellectual debate", "Improve critical thinking", "Free entry", "Meet debating champions"],
            category="Academic & Professional Development"
        ),
        Event(
            name="Start-up Pitch Competition",
            banner_image="startup_pitch.jpg",
            details="Watch student entrepreneurs pitch their innovative business ideas to a panel of investors. Winning team receives $10,000!",
            tags=['startup', 'business', 'innovation', 'competition'],
            date=base_date + timedelta(days=30),
            location="UQ Colin Clark Building",
            duration=150,
            dress_code="Business casual",
            age_requirement="All ages",
            parking="Available at P10 car park",
            registration_required=False,
            expected_attendance=150,
            organizer_id=uq_business_school.id,
            reasons_to_attend=["See innovative ideas", "Learn about entrepreneurship", "Networking opportunities", "Inspiration for your own ventures"],
            category="Entrepreneurship & Startups"
        ),
        Event(
            name="Mental Health First Aid Training",
            banner_image="mental_health_training.jpg",
            details="Accredited Mental Health First Aid course. Learn to identify, understand and respond to signs of mental health issues.",
            tags=['mental health', 'training', 'wellness', 'first aid'],
            date=base_date + timedelta(days=32),
            location="UQ Oral Health Centre",
            duration=480,
            dress_code="Casual",
            age_requirement="18+",
            parking="Available at P9 car park",
            registration_required=True,
            expected_attendance=25,
            organizer_id=uq_medical_society.id,
            reasons_to_attend=["Accredited certification", "Life-saving skills", "Support friends and family", "Free for students"],
            category="Health & Well-being"
        ),
        Event(
            name="Battle of the Bands",
            banner_image="battle_bands.jpg",
            details="UQ student bands compete for the title! Live performances throughout the day, food trucks, and a fantastic atmosphere.",
            tags=['music', 'entertainment', 'competition', 'live performance'],
            date=base_date + timedelta(days=35),
            location="UQ Great Court",
            duration=300,
            dress_code="Casual",
            age_requirement="All ages",
            parking="Available at P10 car park",
            registration_required=False,
            expected_attendance=400,
            organizer_id=uq_music_society.id,
            reasons_to_attend=["Live music all day", "Support student musicians", "Food trucks", "Great atmosphere"],
            category="Music"
        ),
        Event(
            name="Spring Arts Festival",
            banner_image="arts_festival.jpg",
            details="Celebrate creativity with performances, art installations, live painting, poetry readings, and music.",
            tags=['arts', 'festival', 'performance', 'culture'],
            date=base_date + timedelta(days=40),
            location="UQ Warehouse Lawns",
            duration=360,
            dress_code="Casual",
            age_requirement="All ages",
            parking="Available at P2 car park",
            registration_required=False,
            expected_attendance=350,
            organizer_id=uq_art_gallery.id,
            reasons_to_attend=["Diverse art forms", "Live performances", "Interactive installations", "Creative atmosphere"],
            category="Festivals & Celebrations"
        ),
        Event(
            name="UQ Coding Bootcamp",
            banner_image="coding_bootcamp.jpg",
            details="Join UQ Computer Science Society for an intensive coding bootcamp. Enhance your programming skills and learn new technologies.",
            tags=['coding', 'bootcamp', 'tech', 'workshop'],
            date=base_date + timedelta(days=45),
            location="UQ Computer Science Building",
            duration=8,
            dress_code="Casual, bring a laptop",
            age_requirement="All students welcome",
            parking="Available near the building",
            registration_required=True,
            expected_attendance=100,
            organizer_id=uq_computer_science_club.id,
            reasons_to_attend=["Boost your coding skills", "Learn from experienced mentors", "Collaborate with peers"],
            category="Technology"
        ),
        Event(
            name="UQ Literary Festival",
            banner_image="literary_festival.jpg",
            details="Celebrate literature with UQ's Literary Society. Attend author talks, poetry readings, and writing workshops.",
            tags=['literature', 'festival', 'author talks', 'workshop'],
            date=base_date + timedelta(days=50),
            location="UQ Central Library",
            duration=6,
            dress_code="Casual, bring your book collection",
            age_requirement="All students welcome",
            parking="Limited parking, public transport recommended",
            registration_required=False,
            expected_attendance=500,
            organizer_id=uq_union.id,
            reasons_to_attend=["Meet local authors", "Improve your writing skills", "Enjoy literary discussions"],
            category="Literature"
        ),
        Event(
            name="UQ Dance Party",
            banner_image="dance_party.jpg",
            details="Get ready to groove at the UQ Dance Party, hosted by the UQ Music Society. DJ, lights, and amazing beats all night.",
            tags=['party', 'music', 'dance', 'social'],
            date=base_date + timedelta(days=55),
            location="UQ Refectory",
            duration=5,
            dress_code="Dress to impress, but comfortable shoes for dancing",
            age_requirement="18+",
            parking="Available at UQ multi-story car park",
            registration_required=True,
            expected_attendance=1000,
            organizer_id=uq_music_society.id,
            reasons_to_attend=["Dance the night away", "Meet new people", "Enjoy great music and vibes"],
            category="Entertainment"
        ),
        Event(
            name="Sustainable Fashion Show",
            banner_image="fashion_show.jpg",
            details="UQ Sustainability Club presents a fashion show to promote eco-friendly fashion and sustainable clothing choices.",
            tags=['sustainability', 'fashion', 'eco-friendly', 'show'],
            date=base_date + timedelta(days=60),
            location="UQ Great Court",
            duration=3,
            dress_code="Eco-friendly attire, of course!",
            age_requirement="All students welcome",
            parking="Limited parking, public transport recommended",
            registration_required=True,
            expected_attendance=500,
            organizer_id=uq_sustainability_club.id,
            reasons_to_attend=["Learn about sustainable fashion", "See eco-friendly designs", "Support local designers"],
            category="Sustainability & Environment"
        ),
        Event(
            name="UQ Career Networking Night",
            banner_image="networking_night.jpg",
            details="Meet professionals from various industries at UQ Career Services' Networking Night. A great opportunity to make connections.",
            tags=['career', 'networking', 'professionals', 'jobs'],
            date=base_date + timedelta(days=65),
            location="UQ Campus Hall",
            duration=3,
            dress_code="Business casual",
            age_requirement="All students welcome",
            parking="Available at UQ visitor parking",
            registration_required=True,
            expected_attendance=200,
            organizer_id=uq_career_services.id,
            reasons_to_attend=["Expand your professional network", "Meet potential employers", "Get career tips"],
            category="Networking"
        ),
        Event(
            name="UQ Open Mic Night",
            banner_image="open_mic.jpg",
            details="UQ Music Society invites all musicians, poets, and performers for a fun and relaxed Open Mic Night. Showcase your talent!",
            tags=['music', 'performance', 'open mic', 'social'],
            date=base_date + timedelta(days=70),
            location="UQ Student Union Building",
            duration=4,
            dress_code="Casual, come as you are",
            age_requirement="All students welcome",
            parking="Parking available at UQ multi-story car park",
            registration_required=False,
            expected_attendance=100,
            organizer_id=uq_music_society.id,
            reasons_to_attend=["Enjoy live performances", "Showcase your talent", "Support fellow students"],
            category="Arts"
        ),
        Event(
            name="UQ Meditation & Yoga Session",
            banner_image="meditation_yoga.jpg",
            details="Join UQ Health & Wellbeing for a relaxing session of meditation and yoga. Unwind and de-stress in a peaceful environment.",
            tags=['health', 'yoga', 'meditation', 'wellbeing'],
            date=base_date + timedelta(days=75),
            location="UQ Health Centre",
            duration=2,
            dress_code="Comfortable yoga attire",
            age_requirement="All students welcome",
            parking="Available at UQ Health Centre parking",
            registration_required=True,
            expected_attendance=50,
            organizer_id=uq_health_wellbeing.id,
            reasons_to_attend=["Relax and de-stress", "Learn meditation techniques", "Promote mental and physical health"],
            category="Health & Well-being"
        )
    ]

    # Add events to the database
    db.session.add_all(events)
    db.session.commit()
    print(f"Created {len(events)} events (10 past, {len(events)-10} future)!")

    # Separate past and future events
    past_events = [e for e in events if e.date < base_date]
    future_events = [e for e in events if e.date >= base_date]

    # Create Event Registrations
    registrations = []
    
    # For past events - register users who will review them
    for event in past_events:
        # Each past event has 5-10 registered users
        num_registrations = random.randint(5, 10)
        registered_users = random.sample(all_users, min(num_registrations, len(all_users)))
        
        for user in registered_users:
            registration = EventRegistration(
                user_id=user.id,
                event_id=event.id,
                registration_date=event.date - timedelta(days=random.randint(5, 20))
            )
            registrations.append(registration)
            db.session.add(registration)
    
    # For future events - each user registers for 2-4 random future events
    for user in all_users:
        num_registrations = random.randint(2, 4)
        user_future_events = random.sample(future_events, min(num_registrations, len(future_events)))
        
        for event in user_future_events:
            registration = EventRegistration(
                user_id=user.id,
                event_id=event.id,
                registration_date=datetime.now() - timedelta(days=random.randint(1, 5))
            )
            registrations.append(registration)
            db.session.add(registration)
    
    db.session.commit()
    print(f"Created {len(registrations)} event registrations!")

    # Create Reviews - ONLY for past events that users attended (registered for)
    event_comments = [
        "Amazing event! Really enjoyed it and met some great people.",
        "Well organized and lots of fun. Would definitely attend again!",
        "Good event but could have been better advertised.",
        "Fantastic experience! The organizers did an excellent job.",
        "Loved the atmosphere and the activities were super engaging.",
        "Nice event, but the venue was a bit crowded.",
        "Really valuable experience, learned so much!",
        "Had a great time with friends, highly recommend to others.",
        "Excellent networking opportunity, made some valuable connections.",
        "The food was delicious and everything was well organized.",
        "Good event overall, minor timing issues but still enjoyable.",
        "One of the best events I've attended at UQ so far!",
        "Informative and engaging, exactly what I needed.",
        "Great vibe and wonderful people. Can't wait for the next one!",
        "The speakers were inspiring and the content was relevant.",
        "Exceeded my expectations! Really glad I attended.",
        "Fun experience but could use more seating areas.",
        "Professional setup and great attention to detail.",
        "Met so many interesting people, highly valuable!",
        "The activities were well-planned and enjoyable.",
    ]
    
    organizer_comments = [
        "Very professional and responsive organizers.",
        "Great communication before and during the event.",
        "The team did a wonderful job organizing everything smoothly.",
        "Could improve on event updates, but overall very good.",
        "Really appreciate the effort put into making this event special!",
        "Well-coordinated and professional team throughout.",
        "Organizers were friendly and helpful at every step.",
        "Good organization, would definitely attend their events again.",
        "Professional setup and excellent event management.",
        "The organizers clearly care about student experience.",
        "Responsive to questions and very accommodating.",
        "Impressed by the attention to detail and planning.",
        "Fantastic team, made everyone feel welcome.",
        "Could be more proactive with updates, but great overall.",
        "Really well-run event, kudos to the organizing team!",
    ]

    reviews = []
    # Get all registrations for past events
    past_event_registrations = [r for r in registrations if r.event_id in [e.id for e in past_events]]
    
    # Create reviews for 70-80% of past event attendees
    num_reviews = int(len(past_event_registrations) * random.uniform(0.7, 0.8))
    reviewed_registrations = random.sample(past_event_registrations, num_reviews)
    
    for registration in reviewed_registrations:
        event = next(e for e in past_events if e.id == registration.event_id)
        
        event_rating = random.randint(3, 5)
        organizer_rating = random.randint(3, 5)
        
        review = Review(
            event_id=event.id,
            organizer_id=event.organizer_id,
            user_id=registration.user_id,
            event_rating=event_rating,
            organizer_rating=organizer_rating,
            event_comment=random.choice(event_comments),
            organizer_comment=random.choice(organizer_comments),
            created_at=event.date + timedelta(days=random.randint(1, 5))
        )
        reviews.append(review)
        db.session.add(review)
    
    db.session.commit()
    print(f"Created {len(reviews)} reviews (only for past events that users attended)!")

    # Update event and organizer ratings based on reviews
    for event in events:
        event_reviews = [r for r in reviews if r.event_id == event.id]
        if event_reviews:
            avg_rating = sum(r.event_rating for r in event_reviews) / len(event_reviews)
            event.rating = round(avg_rating, 1)
    
    for organizer in organizers:
        org_reviews = [r for r in reviews if r.organizer_id == organizer.id]
        if org_reviews:
            avg_rating = sum(r.organizer_rating for r in org_reviews) / len(org_reviews)
            organizer.rating = round(avg_rating, 1)
    
    db.session.commit()
    print("Updated ratings based on reviews!")

    print("\n" + "="*60)
    print("Database populated successfully!")
    print("="*60)
    print(f"Existing users preserved: {len(existing_users)}")
    print(f"New users created: {len(new_users)}")
    print(f"Total users: {len(all_users)}")
    print(f"Total organizers: {len(organizers)}")
    print(f"Total events: {len(events)}")
    print(f"  - Past events (with reviews): {len(past_events)}")
    print(f"  - Future events: {len(future_events)}")
    print(f"Total registrations: {len(registrations)}")
    print(f"Total reviews: {len(reviews)}")
    print("="*60)