from extensions import db

class Postings(db.Model):
    __tablename__ = 'postings'

    postings_id = db.Column(db.Integer, primary_key=True)
    donor_user_id = db.Column(db.Integer, nullable=False)
    post_title = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    pick_up_location = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    post_status = db.Column(db.String(50), nullable=False)
    post_date = db.Column(db.Date, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)