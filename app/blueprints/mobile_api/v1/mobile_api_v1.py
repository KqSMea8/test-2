# coding=utf-8
from flask import Blueprint, request, g, url_for, jsonify, make_response
from app.models import AppModel, LanguageModel, UserModel, LogModel, BluetoothPacketModel
from app.schema import schema_app, schema_user, schema_Packet
from app.extensions import db

mobile_api_v1_bp = Blueprint('mobile_api_v1', __name__, url_prefix='/mobile_api_v1')


# app初始化接口
@mobile_api_v1_bp.route('appinit', methods=['POST'])
def appinit():
  source = request.json.get('source', '0')
  appModel:AppModel = AppModel.query.filter_by(version_platform=source).order_by(AppModel.create_time.desc()).first()
  if appModel is not None:
    appDic = schema_app(appModel)
    appDic.update({
      'code':200,
      'message':''
    })
    return jsonify(appDic), 200
  return jsonify({'code':201, 'message':'', 'data':{}}), 200
pass


# 登录
@mobile_api_v1_bp.route('/login', methods=['POST'])
def login():
  account = g.data.get('accountName', '')
  password = g.data.get('password', '')

  userModel = UserModel.query.filter(
    UserModel.account == account,
    UserModel.password == password
  ).first()

  if userModel is not None:
    userModel.generate_token()

    userDic = schema_user(userModel)
    userDic.update({
        'code': 200,
        'message':'login successfully',
      })

    return jsonify(userDic), 200
  return jsonify({
    'code':202,
    'message':'login error'
  }), 200
pass


@mobile_api_v1_bp.route('/getBluetoothList', methods=['POST'])
def getBluetoothList():
  token = request.json.get('token', '')

  user:UserModel = UserModel.query.filter_by(token=token).first()

  if user is None:
    return jsonify({
      'code': -1,
      'message': 'token invalid'
    }), 200

  device_type = g.data.get('device_type')

  if device_type is not None:
    packetModels = BluetoothPacketModel.query.filter_by(device_type=device_type).order_by(BluetoothPacketModel.create_time.desc()).all()
  else:
    packetModels = BluetoothPacketModel.query.order_by(BluetoothPacketModel.create_time.desc()).all()

  packages = list()

  for packet in packetModels:
    packages.append(schema_Packet(packet))

  return jsonify({
    'code':200,
    'message':'',
    'packages': packages
  })
pass


# 上传日志
@mobile_api_v1_bp.route('/uploadlog', methods=['POST'])
def upload_log():
  token = request.json.get('token', '')

  user:UserModel = UserModel.query.filter_by(token=token).first()

  if user is not None:
    logs:str = g.data.get('logs', '')
    logArr = logs.split('>>>')

    if len(logArr) >= 3:
      logModel:LogModel = LogModel(phone_type=logArr[0], soft_version=logArr[1], permission_name=logArr[2])

      if len(logArr) > 3:
        logModel.remark = logArr[3]

      logModel.user = user
      db.session.add(logModel)

      db.session.commit()
      return jsonify({
        'code':200,
        'message':'upload success'
      }), 200
    else:
      # 上传了错误的格式
      return jsonify({
        'code':203,
        'message':'upload failed'
      }), 200
  # token失效
  return jsonify({
      'code':-1,
      'message':'token invalid'
    }), 200
pass



@mobile_api_v1_bp.before_request
def mobile_api_before_request():
  if request.json is not None:
    data = request.json.get('data', dict())
    g.data = data
  else:
    response = make_response(jsonify({'code':'201', 'message':'传参错误'}))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,XFILENAME,XFILECATEGORY,XFILESIZE'
    return response
pass


@mobile_api_v1_bp.after_request
def mobile_api_after_request(response):
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
    newResponse.headers['Access-Control-Allow-Headers'] = 'Content-Type,XFILENAME,XFILECATEGORY,XFILESIZE'
    return newResponse;
  else:
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,XFILENAME,XFILECATEGORY,XFILESIZE'
    return response
pass