from extensions import db


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    nick_name = db.Column(db.String(25), nullable=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    fname = db.Column(db.String(25), nullable=False)
    lname = db.Column(db.String(25), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    location_title = db.Column(db.String(125), nullable=False)
    address = db.Column(db.String(256), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    company = db.Column(db.String(50), nullable=True)
    # title = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'nick_name': self.nick_name,
            'fname': self.fname,
            'lname': self.lname,
            'mobile': self.mobile,
            'location_title': self.location_title,
            'address': self.address,
            'city': self.city,
            'company': self.company,
            # 'title': self.title,
            'email': self.email
        }

    def __repr__(self):
        return f"<User {self.nick_name}>"
