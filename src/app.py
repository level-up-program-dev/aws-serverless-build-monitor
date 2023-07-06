from flask import Flask, redirect, render_template, request, jsonify


app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"test": "hello world"})

