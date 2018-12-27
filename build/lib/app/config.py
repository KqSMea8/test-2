# coding=utf-8
import os, sys

baseDir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


# 判断平台
WIN = sys.platform.startswith('win')

secret_key = "I don't want to tell you"

if WIN:
  prefix = 'sqlite:///'
else:
  prefix = 'sqlite:////'

class BaseConfig(object):
  SECRET_KEY = os.getenv('SECRET_KEY', secret_key)

  DEBUG_TB_INTERCEPT_REDIRECTS = False

  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SQLALCHEMY_RECORD_QUERIES = True
pass


class DevelopmentConfig(BaseConfig):
  SQLALCHEMY_DATABASE_URI = prefix + os.path.join(baseDir, 'data-dev.db')
pass


class ProductionConfig(BaseConfig):
  SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + os.path.join(baseDir, 'data.db'))
pass


# 配置字典
config= {
  'development': DevelopmentConfig,
  'production': ProductionConfig
}

