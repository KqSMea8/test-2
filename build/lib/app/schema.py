# coding=utf-8
from app.models import AppModel, LanguageModel, UserModel, CompanyModel, PermissionModel, BluetoothPacketModel


# 格式化appModel
def schema_app(app:AppModel)->dict:
  ispass = app.download_progress

  updateFlag = app.download_flag

  updateLink = app.version_link

  versionInfo = {'updateFlag':updateFlag, 'updateLink':updateLink}

  info = list()
  if app.languages is not None:
    for language in app.languages:
        info.append(schema_language(language))
  pass

  return {
    'isPass': ispass,
    'versionInfo': versionInfo,
    'info': info
  }
pass


# 格式化languageModel
def schema_language(language:LanguageModel)->dict:
  languageStr = language.name or ''
  languageCode = language.code or ''
  languageVersion = language.version or ''
  return {
    'languageStr':languageStr,
    'languageCode':languageCode,
    'languageVersion':languageVersion
  }

pass


# 格式化UserModel
def schema_user(user:UserModel):
  if user.company is not None:
    companyDic = schema_Company(user.company)

  permissions = list()
  if user.permissions is not None:
    for pemission in user.permissions:
     permissions.append(schema_permission(pemission))

  return {
    'groupNo':companyDic['code'],
    'deadline':companyDic['surplusDays'],
    'token':user.token,
    'info':permissions,
    'preStrings':companyDic['pre'],
    'id':user.id,
    'account':user.account,
    'password':user.password,
    'companyName':companyDic['name']
  }
pass



def schema_permission(permission:PermissionModel):
  return {
    'powerName':permission.name,
    'powerNo':permission.code
  }
pass


def schema_Company(company:CompanyModel):
  return {
    'name': company.name,
    'code': company.code,
    'address': company.address,
    'phone': company.phone,
    'surplusDays': company.surplusDays,
    'id': company.id,
    'pre':company.pre
  }
pass


def schema_Packet(packet:BluetoothPacketModel):
  return {
    'packageName': packet.name,
    'version': packet.version,
    'uploadtime': packet.create_time,
    'source': packet.device_type,
    'downLoadLink': packet.link,
    'description': packet.description,
    'id': packet.id
  }
pass
