# -*- coding: utf-8 -*-
import sys
import urllib2
# import BeautifulSoup
import random
import pandas as pd
from bs4 import BeautifulSoup
from urllib2 import urlopen
import pymysql
import sqlmodels
import os
import sys
import xlrd
import json
import csv
import re
import simplejson
from sqlalchemy import Column, ForeignKey, Integer, String,JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodels import Model, Base, CSVData
from sqlalchemy import distinct
from sqlalchemy import func

from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, SelectField

from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, Blueprint, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, configure_uploads, DATA
from flask_paginate import Pagination, get_page_parameter
import math
import requests

reload(sys)
sys.setdefaultencoding("utf8")

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
app.config['TEMPLATES_AUTO_RELOAD']= True
app.config["UPLOADS_DEFAULT_DEST"] = 'static'
app.config["DEBUG"] = True

upload_files = UploadSet("uploads", DATA)
configure_uploads(app, upload_files)

mod = Blueprint('models', __name__)

Base = declarative_base()
engine = create_engine(
     "mysql+pymysql://irie:irie1234@iriedb.cwj1ihf4ectz.us-east-1.rds.amazonaws.com/irie?host=iriedb.cwj1ihf4ectz.us-east-1.rds.amazonaws.com?port=3306")

# engine = create_engine(
#    "mysql+pymysql://root:root@localhost/irie?host=localhost?port=3306"
#    )

Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()

# def create_model(name,description,algorithm,precision, recall,fscore):
def create_model(name,description,algorithm):
    new_model=Model(name=name,description=description,algorithm=algorithm)
    session.add(new_model)
    session.commit()
    return new_model

# Insert an Address in the address table
def insert_training_doc(doc,model):
    new_training = TrainData(doc=doc,model=model)
    session.add(new_training)
    session.commit()

def to_dict(model_instance, query_instance=None):
    if hasattr(model_instance, '__table__'):
        return {c.name: str(getattr(model_instance, c.name)) for c in model_instance.__table__.columns}
    else:
        cols = query_instance.column_descriptions
        return { cols[i]['name'] : model_instance[i]  for i in range(len(cols)) }

def from_dict(dict, model_instance):
    for c in model_instance.__table__.columns:
        setattr(model_instance, c.name, dict[c.name])

def get_models():
    session.commit()
    models = session.query(Model).all()
    return models

def get_model(model_id):
    session.commit()
    model = session.query(Model).get(model_id)
    return model

@app.route("/modellist")
def models_data():
    return simplejson.dumps(get_models())


class ModelForm(Form):
    name = TextField('Model Name:')
    model_desc = TextField('Model Description:')
    model_algo = SelectField('Algorithm:',choices=[('svm', 'Supervised'), ('lda', 'Unsupervised')])

@app.route("/models",methods=['GET', 'POST'])
def models():
    models=get_models()
    csvdata_cnt = session.query(func.count(distinct(CSVData.filename))).one()[0]
    # csvdata = session.query(CSVData).all()

    if request.method == 'POST':
        models_data = []
        for m in models:
            models_data.append({"name": m.name, "description":m.description, "algorithm": m.algorithm, "status": m.status})
        return jsonify({"models":models_data, "models_cnt":len(models), "csvdata_cnt":csvdata_cnt})

    return render_template(
        'models.html',models=models, models_cnt = len(models), csvdata_cnt=csvdata_cnt)

def save_model(model):
    session.add(model)
    session.commit()
 
@app.route('/login', methods=['GET', 'POST'])
def do_admin_login():
    if request.form['password'] == 'irie1234' and request.form['username'] == 'admin':
        return render_template(
            'models.html')
    #     return models()
    else:
        return render_template(
            'login.html')
 
# @app.route("/logout")
# def logout():
#     return render_template(
#         'login.html')

def get_training_docs(id):
    train_data=[]
    train_data = session.query(TrainData).filter(TrainData.model_id == id)
    #doc=train_data[0].doc
    #dict_headers=json.loads(doc)
    #print(dict_headers)
    #print(dict_headers.keys())
    #df = pd.DataFrame(columns=dict_headers.keys())
    data_list=[]
    #print(len(train_data))
    for t in train_data:
        data=t.doc
        # print('Her is ')
        # print(data)
        dict_data = json.loads(data)
        #print(dict_headers.keys())
        # df=df.append(dict_data,ignore_index=True)
        data_list.append(dict_data)
    # print(data_list)
    return data_list

@app.route("/tr/<int:id>",methods=['GET', 'POST'])
def training(id):
    model = get_model(id)
    return jsonify({"status": model.status, "precision":model.precision_value, "recall":model.recall_value, "fscore":model.fscore_value, "accuracy":model.accuracy })

@app.route("/train/<int:id>",methods=['GET', 'POST'])
def train(id):
    model = get_model(id)
    model.status = "Training"
    save_model(model)

    return jsonify({"status":True})

@app.route("/suggest/<int:id>",methods=['GET', 'POST'])
def suggest(id):

    cdata = session.query(Model).filter(Model.model_id == id).first()
    try:
        json_data = json.loads(cdata.lda_model)

        suggestionsData = json_data["annotations"]
    except:
        suggestionsData = []
    # print suggestionsData
    return jsonify({"trData":suggestionsData})

@app.route("/predict/<int:id>",methods=['GET', 'POST'])
def predict(id):

    headers = {
        'Content-Type': 'application/json',
    }

    params = (
        ('modelId', id),
    )
    abstractTxt = request.form['text_data']

    data = '{"APPLICATION_ID":"xyz","ABSTRACT_TEXT":"'+ abstractTxt +'"}'
    # print '---------------'
    # print data

    # response = s.request('POST', 'http://34.228.237.18:8080/ml-runner-0.2.0/test', headers=headers, params=params, data=data, timeout=0.1)
    response = requests.post('http://34.228.237.18:8080/ml-runner-0.2.0/test', headers=headers, params=params, data=data)
    # print response.text
    # print response.status_code

    if response.status_code == 200:
        text = simplejson.loads(response.text)
        re_text = "Prediction : " + json.dumps(text["xyz"]).replace("{", "").replace("}", "")
        return jsonify(re_text)
    else:
        return jsonify("0")

@app.route("/model/<int:id>",methods=['GET', 'POST'])
def model(id):
    form = ModelForm(request.form)

    model = get_model(id)
    # print(model.name)
    form.name.data=model.name
    form.model_desc.data=model.description
    form.model_algo.data=model.algorithm
    # print form.errors
    if request.method == 'POST':
        name = request.form['name']
        model_desc = request.form['model_desc']
        model_algo = request.form['model_algo']
        # print name

        if form.validate():
            # Save the comment here.
            # print('Here')
            model.name=name
            model.description=model_desc
            model.algorithm=model_algo
            save_model(model)
            # if request.files['file'].filename != '':
            #     f = request.files['file']
            #     f.save(f.filename)
            #     save_file(model,f.filename)

        else:
            flash('All the form fields are required. ')
    form.name.data = model.name
    form.model_desc.data=model.description
    form.model_algo.data=model.algorithm
    # train_data=get_training_docs(model.model_id)

    csv_data = session.query(CSVData).filter(CSVData.model_id==id).all()

    total = len(csv_data)
    if total > 0:
        if total%30==0:
            tp = math.floor(total/30)
        else:
            tp = math.floor(total/30) + 1

        filename = csv_data[0].filename
    else:
        tp = 0
        filename = ""
    # print total
    # print csv_data[0]
    # print csv_data[0].filename
    # print(form.name.data)
    # print(train_data)
    return render_template(
        'model.html',id=id,form=form, model=model, total=tp, filename=filename)

@app.route("/model/new",methods=['GET', 'POST'])
def new():
    form = ModelForm(request.form)
    # print form.errors
    if request.method == 'POST':
        new_model = create_model(form.name.data, form.model_desc.data, form.model_algo.data)

        name = request.form['name']
        model_desc = request.form['model_desc']
        model_algo = request.form['model_algo']
        # print name

        if form.validate():
            # Save the comment here.
            # print('Here')
            new_model.name=name
            new_model.description=model_desc
            new_model.algorithm=model_algo
            save_model(new_model)
        else:
            flash('All the form fields are required. ')
        
        return redirect("/model/{}".format(new_model.model_id))
        # return render_template(
        #     'model.html',id=new_model.model_id,form=form, model=new_model, total=0, filename=None)            
    form.name.data = ""
    form.model_desc.data=""
    form.model_algo.data=""

    return render_template(
        'model.html',id=None,form=form, model=None, total=0, filename=None)

def save_file(model,path):
    """
    Open and read an Excel file
    """
    # print('Opening file')
    book = xlrd.open_workbook(path)
    worksheet = book.sheet_by_index(0)
    num_rows = worksheet.nrows - 1
    num_cells = worksheet.ncols - 1
    curr_row = -1
    header_row=worksheet.row(1)
    row_dict = {}
    while curr_row < num_rows:
        curr_row += 1
        row = worksheet.row(curr_row)
        # print 'Row:', curr_row
        curr_cell = -1
        while curr_cell < num_cells:
            curr_cell += 1
            # Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
            cell_type = worksheet.cell_type(curr_row, curr_cell)
            cell_value = worksheet.cell_value(curr_row, curr_cell)
            row_dict[worksheet.cell_value(1,curr_cell)]=cell_value
        #  print ' ', cell_type, ':', cell_value
        doc=json.dumps(row_dict)
        insert_training_doc(doc,model)


@app.route("/tag/<int:id>", methods=['GET', 'POST'])
def update_tag(id):
    try:
        tags = request.args.get('tags')
        model_id = request.args.get('model_id')
        cdata = session.query(CSVData).filter(CSVData.id == id).filter(CSVData.model_id == model_id).first()
        temp_content = simplejson.loads(cdata.content)
        temp_content["TAGS"] = tags
        cdata.content = simplejson.dumps(temp_content)
        session.commit()
        return jsonify("1")
    except:
        return jsonify("0")


@app.route('/csv', methods=['GET', 'POST'])
def getData():
    if request.method == 'GET':
        page = request.args.get('page')
        # print page
        per_page = request.args.get('per_page')
        filename = request.args.get('fname')
        model_id = request.args.get('model_id')

        tt, cc, total,ids = getCsvData(int(page), int(per_page), filename, model_id)
        # print ids
        return jsonify(simplejson.dumps({"title":tt, "content":cc, "ids":ids}))

def getCsvData(page, per_page, filename, model_id):
    content = []
    total = len(session.query(CSVData).filter(CSVData.filename == filename).filter(CSVData.model_id==model_id).all())
    cdata = session.query(CSVData).filter(CSVData.filename == filename).filter(CSVData.model_id==model_id).limit(per_page).offset((page-1)*per_page).all()
    title = simplejson.loads(cdata[0].title)
    ids = [c.id for c in cdata]
    content.extend(simplejson.loads(c.content) for c in cdata)
    if total%per_page==0:
        tp = math.floor(total/per_page)
    else:
        tp = math.floor(total/per_page) + 1
    return title, content, tp, ids

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    # print request.files['uploadfile']
    # return jsonify(1)
    if request.method == 'POST' and request.files['uploadfile'].filename != '':

        filename = upload_files.save(request.files['uploadfile'])

        try:
            model_id = request.form.get("model_id")

        except:
            return jsonify("0")

        fn = upload_files.path(filename)
        try:
            csv_data = []
            with open(fn, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                # print reader
                title = reader.fieldnames
                has_tags = False
                tags_index = len(title)
                # print title

                for tt in title:
                    if tt.upper() == "TAGS":
                        has_tags = True
                        tags_index = title.index(tt)
                        break

                # print tags_index, has_tags
                if has_tags == False:
                    title.append("TAGS")

                    title1 =  [tt for tt in title]
                    title1.insert(0, title1.pop(tags_index))
                    # print title
                    # print "NONE TAGS : ", title1
                    for row in reader:
                        csv_row ={}
                        for i in range(len(title)):
                            if row[title[i]] == None:
                                csv_row[title[i]] = ""
                            else:
                                # csv_row[title[i]] = row[title[i]].decode('utf-8', 'ignore').encode("utf-8")
                                csv_row[title[i]] = row[title[i]].decode("windows-1251")
                        csv_data.append(
                            CSVData(
                                filename=filename,
                                title=simplejson.dumps(title1),
                                content=simplejson.dumps(csv_row),
                                model_id=model_id))
                else:

                    title1 = [tt for tt in title]
                    title1.insert(0, title1.pop(tags_index).upper())
                    # print title1
                    for row in reader:
                        csv_row = {}
                        for i in range(len(title)):
                            if title[i].upper() == "TAGS":
                                csv_row["TAGS"] = row[title[i]].decode("windows-1251")
                            else:
                                csv_row[title[i]] = row[title[i]].decode("windows-1251")
                        # print "HAS TAGS : ", csv_row
                        csv_data.append(
                            CSVData(
                                filename=filename,
                                title=simplejson.dumps(title1),
                                content=simplejson.dumps(csv_row),
                                model_id=model_id))

                session.add_all(csv_data)
                session.commit()
            tt, cc, total, ids = getCsvData(1, 30, filename, model_id)
            return jsonify(simplejson.dumps({"total":total, "fname":filename}))
        except Exception as e:
            print e
            return jsonify("0")

# def write_json(data, json_file, format):
#     with open(json_file, "w") as f:
#         if format == "pretty":
#             f.write(json.dumps(data, sort_keys=False, indent=4, separators=(',', ': '),encoding="utf-8",ensure_ascii=False))
#         else:
#             f.write(json.dumps(data))

@app.route("/visualize/<int:id>",methods=['GET', 'POST'])
def visualize(id):
    if request.method == 'GET':
        chatData = getJson(id)
        # print "-------------------"
        # print chatData
        return render_template(
            'visualize.html', chatData=chatData)

def getJson(modelId):
    
    cdata = session.query(Model).filter(Model.model_id == modelId).first()
    # print "--------------"
    chat_data = {}
    chat_data['name'] = 'topics'
    chat_data['children'] = []

    if cdata.lda_model == None:
        return False

    json_data = json.loads(cdata.lda_model)

    data_buf = json_data["topics"]

    for index in data_buf:

        child = {}
        child['name'] = index['label'].encode('utf-8')
        child['children'] = []

        # print index['id']
        # print index['words']
        # print "======================"

        for word in index['words']:

            value = {}
            value['name'] = word.encode('utf-8')
            value['size'] = int(index['words'][word])

            child['children'].append(value)

        chat_data['children'].append(child)

    return chat_data

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)