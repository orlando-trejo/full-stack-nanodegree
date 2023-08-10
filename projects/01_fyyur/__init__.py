from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
import dateutil.parser
import babel.dates
import logging
from logging import Formatter, FileHandler

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template('errors/500.html'), 500

def configure_logging(app):
    if not app.debug:
        file_handler = FileHandler('error.log')
        file_handler.setFormatter(
            Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        )
        app.logger.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.info('errors')


db = SQLAlchemy()
migrate = Migrate()
moment = Moment()

def create_app():
    app = Flask(__name__)
    app.jinja_env.filters['datetime'] = format_datetime
    register_error_handlers(app)
    configure_logging(app)
    moment.init_app(app)
    app.config.from_object('starter_code.config')
    db.init_app(app)
    migrate.init_app(app, db)

    return app