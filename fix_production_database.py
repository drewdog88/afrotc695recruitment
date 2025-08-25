#!/usr/bin/env python3
"""Fix production database issues"""

from app import app, db, User
from werkzeug.security import generate_password_hash
import traceback

def fix_database():
    print("🔧 Fixing production database issues...")

    try:
        with app.app_context():
            # 1. Update password hash field lengths
            print("1. Updating password hash field lengths...")
            db.session.execute("""
                ALTER TABLE "user" ALTER COLUMN password_hash TYPE VARCHAR(500);
                ALTER TABLE "user" ALTER COLUMN secret_answer_hash TYPE VARCHAR(500);
            """)

            db.session.execute("""
                ALTER TABLE password_history ALTER COLUMN password_hash TYPE VARCHAR(500);
            """)

            db.session.commit()
            print("✅ Password hash fields updated")

            # 2. Create missing tables
            print("2. Creating missing tables...")
            db.create_all()
            print("✅ All tables created")

            # 3. Check if admin user exists
            print("3. Checking for admin user...")
            admin_user = User.query.filter_by(username='admin').first()

            if not admin_user:
                print("Creating admin user...")
                admin_user = User(
                    username='admin',
                    password_hash=generate_password_hash('admin123'),
                    first_name='Admin',
                    last_name='User',
                    email='admin@afrotc695.com',
                    role='admin',
                    secret_question='What is your favorite color?',
                    secret_answer_hash=generate_password_hash('blue')
                )

                db.session.add(admin_user)
                db.session.commit()
                print("✅ Admin user created")
                print("Username: admin")
                print("Password: admin123")
            else:
                print("✅ Admin user already exists")

            # 4. Verify tables exist
            print("4. Verifying tables...")
            tables = db.session.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('user', 'potential_recruit', 'cadet', 'contact', 'calendar_event', 'external_link', 'recruitment_document', 'activity_log', 'password_history')
                ORDER BY table_name;
            """).fetchall()

            print("Found tables:")
            for table in tables:
                print(f"  - {table[0]}")

            # 5. Test basic queries
            print("5. Testing basic queries...")
            user_count = User.query.count()
            print(f"✅ User count: {user_count}")

            return True

    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        db.session.rollback()
        return False

if __name__ == "__main__":
    success = fix_database()
    if success:
        print("\n🎉 Database fixed successfully!")
        print("You should now be able to login with:")
        print("Username: admin")
        print("Password: admin123")
    else:
        print("\n💥 Database fix failed!")
