# coding=utf-8
# import logging
#
# import leancloud

from flask import Flask

from .config import config

from app.extensions import db

from app.blueprints.mobile_api.v1.mobile_api_v1 import mobile_api_v1_bp
from app.blueprints.admin_api.v1.admin_api_v1 import admin_api_v1_bp


def create_app(configName:str=None)->Flask:
  app = Flask(__name__)
  app.config.from_object(config[configName] if configName is not None else config['development'])

  register_extensions(app)

  register_blueprints(app)


  # leancloud.init('p34m7UOfyDunRNWddtX0JRjC-gzGzoHsz', app_key='taQdkywd2XByzYeb98tSDWFH')
  # leancloud.use_region('CN')
  # logging.basicConfig(level=logging.DEBUG)


  from .commands import register_commands
  register_commands(app)

  from werkzeug.contrib.fixers import ProxyFix
  app.wsgi_app = ProxyFix(app.wsgi_app)

  return app
pass



# 注册蓝本
def register_blueprints(app:Flask):
  app.register_blueprint(mobile_api_v1_bp)
  app.register_blueprint(admin_api_v1_bp)
pass



# 注册扩展
def register_extensions(app):
  db.init_app(app)

  from flask_script import Manager

  manager = Manager(app)

  from flask_migrate import Migrate, MigrateCommand
  migrate = Migrate(app, db)
  manager.add_command('db', MigrateCommand)
pass
