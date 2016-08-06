from models import User, Isps, Service_metric_ratings, Service_catergory, Service_metric, Services, Ratings
from database import db


def dropdown():
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

    return isp_entries, services_entries, ratings_entries, servicemetric_entries