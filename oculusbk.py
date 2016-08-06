from flask import Flask, request, redirect, url_for, render_template, flash, g
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from sqlalchemy import func
from utils import *

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'login'

# or set directly on the app
# app.secret_key = os.urandom(24)
app.secret_key = 'some_secret'


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/welcome')
@login_required
def welcome():
    isp_entries, services_entries, ratings_entries, servicemetric_entries = dropdown()
    return render_template('welcome.html', isp_entries=isp_entries, services_entries=services_entries,
                           ratings_entries=ratings_entries, servicemetric_entries=servicemetric_entries)


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/view_my_ratings', methods=['GET', 'POST'])
@login_required
def view_my_ratings():
    # my_service_ratings = Service_metric_ratings.query.filter_by(user_id=g.user.user_id).order_by(
    # Service_metric_ratings.pub_date.desc()).all()

    my_service_ratings = db.session.query(User.email, Isps.isp_name, Service_metric.metric_name, Services.service_name,
                                          Ratings.rating_value, Ratings.rating_comment,
                                          Service_metric_ratings.custom_rating_comment, Service_metric_ratings.pub_date) \
        .filter(Service_metric_ratings.user_id == User.user_id) \
        .filter(Service_metric_ratings.ratings_id == Ratings.ratings_id) \
        .filter(Service_metric_ratings.service_id == Services.service_id) \
        .filter(Service_metric_ratings.metric_id == Service_metric.metric_id) \
        .filter(Service_metric_ratings.isp_id == Isps.isp_id) \
        .filter_by(user_id=g.user.user_id) \
        .order_by(Service_metric_ratings.pub_date.desc()).all()

    # for i in my_service_ratings:
    # print i.Isps.isp_name

    return render_template('view_my_ratings.html', my_service_ratings=my_service_ratings)


@app.route('/build_service_report', methods=['GET', 'POST'])
@login_required
def build_service_report():
    isp_entries, services_entries, ratings_entries, servicemetric_entries = dropdown()
    return render_template('query_average_isp_ratings.html', isp_entries=isp_entries, services_entries=services_entries,
                           servicemetric_entries=servicemetric_entries)


@app.route('/view_average_isp_ratings', methods=['GET', 'POST'])
@login_required
def view_average_isp_ratings():
    if request.method == 'GET':
        return render_template('query_average_isp_ratings.html')
    metric_name = request.form['metric_name']
    isp_name = request.form['isp_name']
    service_name = request.form['service_name']
    if not metric_name:
        flash('KPI is required', 'danger')
    elif not isp_name:
        flash('ISP is required', 'danger')
    elif not service_name:
        flash('service_name is required', 'danger')
    else:
        ratings_table_values = db.session.query(Ratings.rating_value, Ratings.rating_comment)

        isp_ratings_per_service = db.session.query(User.email, Isps.isp_name, Service_metric.metric_name, Services.service_name,
                                                   Ratings.rating_value) \
            .filter(Service_metric_ratings.isp_id == Isps.isp_id) \
            .filter(Service_metric_ratings.ratings_id == Ratings.ratings_id) \
            .filter(Service_metric_ratings.metric_id == Service_metric.metric_id) \
            .filter(Service_metric_ratings.user_id == User.user_id) \
            .filter(Service_metric_ratings.service_id == Services.service_id) \
            .filter(Service_metric.metric_name == metric_name) \
            .filter(Services.service_name == service_name) \
            .filter(Isps.isp_name == isp_name)

        cursor = db.session.query(func.sum(Service_metric_ratings.ratings_id)) \
            .filter(Service_metric_ratings.isp_id == Isps.isp_id) \
            .filter(Service_metric_ratings.ratings_id == Ratings.ratings_id) \
            .filter(Service_metric_ratings.metric_id == Service_metric.metric_id) \
            .filter(Service_metric_ratings.user_id == User.user_id) \
            .filter(Service_metric_ratings.service_id == Services.service_id) \
            .filter(Service_metric.metric_name == metric_name) \
            .filter(Services.service_name == service_name) \
            .filter(Isps.isp_name == isp_name)

        total_ratings = cursor.scalar()
        count_of_users_who_rated = isp_ratings_per_service.count()
        average_isp__service_ratings = 0

        if count_of_users_who_rated <= 0:
            return render_template('view_average_isp_ratings.html',
                                   isp_ratings_per_service=isp_ratings_per_service,
                                   count_of_users_who_rated=count_of_users_who_rated,
                                   average_isp__service_ratings=average_isp__service_ratings,
                                   ratings_table_values=ratings_table_values)
        else:
            average_isp__service_ratings = total_ratings / count_of_users_who_rated
            return render_template('view_average_isp_ratings.html',
                                   isp_ratings_per_service=isp_ratings_per_service,
                                   count_of_users_who_rated=count_of_users_who_rated,
                                   average_isp__service_ratings=average_isp__service_ratings,
                                   ratings_table_values=ratings_table_values)


@app.route('/rate_isp_service', methods=['GET', 'POST'])
@login_required
def rate_isp_service():
    isp_entries, services_entries, ratings_entries, servicemetric_entries = dropdown()
    if request.method == 'POST':
        metric_id = request.form['metric_id']
        isp_id = request.form['isp_id']
        service_id = request.form['service_id']
        ratings_id = request.form['ratings_id']
        custom_rating_comment = request.form['custom_rating_comment']
        if not metric_id:
            flash('KPI is required', 'danger')
        elif not isp_id:
            flash('ISP is required', 'danger')
        elif not service_id:
            flash('service_name is required', 'danger')
        elif not ratings_id:
            flash('ratings_id is required', 'danger')
        elif not custom_rating_comment:
            flash('custom_rating_comment is required', 'danger')
        else:
            user_service_ratings = Service_metric_ratings(metric_id, isp_id, service_id, ratings_id,
                                                          custom_rating_comment)

            exists = db.session.query(Service_metric_ratings.user_id, Service_metric_ratings.metric_id, Service_metric_ratings.service_id,
                                      Service_metric_ratings.isp_id) \
                .filter(Service_metric_ratings.metric_id == metric_id, \
                        Service_metric_ratings.isp_id == isp_id, \
                        Service_metric_ratings.service_id == service_id) \
                .filter_by(user_id=g.user.user_id).count()

            if exists:
                flash('You have already provided ratings for this service , edit it instead', 'danger')
            else:
                user_service_ratings.user = g.user
                db.session.add(user_service_ratings)
                db.session.commit()
                flash('Data successfully Added', 'success')
    return render_template('rate_isp_service.html', isp_entries=isp_entries, services_entries=services_entries,
                           ratings_entries=ratings_entries, servicemetric_entries=servicemetric_entries)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    password = request.form['password']
    email = request.form['email']
    user = User(password, email)
    exists = db.session.query(User.user_id).filter_by(email=email).scalar() is not None
    if exists:
        flash(email + ' is already registered , Login if you remember the password ', 'danger')
        return render_template('login.html')
    else:
        db.session.add(user)
        db.session.commit()
        flash('User successfully registered', 'success')
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    email = request.form['email']
    password = request.form['password']
    remember_me = False
    if 'remember_me' in request.form:
        remember_me = True
    registered_user = User.query.filter_by(email=email).first()
    if registered_user is None:
        flash('Your Username and Password dont exist', 'danger')
        return redirect(url_for('login'))
    if not registered_user.check_password(password):
        flash('Password is invalid', 'danger')
        return redirect(url_for('login'))
    else:
        login_user(registered_user, remember=remember_me)
        # flash('Thank you ' + email + ' for using our site ,we greatly appreciate you sharing your experiences', 'success')
        return redirect(request.args.get('next') or url_for('welcome'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out ,thank you for your contribution', 'success')
    return redirect(url_for('login'))


@login_manager.user_loader
def user_loader(email):
    """Given *user_id*, return the associated User object.
       :param unicode user_id: user_id (email) user to retrieve
      """
    return User.query.get(str(email))


@app.before_request
def before_request():
    g.user = current_user


if __name__ == '__main__':
    app.run(debug=True)