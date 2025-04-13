from extensions import db, bcrypt
from models.user import User
import re
from utils import message_helper


def get_all_users():
    try:
        users = User.query.all()  # Use the SQLAlchemy ORM to retrieve all users
        return users
    except Exception as e:
        print(f"Error occurred: {e}")
        return [e]  # You can customize this response or log the error


def create_user(nick_name, fname, lname, mobile, location_title, address, city, company, email, password):
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        user = User(
            nick_name=nick_name,
            fname=fname,
            lname=lname,
            mobile=mobile,
            location_title=location_title,
            address=address,
            city=city,
            company=company,
            email=email,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()

        return {'message': message_helper.SUCCESS_USER_CREATED, 'user': user.to_dict()}
    except Exception as e:
        print(f"Error occurred: {e}")
        return {'error': str(e)}


def get_user_by_email(email):
    try:
        user = User.query.filter_by(email=email).first()
        if user:
            return user.to_dict()
        else:
            return {'error': message_helper.ERROR_USER_NOT_FOUND}

    except Exception as e:
        print(f"Error occurred: {e}")
        return {'error': str(e)}


def reset_password(email, existing_password, new_password):
    try:
        is_valid_user = validate_user(email, existing_password)
        if is_valid_user:
            user = User.query.filter_by(email=email).first()
            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            return {'message': message_helper.SUCCESS_PASSWORD_RESET}
        else:
            return {'error': message_helper.ERROR_INVALID_USERNAME_OR_PASSWORD}

    except Exception as e:
        print(f"Error occurred: {e}")
        return {'error': str(e)}, 500


def validate_user(email, password):
    try:
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return True
        else:
            return False
    except Exception as e:
        print(f"Error occurred: {e}")
        return False


def is_valid_password(password):
    """
    Function to validate password
    Check if the password length is at least 8 characters
    """
    if len(password) < 8:
        return False

    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False

    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False

    # Check for at least one digit
    if not re.search(r'[0-9]', password):
        return False

    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False

    # If all conditions are met, return True
    return True


def is_valid_email(email):
    """
    Function to validate email
    Check if the email is valid
    """
    pattern = r"^[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if not re.match(pattern, email):
        if '@' not in email:
            # print("Email must contain '@'")
            return False

        username, domain = email.split('@', 1)
        if not username:
            # print("Email must contain a username before '@'")
            return False

        if '.' not in domain or len(domain.split('.')[0]) == 0:
            # print("Invalid domain format")
            return False

    # If all conditions are met, return True
    return True
