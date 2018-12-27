# coding=utf-8
from app import create_app

app = create_app('development')

if __name__ == '__main__':
    app.run(debug=True,host='192.168.1.97', port='5000')
    # app.run(debug=True)