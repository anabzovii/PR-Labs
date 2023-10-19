from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models.database import db
from flask_swagger_ui import get_swaggerui_blueprint
from models.electro_scooter import ElectroScooter


def create_app():
    app = Flask(__name__)
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1111@localhost:5432/electro_scooter'
    db.init_app(app)
    return app


if __name__ == '__main__':
    app = create_app()
    SWAGGER_URL = "/swagger"
    API_URL = "/static/swagger.json"

    swagger_ui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': 'Access API'
        }
    )
    app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
    import routes
    app.run()
