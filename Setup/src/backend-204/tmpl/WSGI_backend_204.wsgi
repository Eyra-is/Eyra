from flask import Flask
application=Flask(__name__)

@application.route('/')
def generate_204():
	return '', 204

if __name__ == '__main__':
	application.run()
