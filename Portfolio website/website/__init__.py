from flask import Flask


# create the app and blueprints that runs the website
def create_app():
    app = Flask(__name__)

    from .views import views

    # URL_prefix for both python sheet, views.py and auth.py
    app.register_blueprint(views, url_prefix='/')
    return app
