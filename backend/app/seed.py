from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.core import security
from app.models import User, Meeting, Participant, TranscriptSegment, Summary, ActionItem

def seed_db(db: Session):
    # 1. Create a demo user if not exists
    demo_email = "demo@example.com"
    demo_user = db.query(User).filter(User.email == demo_email).first()
    
    if not demo_user:
        hashed_password = security.get_password_hash("password123")
        demo_user = User(
            email=demo_email,
            name="Demo User",
            hashed_password=hashed_password
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        print(f"Created demo user: {demo_email}")
    else:
        print("Demo user already exists.")
        
    # 2. Check if meetings already exist for this user. If so, skip seeding
    existing_meetings = db.query(Meeting).filter(Meeting.owner_id == demo_user.id).first()
    if existing_meetings:
        print("Database already seeded. Skipping seeding.")
        return

    print("Seeding database with sample meetings...")

    # Data definition for 4 sample meetings
    meetings_data = [
        {
            "title": "Project Alpha Kickoff",
            "date": datetime.now(timezone.utc) - timedelta(days=5),
            "duration": 1800,  # 30 mins
            "participants": ["Alice Smith", "Bob Jones", "Charlie Brown"],
            "summary": {
                "overview_text": "Kickoff meeting for Project Alpha. The team aligned on the primary project goals, roles, and initial milestones. The core focus will be completing the database schema design by next week and kicking off frontend UI layout.",
                "key_topics": ["Introduction", "Scope & Goals", "Milestones", "Next Steps"]
            },
            "transcript": [
                {"speaker": "Alice Smith", "time": 10, "text": "Welcome everyone to the Project Alpha kickoff! Thanks for joining today."},
                {"speaker": "Bob Jones", "time": 45, "text": "Excited to get started on this. Have we finalized the timeline?"},
                {"speaker": "Alice Smith", "time": 80, "text": "Yes, Bob. We plan to launch the beta in six weeks. First step is database setup."},
                {"speaker": "Charlie Brown", "time": 120, "text": "I will handle the initial database schema design. I need to get review by Tuesday."},
                {"speaker": "Bob Jones", "time": 160, "text": "Great. I should start on the frontend UI boilerplate once the schema is draft."},
                {"speaker": "Alice Smith", "time": 210, "text": "Perfect. Let's meet again next Friday to sync. Have a great weekend!"}
            ],
            "action_items": [
                {"text": "Design the initial database schema", "assignee": "Charlie Brown", "completed": False},
                {"text": "Start frontend UI boilerplate repository", "assignee": "Bob Jones", "completed": False},
                {"text": "Schedule next Friday sync meeting", "assignee": "Alice Smith", "completed": True}
            ]
        },
        {
            "title": "Sprint Planning Sync",
            "date": datetime.now(timezone.utc) - timedelta(days=3),
            "duration": 2700,  # 45 mins
            "participants": ["Bob Jones", "Charlie Brown", "David Miller"],
            "summary": {
                "overview_text": "Sprint planning session focusing on backlog review, ticket estimation, and sprint commitment. The priority of this sprint is integrating JWT authentication and setting up CORS rules.",
                "key_topics": ["Backlog Review", "Estimation", "Sprint Commitment"]
            },
            "transcript": [
                {"speaker": "Bob Jones", "time": 15, "text": "Alright team, let's look at the backlog for this sprint. We need to assign tasks."},
                {"speaker": "David Miller", "time": 60, "text": "I can take the task to implement JWT authentication logic on the backend."},
                {"speaker": "Charlie Brown", "time": 110, "text": "Awesome, David. I will write the unit tests for registration and login."},
                {"speaker": "Bob Jones", "time": 170, "text": "We should also fix the CORS configuration because the frontend has issues."},
                {"speaker": "David Miller", "time": 220, "text": "Agreed. I will add CORS middleware settings directly in main.py."}
            ],
            "action_items": [
                {"text": "Implement JWT authentication on backend", "assignee": "David Miller", "completed": False},
                {"text": "Write auth unit tests", "assignee": "Charlie Brown", "completed": False},
                {"text": "Configure CORS middleware in main.py", "assignee": "David Miller", "completed": True}
            ]
        },
        {
            "title": "Marketing Campaign Strategy",
            "date": datetime.now(timezone.utc) - timedelta(days=2),
            "duration": 3600,  # 60 mins
            "participants": ["Alice Smith", "Emma Watson"],
            "summary": {
                "overview_text": "Brainstorming and alignment session for the Q3 marketing push. Reviewed budget allocations, social media campaigns, and influencer outreach goals.",
                "key_topics": ["Social Media Strategy", "Budget Allocation", "Timeline"]
            },
            "transcript": [
                {"speaker": "Alice Smith", "time": 5, "text": "Emma, let's discuss the marketing roadmap. Do you have the Q3 numbers?"},
                {"speaker": "Emma Watson", "time": 35, "text": "Yes, Alice. I will share the spreadsheet detailing our budget options."},
                {"speaker": "Alice Smith", "time": 85, "text": "Excellent. We need to approve the budget allocations before the corporate sync."},
                {"speaker": "Emma Watson", "time": 140, "text": "I will draft the campaign slide deck and send it over for your feedback."}
            ],
            "action_items": [
                {"text": "Share the Q3 budget spreadsheet", "assignee": "Emma Watson", "completed": True},
                {"text": "Draft the marketing campaign slide deck", "assignee": "Emma Watson", "completed": False}
            ]
        },
        {
            "title": "Database Optimization Review",
            "date": datetime.now(timezone.utc) - timedelta(days=1),
            "duration": 2400,  # 40 mins
            "participants": ["Charlie Brown", "David Miller"],
            "summary": {
                "overview_text": "Tech sync to debug slow query issues on the cloud database. Discussed database indexing, connection pooling configuration, and Turso HTTP protocol redirects.",
                "key_topics": ["Slow Queries", "Indexing", "Turso Redirect Debugging"]
            },
            "transcript": [
                {"speaker": "Charlie Brown", "time": 20, "text": "Thanks for hopping on, David. Our queries to Turso are getting slow locally."},
                {"speaker": "David Miller", "time": 65, "text": "It looks like we are missing an index on the user_id foreign keys in our tables."},
                {"speaker": "Charlie Brown", "time": 120, "text": "I will add proper indexes to models.py and check query execution plans."},
                {"speaker": "David Miller", "time": 185, "text": "Excellent. I will also check if we are making HTTP requests instead of HTTPS, avoiding 308 redirects."}
            ],
            "action_items": [
                {"text": "Add database indexes to foreign key columns", "assignee": "Charlie Brown", "completed": False},
                {"text": "Enforce secure HTTPS protocols in the DB connection engine", "assignee": "David Miller", "completed": True}
            ]
        }
    ]

    for meeting_info in meetings_data:
        # Create meeting
        meeting = Meeting(
            title=meeting_info["title"],
            date=meeting_info["date"],
            duration=meeting_info["duration"],
            owner_id=demo_user.id
        )
        db.add(meeting)
        db.commit()
        db.refresh(meeting)

        # Add participants
        for name in meeting_info["participants"]:
            part = Participant(meeting_id=meeting.id, name=name)
            db.add(part)

        # Add transcript segments
        for seg in meeting_info["transcript"]:
            segment = TranscriptSegment(
                meeting_id=meeting.id,
                speaker_name=seg["speaker"],
                timestamp_seconds=seg["time"],
                text=seg["text"]
            )
            db.add(segment)

        # Add summary
        sum_data = meeting_info["summary"]
        summary = Summary(
            meeting_id=meeting.id,
            overview_text=sum_data["overview_text"],
            key_topics=sum_data["key_topics"]
        )
        db.add(summary)

        # Add action items
        for action in meeting_info["action_items"]:
            item = ActionItem(
                meeting_id=meeting.id,
                text=action["text"],
                assignee=action["assignee"],
                is_completed=action["completed"]
            )
            db.add(item)
            
        db.commit()

    print("Database seeding completed successfully!")
