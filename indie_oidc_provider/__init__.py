import os
from flask import Flask
from .models import db
from .oauth2 import config_oauth
from .routes import bp

import click

__version__ = "0.1.0"


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # load default configuration
    app.config.from_object("indie_oidc_provider.settings")

    # # load environment configuration
    # if "WEBSITE_CONF" in os.environ:
    #     app.config.from_envvar("WEBSITE_CONF")

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    config_oauth(app)

    app.register_blueprint(bp, url_prefix="")

    db.init_app(app)
    app.cli.add_command(initdb)

    return app


@click.command("init-db")
def initdb():
    db.create_all()


def main():
    app = create_app()
    app.run(host="127.0.0.1", port=5000)


if __name__ == "__main__":
    main()
