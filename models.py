from . import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import CheckConstraint

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='employee', nullable=False)

    __table_args__ = (
        CheckConstraint(role.in_(['admin', 'employee']), name='valid_role_check'),
    )

    def __init__(self, email, password, name, role=None):
        self.email = email
        self.password = password
        self.name = name
        if role:
            self.role = role

    def is_admin(self):
        return self.role == 'admin'

    def is_employee(self):
        return self.role == 'employee'


class LeaveApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_from = db.Column(db.Date, nullable=False)
    date_to = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='Pending')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('leave_applications', lazy=True))
    
    __table_args__ = (
        CheckConstraint(status.in_(['Approved', 'pending', 'Rejected']), name='valid_status_check'),
    )
    def __init__(self, date_from, date_to, reason, user_id, status=None):
        # Convert date_from and date_to strings to date objects
        self.date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        self.date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        self.reason = reason
        self.user_id = user_id
        if status:
            self.status = status

    def __repr__(self):
        return f"LeaveApplication({self.date_from}, {self.date_to}, {self.reason}, {self.status})"