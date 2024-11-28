from flask import Flask, render_template, request
import chatbot

app = Flask(__name__)

@app.route("/chatbot")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return str(get_response(userText))

def get_response(userText):
    return chatbot.reply(userText)

app.run(debug = True)
