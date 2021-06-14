from gensim.summarization.summarizer import summarize
from newspaper import Article
from flask import Flask, render_template, request, jsonify
from googletrans import Translator
import json
import pdftotext
import urllib
from urllib.error import URLError, HTTPError
import io
from pathlib import Path
import tempfile

class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='[[',
        variable_end_string=']]',
    ))

app = CustomFlask(__name__)
translator = Translator()

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/news", methods=['POST'])
def news():
    # retrieve articel from URL
    url = request.args['url']
    text = ""

    # for PDF extension
    if Path(url).suffix == '.pdf':
        try :
            # pretend not to crawl
            req = urllib.request.Request(url, headers={'User-Agent' : "Magic Browser"}) 
            con = urllib.request.urlopen(req)
            remoteFile = con.read()  
            momoryFile = io.BytesIO(remoteFile)
            pdf = pdftotext.PDF(momoryFile)
            
            for page in pdf :
                text += page  
        except HTTPError as e :
            err = e.read()
            code = e.getCode()
    # for normal URL
    else :
        news = Article(url)
        news.download()
        news.parse()

        text = news.text

    # remove multiple whitespaces in the article
    text = ' '.join(text.split())
    response = app.response_class(
        response=json.dumps(text),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/abridge", methods=['POST'])
def abridge():
    origin = request.args['origin']
    summarizeRate = request.args['summarizerate']
    length = len(origin.split()) * (int(summarizeRate)/100)
    summarized = summarize(origin, word_count=length)
    response = app.response_class(
        response=json.dumps(summarized.replace("\n", "\n\n")),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/translate", methods=['POST'])
def translate():
    text = ""
    try :
        summarized = request.args['summarized']
        translated = translator.translate(summarized, dest='ko')
        text = translated.text
    except Exception as e: 
        text = "3900 characters limit exceeded !!!"
    response = app.response_class(
        response=json.dumps(text),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/upload", methods=['POST'])
def upload():
    file = request.files['file']    
    text = ""
    tempDir = tempfile.TemporaryDirectory()
    filepath = tempDir.name + '/temp.pdf'
    file.save(filepath)
    con = urllib.request.urlopen('file://'+filepath)
    remoteFile = con.read()  
    momoryFile = io.BytesIO(remoteFile)
    pdf = pdftotext.PDF(momoryFile)
            
    for page in pdf :
        text += page  

    tempDir.cleanup()
    
    text = ' '.join(text.split())
    response = app.response_class(
        response=json.dumps(text),
        status=200,
        mimetype='application/json'
    )
    return response

if __name__ == '__main__':
    app.run(host="127.0.0.1", port="8080")