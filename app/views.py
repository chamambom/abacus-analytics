from flask import request, redirect, url_for, render_template, flash, render_template_string
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy import func
from app.forms import SignupForm, LoginForm, MultipleCheckBoxes
from app.models import User, Services, Service_metric_ratings, Ratings, Kpis, Kpi_ratings, Isps, Service_metric, \
    Isp_service
from app import application, db, mail, Message
import pygal


@application.route('/')
def index():
    return render_template('home.html')


@application.route('/add_your_subscribed_isp_services')
@login_required
def add_your_subscribed_isp_services():
    return render_template('add_your_subscribed_isp_services.html')


@application.route('/current_subscribed_isp_service', methods=['GET', 'POST'])
@login_required
def current_subscribed_isp_service():
    if request.method == 'POST':
        checkbox_values = request.form.getlist('service_name')
        # checkbox_values = dict((key, request.form.getlist(key)) for key in request.form.keys()
        for elem in checkbox_values:
            values = eval(elem) + (current_user.user_id,)
            isp_id = values[0]
            service_id = values[1]
            user_id = values[2]

            exists = db.session.query(Isp_service.user_id, Isp_service.isp_id, Isp_service.user_id) \
                .filter(Isp_service.isp_id == isp_id, Isp_service.service_id == service_id,
                        Isp_service.user_id == user_id) \
                .filter_by(user_id=current_user.user_id).count()

            if exists:
                flash('You have already added this data', 'danger')
                return render_template('add_your_subscribed_isp_services.html')
            else:
                user_isp_subscribed_services = Isp_service(isp_id, service_id, user_id)
                db.session.add(user_isp_subscribed_services)
                db.session.commit()
        flash('Data successfully Added', 'success')
        return redirect(url_for('view_my_isp_service_subscriptions'))
    else:
        return render_template('add_your_subscribed_isp_services.html')


@application.route('/view_my_isp_service_subscriptions', methods=['GET', 'POST'])
@login_required
def view_my_isp_service_subscriptions():
    # my_service_ratings = Service_metric_ratings.query.filter_by(user_id=g.user.user_id).order_by(
    # Service_metric_ratings.pub_date.desc()).all()
    view_my_isp_service_subscriptions = db.session.query(User.email, Isps.isp_name, Services.service_name) \
        .filter(Isp_service.user_id == User.user_id) \
        .filter(Isp_service.isp_id == Isps.isp_id) \
        .filter(Isp_service.service_id == Services.service_id) \
        .filter_by(user_id=current_user.user_id)

    # for i in view_my_isp_service_subscriptions:
    # print i.isp_name

    return render_template('view_my_isp_service_subscriptions.html',
                           view_my_isp_service_subscriptions=view_my_isp_service_subscriptions)


@application.route('/check')
def check():
    form = MultipleCheckBoxes()
    return render_template_string('<form>{{ form.example }}</form>', form=form)


@application.route('/react')
def react():
    return render_template('react.html')


@application.route('/survey')
@login_required
def survey():
    return render_template('take_survey.html')


@application.route('/home')
def home():
    return render_template('home.html')


@application.route('/isp_portal')
def isp_portal():
    return render_template('isp_portal.html')


@application.route('/build_service_report', methods=['GET', 'POST'])
@login_required
def build_service_report():
    return render_template('query_service_ratings.html')


@application.route('/rate_isp', methods=['GET', 'POST'])
@login_required
def rate_isp():
    if request.method == 'GET':
        return render_template('rate_isp.html')
    if request.method == 'POST':
        kpi_id = request.form['kpi_id']
        isp_id = request.form['isp_id']
        ratings_value = request.form['ratings_value']
        kpi_rating_comment = request.form['kpi_rating_comment']
        if not kpi_id:
            flash('KPI is required', 'danger')
            return render_template('rate_isp.html')
        elif not isp_id:
            flash('ISP is required', 'danger')
            return render_template('rate_isp.html')
        elif not ratings_value:
            flash('ratings is required', 'danger')
            return render_template('rate_isp.html')
        elif not kpi_rating_comment:
            flash('kpi_rating_comment is required', 'danger')
            return render_template('rate_isp.html')
        else:
            user_ratings = Kpi_ratings(kpi_id, isp_id, ratings_value, kpi_rating_comment)

            exists = db.session.query(Kpi_ratings.user_id, Kpi_ratings.kpi_id, Kpi_ratings.isp_id) \
                .filter(Kpi_ratings.kpi_id == kpi_id, Kpi_ratings.isp_id == isp_id) \
                .filter_by(user_id=current_user.user_id).count()

            if exists:
                flash('You have already provided ratings for this ISP , edit it instead', 'danger')
                return render_template('rate_isp.html')
            else:
                user_ratings.user = current_user
                db.session.add(user_ratings)
                db.session.commit()
                flash('Data successfully Added', 'success')
                return redirect(url_for('view_my_isp_ratings'))


@application.route('/view_my_isp_ratings', methods=['GET', 'POST'])
@login_required
def view_my_isp_ratings():
    # my_service_ratings = Service_metric_ratings.query.filter_by(user_id=g.user.user_id).order_by(
    # Service_metric_ratings.pub_date.desc()).all()
    view_my_isp_ratings = db.session.query(User.email, Isps.isp_name, Kpis.kpi_name, Ratings.ratings_value,
                                           Ratings.ratings_comment,
                                           Kpi_ratings.kpi_rating_comment, Kpi_ratings.pub_date) \
        .filter(Kpi_ratings.user_id == User.user_id) \
        .filter(Kpi_ratings.ratings_value == Ratings.ratings_value) \
        .filter(Kpi_ratings.kpi_id == Kpis.kpi_id) \
        .filter(Kpi_ratings.isp_id == Isps.isp_id) \
        .filter_by(user_id=current_user.user_id) \
        .order_by(Kpi_ratings.pub_date.desc()).all()

    # below is the charting
    isps = ([i.isp_name for i in view_my_isp_ratings])
    kpi = ([i.kpi_name for i in view_my_isp_ratings])
    ratings_value = ([int(round(i.ratings_value)) for i in view_my_isp_ratings])


    from pygal.style import DefaultStyle
    bar_chart = pygal.Bar(range=(0, 5), print_values=True, style=DefaultStyle(
        value_font_family='googlefont:Raleway',
        label_font_size=18,
        legend_font_size=20,
        tooltip_font_size=20,
        major_label_font_size=20,
        value_label_font_size=20,
        colors=('#ff851b', '#E8537A', '#E95355', '#E87653', '#E89B53'),
        value_font_size=30,
        value_colors=('white',)))

    bar_chart.title = "ISP Reputation Scores for KPI "
    bar_chart.x_labels = isps
    #bar_chart.x_labels = kpi
    bar_chart.add('R-Score', ratings_value)
    my_isp_ratings_graph_data = bar_chart.render(is_unicode=True)


    # for i in my_service_ratings:
    # print i.Isps.isp_name

    return render_template('view_my_isp_ratings.html', view_my_isp_ratings=view_my_isp_ratings,
                           my_isp_ratings_graph_data=my_isp_ratings_graph_data)


@application.route('/view_overall_isp_ratings', methods=['GET', 'POST'])
@login_required
def view_overall_isp_ratings():
    if request.method == 'GET':
        return render_template('query_isp_ratings.html')
    kpi_name = request.form['kpi_name']
    if not kpi_name:
        flash('KPI is required', 'danger')
        return render_template('query_isp_ratings.html')
    else:
        view_overall_isp_ratings = db.session.query(func.count(Ratings.ratings_value).label('count_of_users'),
                                                    func.sum(Ratings.ratings_value).label('sum_of_ratings'),
                                                    func.avg(Ratings.ratings_value).label('avg_of_ratings'),
                                                    Isps.isp_name, Kpis.kpi_name) \
            .filter(Kpi_ratings.isp_id == Isps.isp_id) \
            .filter(Kpi_ratings.ratings_value == Ratings.ratings_value) \
            .filter(Kpi_ratings.kpi_id == Kpis.kpi_id) \
            .filter(Kpi_ratings.user_id == User.user_id) \
            .filter(Kpis.kpi_name == kpi_name) \
            .group_by(Isps.isp_name)

        ratings_table_values = db.session.query(Ratings.ratings_value, Ratings.ratings_comment)
        # for i in view_overall_isp_ratings:
        # print(i.isp_name, i.service_name, i.metric_name, (round(i.avg_of_ratings)))
        # ratings_table_values = Ratings.query.filter_by(rating_value=(round(i.avg_of_ratings)))


        # below is the charting
        avg_ratings = ([int(round(i.avg_of_ratings)) for i in view_overall_isp_ratings])
        isps = ([i.isp_name for i in view_overall_isp_ratings])
        kpi = ([i.kpi_name for i in view_overall_isp_ratings])
        rating_verdict = [''] + ([i.ratings_comment for i in ratings_table_values])

        from pygal.style import DefaultStyle
        bar_chart = pygal.Bar(range=(0, 5), print_values=True, style=DefaultStyle(
            value_font_family='googlefont:Raleway',
            label_font_size=18,
            legend_font_size=20,
            tooltip_font_size=20,
            major_label_font_size=20,
            value_label_font_size=20,
            colors=('#ff851b', '#E8537A', '#E95355', '#E87653', '#E89B53'),
            value_font_size=30,
            value_colors=('white',)))
        bar_chart.title = "ISP Reputation Scores for KPI " + kpi[0]
        bar_chart.x_labels = isps
        bar_chart.y_labels = rating_verdict
        bar_chart.add('R-Score', avg_ratings)
        Overall_isp_ratings_graph_data = bar_chart.render(is_unicode=True)

        pie_chart = pygal.Pie()
        pie_chart.title = 'Browser usage in February 2012 (in %)'
        pie_chart.add('Chrome', 36.3)
        pie_chart.add('Safari', 4.5)
        pie_chart.add('Opera', 2.3)
        Overall_isp_ratings_pie_graph_data = pie_chart.render(is_unicode=True)


        graph = pygal.Line()
        graph.title = '% Change Coolness of programming languages over time.'
        graph.x_labels = ['2011', '2012', '2013', '2014', '2015', '2016']
        graph.add('Python', [15, 31, 89, 200, 356, 900])
        graph.add('Java', [15, 45, 76, 80, 91, 95])
        graph.add('C++', [5, 51, 54, 102, 150, 201])
        graph.add('All others combined!', [5, 15, 21, 55, 92, 105])
        graph_data = graph.render_data_uri()

        return render_template('view_overall_isp_ratings.html',
                               view_overall_isp_ratings=view_overall_isp_ratings,
                               ratings_table_values=ratings_table_values, graph_data=graph_data
                               , Overall_isp_ratings_graph_data=Overall_isp_ratings_graph_data
                               ,Overall_isp_ratings_pie_graph_data=Overall_isp_ratings_pie_graph_data)


@application.route('/rate_service', methods=['GET', 'POST'])
@login_required
def rate_service():
    if request.method == 'POST':
        metric_id = request.form['metric_id']
        isp_id = request.form['isp_id']
        service_id = request.form['service_id']
        ratings_value = request.form['ratings_value']
        custom_rating_comment = request.form['custom_rating_comment']
        if not metric_id:
            flash('Metric is required', 'danger')
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

            exists = db.session.query(Service_metric_ratings.user_id, Service_metric_ratings.metric_id,
                                      Service_metric_ratings.service_id,
                                      Service_metric_ratings.isp_id) \
                .filter(Service_metric_ratings.metric_id == metric_id,
                        Service_metric_ratings.isp_id == isp_id,
                        Service_metric_ratings.service_id == service_id) \
                .filter_by(user_id=current_user.user_id).count()

            if exists:
                flash('You have already rated this service using that KPI , edit it instead', 'danger')
            else:
                user_service_ratings.user = current_user
                db.session.add(user_service_ratings)
                db.session.commit()
                flash('Data successfully Added', 'success')
    return render_template('rate_service.html')


@application.route('/view_my_service_ratings', methods=['GET', 'POST'])
@login_required
def view_my_service_ratings():
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
        .filter_by(user_id=current_user.user_id) \
        .order_by(Service_metric_ratings.pub_date.desc()).all()

    # for i in my_service_ratings:
    # print i.Isps.isp_name

    return render_template('view_my_service_ratings.html', my_service_ratings=my_service_ratings)


@application.route('/view_overall_service_ratings', methods=['GET', 'POST'])
@login_required
def view_overall_service_ratings():
    if request.method == 'GET':
        return render_template('query_service_ratings.html')
    metric_name = request.form['metric_name']
    service_name = request.form['service_name']
    if not metric_name:
        flash('Metric is required', 'danger')
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

        return render_template('view_overall_service_ratings.html',
                               isp_ratings_per_service=isp_ratings_per_service,
                               ratings_table_values=ratings_table_values)


@application.route('/register', methods=['GET', 'POST'])
def register():
    form = SignupForm()
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('register.html', form=form)
        else:
            password = form.password.data
            email = form.email.data
            newuser = User(email, password)
            msg = Message('hie', sender='chamambom@gmail.com', recipients=['chamambom@gmail.com'])
            msg.body = """ From: %s  """ % (form.email.data)
            mail.send(msg)
            db.session.add(newuser)
            db.session.commit()
            current_user = newuser.email

            if current_user:
                return redirect(url_for('dashboard'))
    elif request.method == 'GET':
        return render_template('register.html', form=form)


@application.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            email = form.email.data
            password = form.password.data
            user = User.query.filter_by(email=email).first()
            if user is not None and user.check_password(password):
                user.authenticated = True
                login_user(user)
                # print('Thanks for logging in, {}'.format(current_user.email))
                next = request.args.get('next')
                return redirect(next or url_for("add_your_subscribed_isp_services"))
            else:
                flash('ERROR! Incorrect login credentials.', 'danger')
        except:
            db.session.rollback()
            db.session.remove()
            raise
    return render_template('login.html', form=form)


@application.context_processor
def user_count():
    try:
        user_count_registered = User.query.count()
        user_count_active = db.session.query(User.email).filter(User.authenticated == 1).count()
    except:
        db.session.rollback()
        db.session.remove()
        raise
    return dict(user_count_registered=user_count_registered, user_count_active=user_count_active)


# Below i will need to improvise on the SQL statements for perfomance
@application.context_processor
def dropdown():
    try:
        isp_query = db.session.query(Isps)
        isp_entries = [dict
                       (isp_id=isp.isp_id, isp_name=isp.isp_name, isp_description=isp.isp_description) for isp in
                       isp_query]

        services_query = db.session.query(Services)
        services_entries = [dict
                            (service_id=service.service_id, service_name=service.service_name,
                             service_catergory_id=service.service_catergory_id) for service in
                            services_query]

        ratings_query = db.session.query(Ratings)
        ratings_entries = [dict
                           (ratings_value=rating.ratings_value,
                            ratings_comment=rating.ratings_comment) for rating in
                           ratings_query]

        servicemetric_query = db.session.query(Service_metric)
        servicemetric_entries = [dict
                                 (metric_id=metric.metric_id, metric_name=metric.metric_name,
                                  metric_description=metric.metric_description) for metric in
                                 servicemetric_query]

        kpi_query = db.session.query(Kpis)
        kpi_entries = [dict
                       (kpi_id=kpi.kpi_id, kpi_name=kpi.kpi_name, kpi_description=kpi.kpi_description)
                       for kpi in
                       kpi_query]
    except:
        db.session.rollback()
        db.session.remove()
        raise
    return dict(isp_entries=isp_entries, services_entries=services_entries, ratings_entries=ratings_entries
                , servicemetric_entries=servicemetric_entries, kpi_entries=kpi_entries)


@application.route('/myprofile')
@login_required
def myprofile():
    try:
        logged_in_user = db.session.query(User.email).filter(User.email == current_user.email)
    except:
        db.session.rollback()
        db.session.remove()
        raise
    return render_template('myprofile.html', logged_in_user=logged_in_user)


@application.route('/logout')
@login_required
def logout():
    """Logout the current user."""
    user = current_user
    user.authenticated = False
    logout_user()
    flash('You have logged out ,thank you for your contribution', 'success')
    return redirect(url_for('login'))

# Look into the function below and see how you can use it

# @login_manager.unauthorized_handler
# def unauthorized_handler():
#     return 'Unauthorized'
