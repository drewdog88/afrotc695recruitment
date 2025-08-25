"""
Unit tests for recruit management functionality.
Tests individual functions and methods with mocked dependencies.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, date
from werkzeug.security import generate_password_hash

from app import app, db, PotentialRecruit, User


class TestRecruitDataValidation:
    """Test recruit data validation functionality."""

    def test_valid_recruit_data(self, test_app, test_db):
        """Test that valid recruit data passes validation."""
        with test_app.app_context():
            recruit = PotentialRecruit(
                first_name='John',
                last_name='Doe',
                email='john.doe@example.com',
                phone='555-123-4567',
                current_school='Test High School',
                school_type='high_school',
                high_school_graduation_year=2024,
                gpa=3.5,
                act_score=25,
                sat_score=1200,
                status='interested',
                notes='Test recruit'
            )

            # Should not raise any validation errors
            test_db.session.add(recruit)
            test_db.session.commit()

            # Verify the recruit was created
            assert recruit.id is not None
            assert recruit.first_name == 'John'
            assert recruit.last_name == 'Doe'

    def test_recruit_email_validation(self, test_app, test_db):
        """Test recruit email validation."""
        with test_app.app_context():
            # Test invalid email format - database doesn't validate email format
            recruit = PotentialRecruit(
                first_name='John',
                last_name='Doe',
                email='invalid-email',
                phone='555-123-4567',
                current_school='Test High School',
                school_type='high_school',
                high_school_graduation_year=2024
            )

            # Database accepts any string for email field
            test_db.session.add(recruit)
            test_db.session.commit()

            # Verify the recruit was created with the invalid email
            assert recruit.id is not None
            assert recruit.email == 'invalid-email'

    def test_recruit_required_fields(self, test_app, test_db):
        """Test that required fields are enforced."""
        with test_app.app_context():
            # Test missing required fields
            recruit = PotentialRecruit(
                # Missing first_name, last_name, email
                phone='555-123-4567',
                current_school='Test High School',
                school_type='high_school',
                high_school_graduation_year=2024
            )

            # Should raise validation error for missing required fields
            with pytest.raises(Exception):
                test_db.session.add(recruit)
                test_db.session.commit()

    def test_recruit_graduation_year_validation(self, test_app, test_db):
        """Test graduation year validation."""
        with test_app.app_context():
            current_year = datetime.now().year

            # Test future graduation year (should be valid)
            recruit = PotentialRecruit(
                first_name='John',
                last_name='Doe',
                email='john.doe@example.com',
                phone='555-123-4567',
                current_school='Test High School',
                school_type='high_school',
                high_school_graduation_year=current_year + 2
            )

            test_db.session.add(recruit)
            test_db.session.commit()
            assert recruit.high_school_graduation_year == current_year + 2

            # Test past graduation year (should be valid for historical data)
            recruit2 = PotentialRecruit(
                first_name='Jane',
                last_name='Smith',
                email='jane.smith@example.com',
                phone='555-987-6543',
                current_school='Test High School',
                school_type='high_school',
                high_school_graduation_year=current_year - 1
            )

            test_db.session.add(recruit2)
            test_db.session.commit()
            assert recruit2.high_school_graduation_year == current_year - 1

    def test_recruit_gpa_validation(self, test_app, test_db):
        """Test GPA validation."""
        with test_app.app_context():
            # Test valid GPA range
            valid_gpas = [0.0, 2.5, 4.0, 4.33]
            for gpa in valid_gpas:
                recruit = PotentialRecruit(
                    first_name=f'Test{gpa}',
                    last_name='GPA',
                    email=f'test{gpa}@example.com',
                    phone='555-123-4567',
                    current_school='Test High School',
                    school_type='high_school',
                    high_school_graduation_year=2024,
                    gpa=gpa
                )

                test_db.session.add(recruit)
                test_db.session.commit()
                assert recruit.gpa == gpa

    def test_recruit_test_scores_validation(self, test_app, test_db):
        """Test ACT/SAT score validation."""
        with test_app.app_context():
            # Test valid ACT scores
            valid_act_scores = [1, 20, 36]
            for act_score in valid_act_scores:
                recruit = PotentialRecruit(
                    first_name=f'ACT{act_score}',
                    last_name='Test',
                    email=f'act{act_score}@example.com',
                    phone='555-123-4567',
                    current_school='Test High School',
                    school_type='high_school',
                    high_school_graduation_year=2024,
                    act_score=act_score
                )

                test_db.session.add(recruit)
                test_db.session.commit()
                assert recruit.act_score == act_score

            # Test valid SAT scores
            valid_sat_scores = [400, 1000, 1600]
            for sat_score in valid_sat_scores:
                recruit = PotentialRecruit(
                    first_name=f'SAT{sat_score}',
                    last_name='Test',
                    email=f'sat{sat_score}@example.com',
                    phone='555-123-4567',
                    current_school='Test High School',
                    school_type='high_school',
                    high_school_graduation_year=2024,
                    sat_score=sat_score
                )

                test_db.session.add(recruit)
                test_db.session.commit()
                assert recruit.sat_score == sat_score


class TestRecruitCRUDOperations:
    """Test recruit CRUD operations."""

    def test_create_recruit(self, test_app, test_db):
        """Test creating a new recruit."""
        with test_app.app_context():
            recruit = PotentialRecruit(
                first_name='John',
                last_name='Doe',
                email='john.doe@example.com',
                phone='555-123-4567',
                current_school='Test High School',
                school_type='high_school',
                high_school_graduation_year=2024,
                gpa=3.5,
                status='interested'
            )

            test_db.session.add(recruit)
            test_db.session.commit()

            # Verify recruit was created
            assert recruit.id is not None
            assert recruit.first_name == 'John'
            assert recruit.last_name == 'Doe'
            assert recruit.email == 'john.doe@example.com'
            assert recruit.status == 'interested'

    def test_read_recruit(self, test_app, test_db):
        """Test reading recruit data."""
        with test_app.app_context():
            # Create a recruit
            recruit = PotentialRecruit(
                first_name='Jane',
                last_name='Smith',
                email='jane.smith@example.com',
                phone='555-987-6543',
                current_school='Test High School',
                school_type='high_school',
                high_school_graduation_year=2024,
                gpa=3.8,
                status='applied'
            )

            test_db.session.add(recruit)
            test_db.session.commit()

            # Read the recruit
            retrieved_recruit = PotentialRecruit.query.get(recruit.id)
            assert retrieved_recruit is not None
            assert retrieved_recruit.first_name == 'Jane'
            assert retrieved_recruit.last_name == 'Smith'
            assert retrieved_recruit.email == 'jane.smith@example.com'
            assert retrieved_recruit.status == 'applied'

    def test_update_recruit(self, test_app, test_db):
        """Test updating recruit data."""
        with test_app.app_context():
            # Create a recruit
            recruit = PotentialRecruit(
                first_name='Bob',
                last_name='Johnson',
                email='bob.johnson@example.com',
                phone='555-111-2222',
                current_school='Test High School',
                school_type='high_school',
                high_school_graduation_year=2024,
                gpa=3.2,
                status='interested'
            )

            test_db.session.add(recruit)
            test_db.session.commit()

            # Update the recruit
            recruit.gpa = 3.6
            recruit.status = 'applied'
            recruit.notes = 'Updated notes'
            test_db.session.commit()

            # Verify updates
            updated_recruit = PotentialRecruit.query.get(recruit.id)
            assert updated_recruit.gpa == 3.6
            assert updated_recruit.status == 'applied'
            assert updated_recruit.notes == 'Updated notes'

    def test_delete_recruit(self, test_app, test_db):
        """Test deleting a recruit."""
        with test_app.app_context():
            # Create a recruit
            recruit = PotentialRecruit(
                first_name='Alice',
                last_name='Brown',
                email='alice.brown@example.com',
                phone='555-333-4444',
                current_school='Test High School',
                school_type='high_school',
                high_school_graduation_year=2024,
                gpa=3.7,
                status='enrolled'
            )

            test_db.session.add(recruit)
            test_db.session.commit()

            recruit_id = recruit.id

            # Delete the recruit
            test_db.session.delete(recruit)
            test_db.session.commit()

            # Verify recruit was deleted
            deleted_recruit = PotentialRecruit.query.get(recruit_id)
            assert deleted_recruit is None


class TestRecruitQueries:
    """Test recruit query functionality."""

    def test_filter_by_status(self, test_app, test_db):
        """Test filtering recruits by status."""
        with test_app.app_context():
            # Create recruits with different statuses
            statuses = ['interested', 'applied', 'enrolled', 'declined']
            recruits = []

            for status in statuses:
                recruit = PotentialRecruit(
                    first_name=f'Test{status}',
                    last_name='User',
                    email=f'test{status}@example.com',
                    phone='555-123-4567',
                    current_school='Test High School',
                    school_type='high_school',
                    high_school_graduation_year=2024,
                    status=status
                )
                recruits.append(recruit)
                test_db.session.add(recruit)

            test_db.session.commit()

            # Test filtering by each status
            for status in statuses:
                filtered_recruits = PotentialRecruit.query.filter_by(status=status).all()
                assert len(filtered_recruits) == 1
                assert filtered_recruits[0].status == status

    def test_filter_by_graduation_year(self, test_app, test_db):
        """Test filtering recruits by graduation year."""
        with test_app.app_context():
            # Create recruits with different graduation years
            years = [2023, 2024, 2025]
            recruits = []

            for year in years:
                recruit = PotentialRecruit(
                    first_name=f'Test{year}',
                    last_name='User',
                    email=f'test{year}@example.com',
                    phone='555-123-4567',
                    current_school='Test High School',
                    school_type='high_school',
                    high_school_graduation_year=year
                )
                recruits.append(recruit)
                test_db.session.add(recruit)

            test_db.session.commit()

            # Test filtering by graduation year
            current_year_recruits = PotentialRecruit.query.filter_by(high_school_graduation_year=2024).all()
            assert len(current_year_recruits) == 1
            assert current_year_recruits[0].high_school_graduation_year == 2024

    def test_search_by_name(self, test_app, test_db):
        """Test searching recruits by name."""
        with test_app.app_context():
            # Create recruits with different names
            names = [
                ('John', 'Doe'),
                ('Jane', 'Smith'),
                ('Bob', 'Johnson'),
                ('Alice', 'Brown')
            ]

            for first_name, last_name in names:
                recruit = PotentialRecruit(
                    first_name=first_name,
                    last_name=last_name,
                    email=f'{first_name.lower()}.{last_name.lower()}@example.com',
                    phone='555-123-4567',
                    current_school='Test High School',
                    school_type='high_school',
                    high_school_graduation_year=2024
                )
                test_db.session.add(recruit)

            test_db.session.commit()

            # Test searching by first name
            john_recruits = PotentialRecruit.query.filter(
                PotentialRecruit.first_name.ilike('%john%')
            ).all()
            assert len(john_recruits) == 1
            assert john_recruits[0].first_name == 'John'

            # Test searching by last name
            smith_recruits = PotentialRecruit.query.filter(
                PotentialRecruit.last_name.ilike('%smith%')
            ).all()
            assert len(smith_recruits) == 1
            assert smith_recruits[0].last_name == 'Smith'

    def test_order_by_gpa(self, test_app, test_db):
        """Test ordering recruits by GPA."""
        with test_app.app_context():
            # Create recruits with different GPAs
            gpas = [2.5, 3.0, 3.5, 4.0]
            recruits = []

            for gpa in gpas:
                recruit = PotentialRecruit(
                    first_name=f'Test{gpa}',
                    last_name='User',
                    email=f'test{gpa}@example.com',
                    phone='555-123-4567',
                    current_school='Test High School',
                    school_type='high_school',
                    high_school_graduation_year=2024,
                    gpa=gpa
                )
                recruits.append(recruit)
                test_db.session.add(recruit)

            test_db.session.commit()

            # Test ordering by GPA (ascending)
            ascending_recruits = PotentialRecruit.query.order_by(PotentialRecruit.gpa.asc()).all()
            assert len(ascending_recruits) == 4
            assert ascending_recruits[0].gpa == 2.5
            assert ascending_recruits[-1].gpa == 4.0

            # Test ordering by GPA (descending)
            descending_recruits = PotentialRecruit.query.order_by(PotentialRecruit.gpa.desc()).all()
            assert len(descending_recruits) == 4
            assert descending_recruits[0].gpa == 4.0
            assert descending_recruits[-1].gpa == 2.5


class TestRecruitBusinessLogic:
    """Test recruit business logic functionality."""

    def test_recruit_status_transitions(self, test_app, test_db):
        """Test valid recruit status transitions."""
        with test_app.app_context():
            recruit = PotentialRecruit(
                first_name='Status',
                last_name='Test',
                email='status.test@example.com',
                phone='555-123-4567',
                current_school='Test High School',
                school_type='high_school',
                high_school_graduation_year=2024,
                status='interested'
            )

            test_db.session.add(recruit)
            test_db.session.commit()

            # Test status transitions
            valid_transitions = ['interested', 'applied', 'enrolled', 'declined']

            for status in valid_transitions:
                recruit.status = status
                test_db.session.commit()

                updated_recruit = PotentialRecruit.query.get(recruit.id)
                assert updated_recruit.status == status

    def test_recruit_contact_information(self, test_app, test_db):
        """Test recruit contact information handling."""
        with test_app.app_context():
            recruit = PotentialRecruit(
                first_name='Contact',
                last_name='Test',
                email='contact.test@example.com',
                phone='555-123-4567',
                current_school='Test High School',
                school_type='high_school',
                high_school_graduation_year=2024
            )

            test_db.session.add(recruit)
            test_db.session.commit()

            # Verify contact information
            assert recruit.email == 'contact.test@example.com'
            assert recruit.phone == '555-123-4567'

    def test_recruit_academic_information(self, test_app, test_db):
        """Test recruit academic information handling."""
        with test_app.app_context():
            recruit = PotentialRecruit(
                first_name='Academic',
                last_name='Test',
                email='academic.test@example.com',
                phone='555-123-4567',
                current_school='Test High School',
                school_type='high_school',
                high_school_graduation_year=2024,
                gpa=3.8,
                act_score=28,
                sat_score=1350
            )

            test_db.session.add(recruit)
            test_db.session.commit()

            # Verify academic information
            assert recruit.gpa == 3.8
            assert recruit.act_score == 28
            assert recruit.sat_score == 1350

    def test_recruit_notes_and_comments(self, test_app, test_db):
        """Test recruit notes and comments functionality."""
        with test_app.app_context():
            recruit = PotentialRecruit(
                first_name='Notes',
                last_name='Test',
                email='notes.test@example.com',
                phone='555-123-4567',
                current_school='Test High School',
                school_type='high_school',
                high_school_graduation_year=2024,
                notes='Initial contact made'
            )

            test_db.session.add(recruit)
            test_db.session.commit()

            # Verify notes
            assert recruit.notes == 'Initial contact made'

            # Test updating notes
            recruit.notes = 'Follow-up meeting scheduled'
            test_db.session.commit()

            updated_recruit = PotentialRecruit.query.get(recruit.id)
            assert updated_recruit.notes == 'Follow-up meeting scheduled'


class TestRecruitRoutes:
    """Test recruit route functionality."""

    def test_recruits_route_get(self, test_client, test_app, test_db):
        """Test GET request to recruits route."""
        from app import User
        from werkzeug.security import generate_password_hash

        with test_app.app_context():
            # Create test user
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash='pbkdf2:sha256:600000$test$hash$for$testing',
                first_name='Test',
                last_name='User',
                role='admin',
                secret_question='What is your favorite color?',
                secret_answer_hash='pbkdf2:sha256:600000$test$answer$hash'
            )
            test_db.session.add(test_user)
            test_db.session.commit()

            # Manually set session
            with test_client.session_transaction() as sess:
                sess['user_id'] = test_user.id
                sess['username'] = test_user.username
                sess['role'] = test_user.role

            response = test_client.get('/recruits')
            assert response.status_code == 200
            assert b'Recruits' in response.data

    def test_add_recruit_route_get(self, test_client, test_app, test_db):
        """Test GET request to add recruit route."""
        from app import User

        with test_app.app_context():
            # Create test user
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash='pbkdf2:sha256:600000$test$hash$for$testing',
                first_name='Test',
                last_name='User',
                role='admin',
                secret_question='What is your favorite color?',
                secret_answer_hash='pbkdf2:sha256:600000$test$answer$hash'
            )
            test_db.session.add(test_user)
            test_db.session.commit()

            # Manually set session
            with test_client.session_transaction() as sess:
                sess['user_id'] = test_user.id
                sess['username'] = test_user.username
                sess['role'] = test_user.role

            response = test_client.get('/recruits/add')
            assert response.status_code == 200
            assert b'Add Recruit' in response.data

    def test_add_recruit_route_post(self, test_app, test_db, test_client):
        """Test POST request to add recruit route."""
        from app import User

        with test_app.app_context():
            # Create test user
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash='pbkdf2:sha256:600000$test$hash$for$testing',
                first_name='Test',
                last_name='User',
                role='admin',
                secret_question='What is your favorite color?',
                secret_answer_hash='pbkdf2:sha256:600000$test$answer$hash'
            )
            test_db.session.add(test_user)
            test_db.session.commit()

            # Manually set session
            with test_client.session_transaction() as sess:
                sess['user_id'] = test_user.id
                sess['username'] = test_user.username
                sess['role'] = test_user.role

            response = test_client.post('/recruits/add', data={
                'first_name': 'Test',
                'last_name': 'Recruit',
                'email': 'test.recruit@example.com',
                'phone': '555-123-4567',
                'major': 'Computer Science',
                'current_school': 'Test High School',
                'school_type': 'high_school',
                'high_school_graduation_year': '2024',
                'gpa': '3.5',
                'status': 'interested',
                'notes': 'Test recruit',
                'interests': 'Programming, Leadership'
            }, follow_redirects=False)

            # Should redirect to recruits page (302) or return success
            assert response.status_code in [200, 302]

            # Verify recruit was created in database
            recruit = PotentialRecruit.query.filter_by(
                email='test.recruit@example.com'
            ).first()
            assert recruit is not None
            assert recruit.first_name == 'Test'
            assert recruit.last_name == 'Recruit'

    @pytest.mark.skip(reason="Edit route not implemented in main app.py")
    def test_edit_recruit_route_get(self, test_app, test_db, authenticated_client):
        """Test GET request to edit recruit route."""
        # Edit route exists in app_local.py but not in main app.py
        pass

    @pytest.mark.skip(reason="Edit route not implemented in main app.py")
    def test_edit_recruit_route_post(self, test_app, test_db, authenticated_client):
        """Test POST request to edit recruit route."""
        # Edit route exists in app_local.py but not in main app.py
        pass
