# coding=utf-8
import os, gzip, uuid, random

from flask import Blueprint, request, g, jsonify, url_for, make_response, abort

from app.utility import protectSql

from app.models import BluetoothPacketModel, CompanyModel, UserModel, PermissionModel, AdminUserModel, SMSCodeModel

from app.extensions import db

from app.schema import schema_Packet, schema_Company, schema_user, schema_permission, schema_admin_user_info

from sqlalchemy.exc import IntegrityError

from app.dysms_python.demo_sms_send import send_sms

import time


admin_api_v1_bp = Blueprint('admin_api_v1', __name__, url_prefix='/admin_api_v1')

# 上传的文件位置
UPLOAD_FOLDER = 'bluetooth'

# 上传的基地址
basedir = os.path.abspath('app/static')

# 允许上传的格式
ALLOWED_EXTENSIONS = set(['zip'])



# 上传新的蓝牙升级包
@admin_api_v1_bp.route('/uploadNewBluetoothPacket', methods=['POST'])
def uploadNewBluetoothPacket():
  '''通过管理后台上传新的蓝牙升级包'''
  requestDic = request.form.to_dict()

  bluetoothFiles = dict(request.files).get('bluetooth', list())

  packetVersion = requestDic.get('version', '')

  device_type = requestDic.get('deviceType', '0')

  description = requestDic.get('description', '')


  if len(bluetoothFiles) == 0:
    return jsonify(
      {
        'code':205,
        'message':'empty file'
      }
    ), 200


  # 处理文件
  file_dir = os.path.join(basedir, UPLOAD_FOLDER)

  if not os.path.exists(file_dir):
    os.makedirs(file_dir)

  bluetoothFile = bluetoothFiles[0]
  fileName = protectSql(bluetoothFile.filename)

  if allow_file(fileName):
    unixTime = int(time.time())
    newName = str(unixTime) + fileName
    fullFileName = os.path.join(file_dir, newName)

    bluetoothFile.save(fullFileName)

    bluetoothModel = BluetoothPacketModel(name=fileName, link=url_for('static', filename=(UPLOAD_FOLDER + '/'+ newName), _external=True), version = packetVersion, device_type=device_type, description=description)
    db.session.add(bluetoothModel)
    db.session.commit()

    return jsonify({
      'code':200,
      'message':'success'
    }), 200

  # 上传失败
  return jsonify({
    'code': 206,
    'message': 'failed'
  }), 200

pass



# 获取所有的升级包
@admin_api_v1_bp.route('/bluetoothPackets')
def getAllBluetoothPackets():
  packets = BluetoothPacketModel.query.order_by(BluetoothPacketModel.create_time.desc()).all()

  packetList = list()

  if packets is not None:
    for packet in packets:
      packetList.append(schema_Packet(packet))

    return jsonify(
      {
        'code':200,
        'message':'',
        'packetList':packetList
      }
    ), 200

  return jsonify({
    'code':208,
    'message':''
  })
pass



# 删除某个固件升级包
@admin_api_v1_bp.route('/deletePacket', methods=['POST'])
def deletePacket():
  id = request.json.get('packetId')
  if id is not None:
    packetModel:BluetoothPacketModel = BluetoothPacketModel.query.get_or_404(id)

    filePath:str = packetModel.link

    realPath = basedir + filePath.split('static')[1]

    db.session.delete(packetModel)
    db.session.commit()

    if os.path.exists(realPath):
      os.remove(realPath)

    return jsonify({
      'code':200,
      'message':'success'
    }), 200
  return jsonify({
      'code':210,
      'message':'failed'
    }), 200
pass


# 修改固件升级包信息
@admin_api_v1_bp.route('/modifyPacket', methods=['POST'])
def modifyPacket():
  id = request.json.get('packetId')
  if id is not None:
    packetModel:BluetoothPacketModel = BluetoothPacketModel.query.get_or_404(id)

    packetVersion = request.json.get('version', '')
    device_type = request.json.get('deviceType', '0')
    description = request.json.get('description', '')

    packetModel.version = packetVersion
    packetModel.description = description
    packetModel.device_type = device_type

    db.session.commit()

    return jsonify({
      'code':200,
      'message':'success',
      'packet':schema_Packet(packetModel)
    }), 200
  return jsonify({
    'code':211,
    'message':'faild'
  }), 200

pass



# 添加公司
@admin_api_v1_bp.route('/createCompany', methods=['POST'])
def createCompany():
  if request.json is not None:
    companyName = request.json.get('companyName', '')
    companyCode = request.json.get('companyCode', '')
    companyAddress = request.json.get('companyAddress', '')
    companyPhone = request.json.get('phone', '')
    companySurplusDays = request.json.get('surplusDay', 0)
    companyPre = str(request.json.get('Pre', '')).replace('+',">>>")
    companyDescription = request.json.get('description', '')

    companyModel:CompanyModel = CompanyModel(name=companyName, code=companyCode, address=companyAddress, phone=companyPhone, pre=companyPre, description=companyDescription)
    companyModel.surplusDays = companySurplusDays

    db.session.add(companyModel)
    db.session.commit()
    return jsonify({
      'code':200,
      'message':'success',
      'company':schema_Company(companyModel)
    }), 200

  return jsonify({
    'code': 212,
    'message': 'failed'
  }), 200

pass




@admin_api_v1_bp.route('/allCompanies')
def getAllCompany():
  allCompany = CompanyModel.query.order_by(CompanyModel.create_time.desc()).all()

  companyList = list()

  for companyModel in allCompany:
    companyList.append(schema_Company(companyModel))

  return jsonify({
    'code':200,
    'message':'success',
    'companyList':companyList
  })
pass


# 修改公司信息
@admin_api_v1_bp.route('/modifyCompany', methods=['POST'])
def modifyCompany():
  id = request.json.get('companyId')

  if id is not None:
    companyName = request.json.get('companyName', '')
    companyCode = request.json.get('companyCode', '')
    companyAddress = request.json.get('companyAddress', '')
    companyPhone = request.json.get('phone', '')
    companySurplusDays = request.json.get('surplusDay', 0)
    companyPre = str(request.json.get('Pre', '')).replace('+',">>>")
    companyDescription = request.json.get('description', '')

    companyModel:CompanyModel = CompanyModel.query.get_or_404(id)
    companyModel.name = companyName
    companyModel.code = companyCode
    companyModel.address = companyAddress
    companyModel.phone = companyPhone
    companyModel.surplusDays = int(companySurplusDays)
    companyModel.pre = companyPre
    companyModel.description = companyDescription

    db.session.commit()

    return jsonify({
      'code':'200',
      'message':'修改成功',
      'company':schema_Company(companyModel)
    })
  return jsonify({
    'code': '212',
    'message': '修改失败'
  })

pass


# 添加用户
@admin_api_v1_bp.route('/addUser', methods=['POST'])
def addUser():
  companyId = request.json.get('companyId')
  if companyId is not None:
    companyModel = CompanyModel.query.get_or_404(companyId)

    if len(companyModel.users) >= 3:
      return jsonify({
        'code': 215,
        'message': '每个公司最多3个用户'
      }), 200

    account = request.json.get('account', '')
    password = request.json.get('password', '')

    userModel= UserModel(account=account, password=password)
    userModel.permissions = PermissionModel.query.all()
    userModel.company = companyModel

    db.session.add(userModel)
    db.session.commit()

    return jsonify({
      'code':200,
      'message':'新增用户成功',
      'user': schema_user(userModel)
    }), 200

  return jsonify({
    'code': 214,
    'message': '新增用户失败'
  }), 200
pass


# 删除用户
@admin_api_v1_bp.route('/deleteUser', methods=['POST'])
def deleteUser():
  userId = request.json.get('userId')
  if userId is not None:
    userModel = UserModel.query.get_or_404(userId)

    db.session.delete(userModel)
    db.session.commit()

    return jsonify({
      'code':200,
      'message':'删除用户成功'
    }), 200

  return jsonify({
    'code': 212,
    'message': '用户不存在'
  }), 200

pass


# 修改用户信息
@admin_api_v1_bp.route('/modifyUser', methods=['POST'])
def modifyUser():
  userId = request.json.get('userId')
  if userId is not None:
    userModel:UserModel = UserModel.query.get_or_404(userId)

    password = request.json.get('password','')

    if len(password) == 0 :
      return jsonify({
        'code':218,
        'message':'密码为空'
      }), 200

    permissions = str(request.json.get('permissions','')).split(',')

    userModel.setPasswordMd5(password)
    userModel.token = ''

    # userModel.permissions.all().remove_all()

    for permissionModel in PermissionModel.query.all():
      if permissionModel in userModel.permissions:
        userModel.permissions.remove(permissionModel)

    if len(permissions) > 0:
      for permission in permissions:
        if len(permission) > 0:
          permissionModel = PermissionModel.query.get_or_404(permission)
          userModel.permissions.append(permissionModel)

    db.session.commit()
    return jsonify({
      'code':200,
      'message':'修改成功'
    }), 200
  return jsonify({
    'code':213,
    'message':'修改失败'
  }), 200

pass


# 查询用户信息
@admin_api_v1_bp.route('/allUsers', methods=['POST'])
def allUsers():
  companyId = request.json.get('companyId')
  # page = request.json.get('page')
  # per_page = 30

  if companyId is not None and len(companyId) > 0:
    allUsers = UserModel.query.filter_by(company_id=companyId).order_by(UserModel.create_time.desc()).all()
  else:
    allUsers = UserModel.query.order_by(UserModel.create_time.desc()).all()

  userList = list()

  for user in allUsers:
    userList.append(schema_user(user))

  return jsonify({
    'code':200,
    'message':'',
    'userList':userList
  }), 200
pass



# 查询平台所有权限
@admin_api_v1_bp.route('/permissions')
def getAllPermissions():
  permissionList = list()

  for permission in PermissionModel.query.all():
    permissionList.append(schema_permission(permission))

  return jsonify({
    'code':'200',
    'message':'',
    'permissionList':permissionList
  })
pass



# 发送验证码
@admin_api_v1_bp.route('/adminSmS', methods=['POST'])
def admin_user_get_smsCode():
  adminPhone = request.json.get('phone','')
  adminModel = AdminUserModel.query.filter_by(phone=adminPhone).first()

  if adminModel is not None:
    __business_id = uuid.uuid1()
    code = random.randint(100000, 999999)
    params = {'code':code,"product":"KingMeter"}


    result = eval(str(send_sms(__business_id, adminPhone, "KingMeter", "SMS_144896528",str(params)).decode()))

    if result is not None and result.get('Code','') == 'OK':
      smsCodeModel = SMSCodeModel(phone=adminPhone, code=code)
      db.session.add(smsCodeModel)
      db.session.commit()

      return jsonify({
        'code':200,
        'message':'验证码已发送'
      }), 200

    else:
      result.update({
        'code': 232,
        'message': '验证码失败'
      })
      return jsonify(result), 200

  else:
    return jsonify({
      'code':233,
      'message':'账号不存在'
    }), 200

  pass


# 登录
@admin_api_v1_bp.route('/adminLogin', methods=['POST'])
def adminLogin():
  phone = request.json.get('phone', '')
  code = request.json.get('code', '')

  adminModel:AdminUserModel = AdminUserModel.query.filter_by(phone=phone).first()
  if adminModel is None:
    return jsonify({
      'code': 233,
      'message': '账号不存在'
    }), 200

  smsCodeModel = SMSCodeModel.query.filter(
    SMSCodeModel.code == code,
    SMSCodeModel.phone == phone
  ).order_by(SMSCodeModel.create_time.desc()).first()

  if smsCodeModel is None or smsCodeModel.is_valid == False:
    return jsonify({
      'code':234,
      'message':'验证码错误'
    }), 200

  db.session.delete(smsCodeModel)
  adminModel.generate_token(smsCodeModel.code)
  db.session.commit()

  adminUserDic:dict = schema_admin_user_info(adminModel)
  adminUserDic.update({'code':200,'message':'登录成功'})
  return jsonify(adminUserDic), 200
pass



@admin_api_v1_bp.before_request
def before_request():
  if request.method == 'OPTIONS':
    response = make_response(jsonify({'code': '250', 'message': 'token 失效, 请重新登录'}), 401)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

  # todo: 验证用户的合法性
  token = request.headers.get('X-AUTH-TOKEN', '')

  adminUserMode:AdminUserModel = AdminUserModel.query.filter_by(token=token).first()
  if adminUserMode is None and request.path.endswith('adminSmS') == False and request.path.endswith('adminLogin') == False:
    abort(401)
    # response = make_response(jsonify({'code': '250', 'message': 'token 失效, 请重新登录'}), 401)
    # response.headers['Access-Control-Allow-Origin'] = '*'
    # response.headers['Access-Control-Allow-Headers'] = '*'
    # return response
pass


@admin_api_v1_bp.after_request
def after_request(response):
  res = dict()
  if response.json is not None:
    data = dict(response.json)
    res['code'] = data.get('code', '-1')
    res['message'] = data.get('message', '')
    if 'code' in data:
      del data['code']

    if 'message' in data:
      del data['message']

    res['data'] = data


    newResponse = make_response(jsonify(res))
    newResponse.headers['Access-Control-Allow-Origin'] = '*'
    newResponse.headers['Access-Control-Allow-Headers'] = '*'
    # newResponse.headers['Content-Encoding'] = 'gzip'
    # newResponse.setContentLength(gzip)
    return newResponse
  else:
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'

    return response
pass


@admin_api_v1_bp.errorhandler(404)
def resource_not_found(e):
  return jsonify({
    'code':209,
    'message':'资源不存在'
  }), 200
pass

@admin_api_v1_bp.errorhandler(500)
def server_problem(e):
  return jsonify({
    'code':219,
    'message':'访问失败'
  }), 200
pass


@admin_api_v1_bp.errorhandler(IntegrityError)
def catch_IntegrityError(e):
  return jsonify({
    'code':219,
    'message':'请求失败，请检查数据'
  }), 200
pass


# 判断是否符合上传规则
def allow_file(filename:str):
  return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

