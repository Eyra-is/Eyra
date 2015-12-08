from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World yo!'

@app.route('/interact/', methods=["GET","POST"])
def get_or_post():

	help_topics={'usage':'Send a POST or GET request. More help to follow.\n'}
	
	method=None
	json_data=None
	file_data=None
	help_data=None
	response=''
	try:
		if request.method == 'POST':
			
			method='POST'
			
			if 'json' in request.form:
				json_data=request.form['json']
				response+='json: ' + json_data + '\n'

			if 'file' in request.files:
				file_data=request.files['file']
				response+='file: ' + file_data.filename + '\n'
			
		elif request.method == 'GET':
			
			method='GET'

			if 'json' in request.form:
				json_data=request.form['json']
				response+='json: ' + json_data + '\n'
			
			if 'help' in request.form:
				help_data=request.form['help']
				if help_data in help_topics:
					return help_topics[help_data]
			
		else:
			
			method='UNKNOWN: ' + request.method
			
	except Exception as e:
			
			method='ERROR:' + e.text()
			
	return "Request: " + method + "\n" + \
				"Content:\n" + response

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0') 
