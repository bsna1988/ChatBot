from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/chatbot")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return str(get_response(userText))

def get_response(userText):
    return "Default response"

app.run(debug = True)
