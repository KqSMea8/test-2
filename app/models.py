# coding=utf-8
from datetime import datetime, timedelta

from .extensions import db

from werkzeug.security import generate_password_hash, check_password_hash

import hashlib

# app版本和语言关联表
app_language_table = db.Table(
  'app_language_table',
  db.Column('app_id', db.Integer, db.ForeignKey('app.id'), primary_key=True),
  db.Column('language_id', db.Integer, db.ForeignKey('language.id'), primary_key=True)
)

# App版本类
class AppModel(db.Model):
  __tablename__ = 'app'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)

  # 来源 0表示iOS，其他表示安卓的各个平台
  version_platform = db.Column(db.SmallInteger, index=True, nullable=False, default=0)

  # 下载地址
  version_link = db.Column(db.String(500))

  # 版本号
  version_code = db.Column(db.String(30))

  # 版本描述
  description = db.Column(db.Text)

  # 下载标志，0代表不提示下载，1代表提示下载，2代表强制下载
  download_flag = db.Column(db.SmallInteger, nullable=False, default=0)

  # 是否通过下载
  download_progress = db.Column(db.SmallInteger, nullable=False, default=0)

  # 创建时间
  create_time = db.Column(db.DateTime, default=datetime.utcnow)

  languages = db.relationship('LanguageModel', back_populates='apps', secondary=app_language_table)

  def __repr__(self):
    return "<APP:> {\nversionPlatform = %d, languages = %s\n}" % (self.version_platform, self.languages)
  pass
pass



# 语言类
class LanguageModel(db.Model):
  __tablename__ = 'language'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)

  # 语言名称
  name = db.Column(db.String(20), nullable=False, default='English')

  # 语言代码0代表英语，1代表中文，2代表德语
  code = db.Column(db.SmallInteger, nullable=False, default=0)

  # 语言版本
  version = db.Column(db.Float, nullable=False)

  # 语言文件名
  filename = db.Column(db.String(255), nullable='')

  # 上传时间
  create_time = db.Column(db.DateTime, default=datetime.utcnow)

  description = db.Column(db.Text, default='')

  apps = db.relationship('AppModel', secondary=app_language_table, back_populates='languages')

  def __init__(self, **kwargs):
    super(LanguageModel, self).__init__(**kwargs)
    self.__setDefaultVersion()
  pass

  def __repr__(self):
    return "<Language>{\ncode = %d, \nfilename= %s, \nversion = %f, \napps = %s\n}" % (self.code, self.filename, self.version, self.apps)

  def __setDefaultVersion(self):
    """根据数据库内当前语言的版本来决定新的版本, 若用户自己设置则不做任何涉及"""
    if self.version is None:
      language:LanguageModel = LanguageModel.query.filter_by(code=self.code).order_by(LanguageModel.version.desc()).first()
      if language is not None:
        self.version = language.version + 1.0;
      else:
        self.version = 0
  pass
pass


# 权限用户表
user_permission_table = db.Table(
  'user_permission_table',
  db.Column('user_id', db.Integer, db.ForeignKey('mmuser.id'), primary_key=True),
  db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'), primary_key=True)
)

# 用户表
class UserModel(db.Model):
  __tablename__ = 'mmuser'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)

  # 账户名
  account = db.Column(db.String(50), unique=True, nullable=False)

  # 密码
  password = db.Column(db.String(255))

  # token
  token = db.Column(db.String(255), nullable=True, unique=True)

  # 创建时间
  create_time = db.Column(db.DateTime, default=datetime.utcnow)

  # 公司
  company_id = db.Column(db.Integer, db.ForeignKey('mmcompany.id'), nullable=False)
  company = db.relationship('CompanyModel', back_populates='users', uselist=False)

  # 权限
  permissions = db.relationship('PermissionModel', secondary=user_permission_table, back_populates='users')

  # 用户日志
  logs = db.relationship('LogModel', back_populates='user', lazy='dynamic', cascade='all')

  def __init__(self, **kwargs):
    super(UserModel, self).__init__(**kwargs)

    # 设置MD5密码
    hash5 = hashlib.md5()
    hash5.update(bytes(self.password, encoding='utf-8'))
    self.password = hash5.hexdigest()
  pass


  def generate_token(self):
    baseStr = self.account + datetime.now().strftime('%Y%m%d %H%M%S') + self.password + str(self.id)
    hash5 = hashlib.md5()
    hash5.update(bytes(baseStr, encoding='utf-8'))
    self.token = hash5.hexdigest()
    db.session.commit()
  pass

  # 设置MD5密码
  def setPasswordMd5(self, password):
    hash5 = hashlib.md5()
    hash5.update(bytes(password, encoding='utf-8'))
    self.password = hash5.hexdigest()
  pass

  def __repr__(self):
    return "<User>{\naccount = %s, \ncompanyId = %s\n, permissions = %s}" % (self.account, self.company_id, self.permissions)

pass


class CompanyModel(db.Model):
  __tablename__ = 'mmcompany'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)

  # 名称
  name = db.Column(db.String(100), unique=True, nullable=False)

  # 公司代码
  code = db.Column(db.String(10), nullable=False)

  # 地址
  address = db.Column(db.String(500))

  # 联系电话
  phone = db.Column(db.String(30))

  # 设备前缀
  pre = db.Column(db.String(255))

  # 到期日期
  deadline = db.Column(db.DateTime)

  # 创建日期
  create_time= db.Column(db.DateTime, default=datetime.utcnow)

  # 公司下的所有用户
  users = db.relationship('UserModel', back_populates='company', cascade='all')

  # 描述
  description = db.Column(db.Text)


  # 剩余使用天数
  @property
  def surplusDays(self):
    if self.deadline is None:
      return 0;
    else:
      days = (self.deadline - datetime.utcnow()).days
      if days > 0 :
       return int(days) + 1
      else:
        if (self.deadline - datetime.utcnow()).seconds > 0:
          return 1
        return 0
  pass

  # 设置剩余使用天数
  @surplusDays.setter
  def surplusDays(self, value):
    if value is not None and (int(value) >= 0 or len(value) != 0):
      self.deadline = datetime.utcnow() + timedelta(days=int(value))
  pass


  def __repr__(self):
    return "<Company>{\nname = %s, \ncode = %s, \nusers = %s\n}" % (self.name, self.code, self.users)
  pass

pass



# 权限类
class PermissionModel(db.Model):
  __tablename__ = 'permission'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)

  name = db.Column(db.String(30), unique=True)

  code = db.Column(db.SmallInteger)

  users = db.relationship('UserModel', secondary=user_permission_table, back_populates='permissions')

  def __repr__(self):
    return "<Permission>{\nname = %s, \ncode = %d}" % (self.name, self.code)
  pass
pass



class LogModel(db.Model):
  __tablename__ = 'mmlog'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)

  phone_type = db.Column(db.String(30))

  soft_version = db.Column(db.String(30))

  permission_name = db.Column(db.String(30))

  remark = db.Column(db.String(300))

  user_id = db.Column(db.Integer, db.ForeignKey('mmuser.id'))
  user = db.relationship('UserModel', back_populates='logs')

  def __repr__(self):
    return "<Log>{\nuser_id = %s, permissionName = %s\n}" % (self.user_id, self.permission_name)
  pass

pass


class BluetoothPacketModel(db.Model):
  __tablename__ = 'bluetooth_packet'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)

  # 文件名
  name = db.Column(db.String(255), nullable=False, default='')

  # 版本号
  version = db.Column(db.String(20))

  # 设备类型，0代表蓝牙锁，1代表智能锁，2代表西班牙的电池
  device_type = db.Column(db.SmallInteger)

  # 下载链接
  link = db.Column(db.String(400))

  # 描述
  description = db.Column(db.Text, default='')

  # 上传时间
  create_time = db.Column(db.DateTime, default=datetime.utcnow)

  def __repr__(self):
    return "<Packet>:{\nname = %s, \nlink = %s\n}" % (self.name, self.link)
  pass

pass



class AdminUserModel(db.Model):
  __tablename__ = 'admin_user'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)

  phone = db.Column(db.String(30), unique=True)

  token = db.Column(db.String(256), nullable=True)

  def __repr__(self):
    return "<Admin User>:{\nphone = %s\n}" % self.phone
  pass

  def generate_token(self, code):
    baseStr = self.phone + datetime.now().strftime('%Y%m%d %H%M%S') + str(code) + str(self.id)
    hash5 = hashlib.md5()
    hash5.update(bytes(baseStr, encoding='utf-8'))
    self.token = hash5.hexdigest()
    db.session.commit()
  pass

pass


class SMSCodeModel(db.Model):
  __tablename__ = 'snscode'

  id = db.Column(db.Integer, primary_key=True)

  phone = db.Column(db.String(30), index=True)

  code = db.Column(db.String(20))

  create_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

  @property
  def is_valid(self):
    return (datetime.utcnow() - self.create_time).seconds < 300
  pass
pass
