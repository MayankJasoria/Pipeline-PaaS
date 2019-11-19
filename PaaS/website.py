from flask import Flask, render_template, request
from main import BuildPipeline

app=Flask(__name__)

pipeline = None

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/', methods=["POST"])
def registerService():
    if request.form.post['action'] == "Add Service":
        # call add service
        if request.form['parent'] == "":
            pipeline.addService(request.form['name'], 'rmq_com.py')
        else:
            pipeline.addService(request.form['name'], 'rmq_com.py', request.form['parent'])
    else:# request.form.post['action'] == "Remove Service":
        # call delelteService
        pipeline.removeService(request.form['name'])
        # do nothing
    return render_template('index.html')

@app.route('/build/', methods=["POST"])
def build():
    pipeline.buildPipeline()
    return render_template("built.html")

@app.route('/pipeline/', methods=["POST"])
def terminate():
    pipeline.terminatePipeline()
    return render_template("index.html")

if __name__ == "__main__":
    pipeline = BuildPipeline()
    app.run(debug=True)