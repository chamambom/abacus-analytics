from database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column('user_id', db.Integer, primary_key=True)
    email = db.Column('email', db.String(50), unique=True, index=True)
    password = db.Column('password', db.String(10))
    registered_on = db.Column('registered_on', db.DateTime, default=datetime.utcnow())

    # Defining One to Many relationships with the relationship function on the Parent Table
    service_metric_ratings = db.relationship('Service_metric_ratings', backref="user", cascade="all, delete-orphan",
                                             lazy='dynamic')

    def __init__(self, password, email):
        self.set_password(password)
        self.email = email
        self.registered_on = datetime.utcnow()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.user_id)

    def __repr__(self):
        return '<User %r>' % (self.user_id)


class Isps(db.Model):
    __tablename__ = "isps"
    isp_id = db.Column('isp_id', db.Integer, primary_key=True)
    isp_name = db.Column('isp_name', db.String(80), unique=True)
    isp_description = db.Column('isp_description', db.Unicode)

    def __init__(self, isp_name, isp_description):
        self.isp_name = isp_name
        self.isp_description = isp_description

    def __repr__(self):
        return '<Isps %r>' % self.isp_name


class Service_catergory(db.Model):
    __tablename__ = "service_catergory"
    service_catergory_id = db.Column('service_catergory_id', db.Integer, primary_key=True)
    service_catergory_name = db.Column('service_catergory_name', db.String(80), unique=True)

    def __init__(self, service_catergory_name):
        self.service_catergory_name = service_catergory_name

    def __repr__(self):
        return '<Service_catergory %r>' % self.service_catergory_name


class Services(db.Model):
    __tablename__ = "services"
    service_id = db.Column('service_id', db.Integer, primary_key=True)
    service_name = db.Column('service_name', db.String(80), unique=True)
    # Defining the Foreign Key on the Child Table
    service_catergory_id = db.Column(db.Integer, db.ForeignKey('service_catergory.service_catergory_id'))

    def __init__(self, service_name):
        self.service_name = service_name

    def __repr__(self):
        return '<Services %r>' % self.service_name


class Service_metric(db.Model):
    __tablename__ = "service_metric"
    metric_id = db.Column('metric_id', db.Integer, primary_key=True)
    metric_name = db.Column('metric_name', db.String(80), unique=True)
    metric_description = db.Column('metric_description', db.Unicode)

    def __init__(self, metric_name, metric_description):
        self.metric_name = metric_name
        self.metric_description = metric_description

    def __repr__(self):
        return '<Service_metric %r>' % self.metric_name


class Ratings(db.Model):
    __tablename__ = "ratings"
    ratings_value = db.Column('ratings_value', db.Integer, primary_key=True)
    ratings_comment = db.Column('ratings_comment', db.String(120), unique=False)

    def __init__(self, ratings_comment):
        self.ratings_comment = ratings_comment

    def __repr__(self):
        return '<Ratings %r>' % self.ratings_value


class Service_metric_ratings(db.Model):
    __tablename__ = "service_metric_ratings"
    service_metric_rate_id = db.Column('service_metric_rate_id', db.Integer, primary_key=True)
    pub_date = db.Column('pub_date', db.DateTime, default=datetime.utcnow())
    custom_rating_comment = db.Column('custom_rating_comment', db.String(80), unique=False)
    # Defining the Foreign Key on the Child Table
    metric_id = db.Column(db.Integer, db.ForeignKey('service_metric.metric_id'))
    isp_id = db.Column(db.Integer, db.ForeignKey('isps.isp_id'))
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'))
    ratings_value = db.Column(db.Integer, db.ForeignKey('ratings.ratings_value'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))


    def __init__(self, metric_id, isp_id, service_id, ratings_value, custom_rating_comment):
        self.custom_rating_comment = custom_rating_comment
        self.metric_id = metric_id
        self.isp_id = isp_id
        self.service_id = service_id
        self.ratings_value = ratings_value
        self.pub_date = datetime.utcnow()


    def __repr__(self):
        return '<Service_metric_ratings %r>' % self.service_metric_rate_id




