from flask_api import home_app

if __name__ == '__main__':
    home_app.app.run(host='0.0.0.0', debug=True)
