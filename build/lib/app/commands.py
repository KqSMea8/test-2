# coding=utf-8
import click

from flask import Flask

from app.extensions import db


from app.models import AppModel, LanguageModel, UserModel, CompanyModel, PermissionModel, AdminUserModel

def register_commands(app:Flask):
  @app.cli.command()
  @click.option('--drop', is_flag=True, help='Creat after drop.')
  def initdb(drop):
    """生成数据库"""
    if drop:
      click.confirm('确认删除？', abort=True)
      db.drop_all()

    db.create_all()
    make_appinfo()
    make_permissioninfo()
    make_userinfo()
    make_adminUser()
    click.echo('数据库已生成')
  pass


  # 生成app初始化信息
  def make_appinfo():
    appModel: AppModel = AppModel()
    appModel.version_platform = 0
    appModel.version_link = "https:///www.baidu.com"
    appModel.version_code = 1.0
    appModel.download_flag = 0
    appModel.download_progress = 1
    appModel.description = '测试下载'

    language1: LanguageModel = LanguageModel()
    language1.name = 'English'
    language1.code = 0
    language1.version = 0.1
    language1.filename = 'en.json'

    language2: LanguageModel = LanguageModel()
    language2.name = '中文'
    language2.code = 1
    language2.version = 0.1
    language2.filename = 'zh.json'

    appModel.languages = [language1, language2]

    db.session.add_all([appModel, language1, language2])
    db.session.commit()
  pass



  # 生成账号信息
  def make_userinfo():
    company:CompanyModel = CompanyModel()
    company.name = '金米特1'
    company.code = 2113
    company.address = '天津市北辰区辰昌路15号'
    company.phone = '13155463802'
    company.surplusDays = 365


    users = [
      {
        'account':'cr001',
        'password':'111'
      },
      {
        'account':'cr002',
        'password':'111'
      }
    ]


    for userDic in users:
      userModel = UserModel(account=userDic['account'], password=userDic['password'])
      userModel.permissions = PermissionModel.query.all()
      userModel.company = company

    db.session.add(company)
    db.session.commit()
  pass

  # 生成权限
  def make_permissioninfo():
    permissions = [
      {
        'name':'Lock re-name',
        'code':'1'
      },
      {
        'name':'User ID',
        'code':'2'
      },
      {
        'name':'IP & port',
        'code':'3'
      },
      {
        'name':'S/W Update',
        'code':'4'
      },
      {
        'name':'Unlock test',
        'code':'5'
      },
      {
        'name':'History Log',
        'code':'6'
      },
      {
        'name':'ICCID',
        'code':'7'
      },
      {
        'name':'Sleep mode',
        'code':'8'
      },
      {
        'name':'APN',
        'code':'9'
      },
      {
        'name':'Reset Lock',
        'code':'10'
      },
      {
        'name':'New RFID',
        'code':'11'
      },
      {
        'name':'Battery',
        'code':'12'
      },
    ]

    for permission in permissions:
      permissionModel:PermissionModel = PermissionModel(name=permission['name'], code=permission['code'])

      db.session.add(permissionModel)

    db.session.commit()
  pass



  def make_adminUser():
    adminUser:AdminUserModel = AdminUserModel()
    adminUser.phone = '15022005448'
    db.session.add(adminUser)
    db.session.commit()
  pass

pass

