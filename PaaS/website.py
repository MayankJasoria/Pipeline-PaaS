from flask import Flask, render_template, request
from main import BuildPipeline
from config import Config
from threading import Thread

app=Flask(__name__)

pipeline = None

@app.route('/')
def index():
    print("Index!!")
    return render_template("index.html")

@app.route('/service/', methods=["GET","POST"])
def registerService():
    print("Add Service Called")
    if request.form['action'] == "Add Service":
        # call add service
        print(request.form)
        if request.form['parent'] == "":
            print('Parent is None')
            pipeline.addService(request.form['name'], Config.services[request.form['services']])
        else:
            pipeline.addService(request.form['name'], Config.services[request.form['services']], request.form['parent'])
    else:# request.form.post['action'] == "Remove Service":
        # call delelteService
        pipeline.removeService(request.form['name'])
        # do nothing
    return render_template('index.html')

@app.route('/build/', methods=["GET","POST"])
def build():
    thread = Thread(target=pipeline.buildPipeline, args=(), daemon=True)
    thread.start()
    # pipeline.buildPipeline()
    return render_template("built.html")

@app.route('/pipeline/', methods=["GET","POST"])
def terminate():
    thread = Thread(target=pipeline.terminatePipeline, args=(), daemon=True)
    thread.start()
    # pipeline.terminatePipeline()
    return render_template("index.html")

if __name__ == "__main__":
    pipeline = BuildPipeline()
    app.run(debug=True)