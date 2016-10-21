from flask import Flask, request, redirect, url_for, render_template, flash, g
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from forms import SignupForm
from sqlalchemy import func
from utils import *

application = Flask(__name__)
application.secret_key = 'A0Zr98j/3yXR~XHH!jmN]LWX/,?RT'
login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = '/login'


@application.route('/')
def index():
    return render_template('home.html')


@application.route('/welcome')
@login_required
def welcome():
    isp_entries, services_entries, ratings_entries, servicemetric_entries = dropdown()
    return render_template('welcome.html', isp_entries=isp_entries, services_entries=services_entries,
                           ratings_entries=ratings_entries, servicemetric_entries=servicemetric_entries)


@application.route('/react')
def react():
    return render_template('react.html')


@application.route('/survey')
@login_required
def survey():
    isp_entries, services_entries, ratings_entries, servicemetric_entries = dropdown()
    return render_template('take_survey.html', isp_entries=isp_entries, services_entries=services_entries,
                           ratings_entries=ratings_entries, servicemetric_entries=servicemetric_entries)


@application.route('/home')
def home():
    return render_template('home.html')



@application.route('/isp_portal')
def isp_portal():
    return render_template('isp_portal.html')


@application.route('/view_my_ratings', methods=['GET', 'POST'])
@login_required
def view_my_ratings():
    # my_service_ratings = Service_metric_ratings.query.filter_by(user_id=g.user.user_id).order_by(
    # Service_metric_ratings.pub_date.desc()).all()
    my_service_ratings = db.session.query(User.email, Isps.isp_name, Service_metric.metric_name, Services.service_name,
                                          Ratings.ratings_value, Ratings.ratings_comment,
                                          Service_metric_ratings.custom_rating_comment, Service_metric_ratings.pub_date) \
        .filter(Service_metric_ratings.user_id == User.user_id) \
        .filter(Service_metric_ratings.ratings_value == Ratings.ratings_value) \
        .filter(Service_metric_ratings.service_id == Services.service_id) \
        .filter(Service_metric_ratings.metric_id == Service_metric.metric_id) \
        .filter(Service_metric_ratings.isp_id == Isps.isp_id) \
        .filter_by(user_id=g.user.user_id) \
        .order_by(Service_metric_ratings.pub_date.desc()).all()

    # for i in my_service_ratings:
    # print i.Isps.isp_name

    return render_template('view_my_ratings.html', my_service_ratings=my_service_ratings)


@application.route('/build_service_report', methods=['GET', 'POST'])
@login_required
def build_service_report():
    isp_entries, services_entries, ratings_entries, servicemetric_entries = dropdown()
    return render_template('query_average_isp_ratings.html', isp_entries=isp_entries, services_entries=services_entries,
                           servicemetric_entries=servicemetric_entries)


@application.route('/view_average_isp_ratings', methods=['GET', 'POST'])
@login_required
def view_average_isp_ratings():
    if request.method == 'GET':
        return render_template('query_average_isp_ratings.html')
    metric_name = request.form['metric_name']
    service_name = request.form['service_name']
    if not metric_name:
        flash('KPI is required', 'danger')
    elif not service_name:
        flash('service_name is required', 'danger')
    else:
        isp_ratings_per_service = db.session.query(func.count(Ratings.ratings_value).label('count_of_users'),
                                                   func.sum(Ratings.ratings_value).label('sum_of_ratings'),
                                                   func.avg(Ratings.ratings_value).label('avg_of_ratings'),
                                                   Isps.isp_name, Service_metric.metric_name, Services.service_name) \
            .filter(Service_metric_ratings.isp_id == Isps.isp_id) \
            .filter(Service_metric_ratings.ratings_value == Ratings.ratings_value) \
            .filter(Service_metric_ratings.metric_id == Service_metric.metric_id) \
            .filter(Service_metric_ratings.user_id == User.user_id) \
            .filter(Service_metric_ratings.service_id == Services.service_id) \
            .filter(Service_metric.metric_name == metric_name) \
            .filter(Services.service_name == service_name) \
            .group_by(Isps.isp_name)

        ratings_table_values = db.session.query(Ratings.ratings_value, Ratings.ratings_comment)
        # for i in isp_ratings_per_service:
        # print(i.isp_name, i.service_name, i.metric_name, (round(i.avg_of_ratings)))
        # ratings_table_values = Ratings.query.filter_by(rating_value=(round(i.avg_of_ratings)))

        return render_template('view_average_isp_ratings.html',
                               isp_ratings_per_service=isp_ratings_per_service,
                               ratings_table_values=ratings_table_values)


@application.route('/rate_isp_service', methods=['GET', 'POST'])
@login_required
def rate_isp_service():
    isp_entries, services_entries, ratings_entries, servicemetric_entries = dropdown()
    if request.method == 'POST':
        metric_id = request.form['metric_id']
        isp_id = request.form['isp_id']
        service_id = request.form['service_id']
        ratings_value = request.form['ratings_value']
        custom_rating_comment = request.form['custom_rating_comment']
        if not metric_id:
            flash('KPI is required', 'danger')
        elif not isp_id:
            flash('ISP is required', 'danger')
        elif not service_id:
            flash('service_name is required', 'danger')
        elif not ratings_value:
            flash('ratings_id is required', 'danger')
        elif not custom_rating_comment:
            flash('custom_rating_comment is required', 'danger')
        else:
            user_service_ratings = Service_metric_ratings(metric_id, isp_id, service_id, ratings_value,
                                                          custom_rating_comment)

            exists = db.session.query(Service_metric_ratings.user_id, Service_metric_ratings.metric_id, Service_metric_ratings.service_id,
                                      Service_metric_ratings.isp_id) \
                .filter(Service_metric_ratings.metric_id == metric_id,
                        Service_metric_ratings.isp_id == isp_id,
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


@application.route('/rate_isp_service_multiple', methods=['GET', 'POST'])
@login_required
def rate_isp_service_multiple():
    isp_entries, services_entries, ratings_entries, servicemetric_entries = dropdown()

    if request.method == 'POST':
        metric_id = request.form['metric_id']
        isp_id = request.form['isp_id']
        service_id = request.form['service_id']
        ratings_value = request.form['ratings_value']
        custom_rating_comment = request.form['custom_rating_comment']
        if not metric_id:
            flash('KPI is required', 'danger')
        elif not isp_id:
            flash('ISP is required', 'danger')
        elif not service_id:
            flash('service_name is required', 'danger')
        elif not ratings_value:
            flash('ratings_id is required', 'danger')
        elif not custom_rating_comment:
            flash('custom_rating_comment is required', 'danger')
        else:
            user_service_ratings = Service_metric_ratings(metric_id, isp_id, service_id, ratings_value,
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
    return render_template('rate_isp_service_multiple.html', isp_entries=isp_entries, services_entries=services_entries,
                           ratings_entries=ratings_entries, servicemetric_entries=servicemetric_entries)


# @app.route('/register', methods=['GET', 'POST'])
# def register():
# if request.method == 'GET':
# return render_template('register.html')
# password = request.form['password']
# email = request.form['email']
# user = User(password, email)
# exists = db.session.query(User.user_id).filter_by(email=email).scalar() is not None
#     if exists:
#         flash(email + ' is already registered , Login if you remember the password ', 'danger')
#         return render_template('login.html')
#     else:
#         db.session.add(user)
#         db.session.commit()
#         flash('User successfully registered', 'success')
#     return redirect(url_for('login'))


@application.route('/register', methods=['GET', 'POST'])
def register():
    form = SignupForm()
    if g.user.is_authenticated:
        return redirect(url_for('welcome'))

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('register.html', form=form)
        else:
            newuser = User(form.password.data, form.email.data)
            db.session.add(newuser)
            db.session.commit()

            current_user = newuser.email
            if current_user:
                return redirect(url_for('welcome'))

    elif request.method == 'GET':
        return render_template('register.html', form=form)


@application.route('/login', methods=['GET', 'POST'])
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
    return redirect(request.args.get('next') or url_for('rate_isp_service'))


@application.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out ,thank you for your contribution', 'success')
    return redirect(url_for('login'))


#!py
@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve
    """
    return User.query.get(user_id)



@application.before_request
def before_request():
    g.user = current_user


if __name__ == '__main__':
    application.run(debug=True)