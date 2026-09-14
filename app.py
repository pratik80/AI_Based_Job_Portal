from flask import Flask, render_template, request,redirect,url_for,session
import sqlite3
from flask_sqlalchemy import SQLAlchemy
import sys, fitz
import numpy
import pickle
import spacy
import pickle
import random
import nlp
nlp_model = spacy.load('nlp_model')
import os
import re

from sqlalchemy import desc


app = Flask(__name__)
app.config['SECRET_KEY'] = 'This is a secret key required for session'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///jobportal.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app)
UPLOAD_FOLDER3 = 'E:\\Pratik\\FINAL YEAR PROJECT\\Flask\\static\\jobResumes'
app.config['UPLOAD_FOLDER3'] = UPLOAD_FOLDER3
class applicantLogin(db.Model):  
    email = db.Column(db.String(200), primary_key=True )
    password = db.Column(db.String(200), nullable=False)

class recruiterLogin(db.Model):
    email = db.Column(db.String(200), primary_key=True)
    password = db.Column(db.String(200), nullable=False)
class jobNotice(db.Model):
    email = db.Column(db.String(100), primary_key=True)
    jobtitle = db.Column(db.String(100), nullable=False)
    jobdesc = db.Column(db.String(10000),nullable=False)
    Jinfo = db.Column(db.String(10000))

class jobApplicants(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    Aemail = db.Column(db.String(100))
    Remail = db.Column(db.String(100))
    Ainfo = db.Column(db.String(10000))
    scores = db.Column(db.Integer,default=-1)



@app.route("/")
def start():
    return redirect("User.html")

@app.route('/User.html',methods=['GET', 'POST'])
def applogin():
    if request.method=='POST':
        if "newemail" in request.form:
            formemail = request.form['newemail']
            row  = applicantLogin.query.filter_by(email = formemail).first()
            if row is not None:
                return render_template('User.html',check1=True,check2=False)
            else:
                formemail = request.form['newemail']
                formpassword = request.form['newpassword']
                applicant = applicantLogin(email = formemail,password = formpassword )
                db.session.add(applicant)
                db.session.commit()
                session['email'] =  formemail
                return redirect("home_apl.html")

        elif "email" in request.form:
            formemail = request.form['email']
            formpassword = request.form['password']
            row  = applicantLogin.query.filter_by(email = formemail).first()
            if row is None:
                return render_template('User.html',check1=False,check2=True)
            else:
                if row.password == formpassword:
                    session['email'] =  formemail
                    return redirect("home_apl.html")
                else:
                    return render_template('User.html',check1=False,check2=True)

                    
    return render_template('User.html',check1=False,check2=False)

@app.route('/home_apl.html',methods=['GET', 'POST'])
def applicant():
    return render_template('home_apl.html')



@app.route('/Admin.html',methods=['GET', 'POST'])
def reclogin():
    if request.method=='POST':
        if "newemail" in request.form:
            formemail = request.form['newemail']
            row  = recruiterLogin.query.filter_by(email = formemail).first()
            if row is not None:
                return render_template('Admin.html',check1=True,check2=False)
            else:
                
                formemail = request.form['newemail']
                formpassword = request.form['newpassword']
                recruiter = recruiterLogin(email = formemail,password = formpassword )
                db.session.add(recruiter)
                db.session.commit()
                session['email'] =  formemail
                return redirect("home_rec.html")

        elif "email" in request.form:
            formemail = request.form['email']
            formpassword = request.form['password']
            row  = recruiterLogin.query.filter_by(email = formemail).first()
            if row is None:
                return render_template('Admin.html',check1=False,check2=True)
            else:
                if row.password == formpassword:
                    session['email'] =  formemail
                    return redirect("home_rec.html")
                else:
                    return render_template('Admin.html',check1=False,check2=True)

    return render_template('Admin.html',check1=False,check2=False)


@app.route("/home_rec.html")
def user():
    return render_template('home_rec.html')

@app.route('/jobnotice.html',methods=['GET', 'POST'])
def jobnotice():
    email = session['email']
    if request.method=='POST':
        jobtitle = request.form['formJobtitle']
        jobdesc = request.form['formJobdesc']
        jobdesc = jobdesc.strip()
        text = jobdesc
        tx = " ".join(text.split('\n'))

        doc = nlp_model(tx)
        info={}
        for ent in doc.ents:
            entityName = ent.label_.upper()
            entity = ent.text.strip()
            lst=[]
            for i in re.split(r"[-;,:!.\s@\\\/+\*(){}<>\[\]']\s*",entity):
                if i!="":
                    lst.append(i.lower())

            if entityName in info:
                info[entityName].extend(lst)
            else:
                info[entityName]=lst

        notice = jobNotice(email = email, jobtitle = jobtitle, jobdesc = jobdesc,Jinfo=str(info))
        db.session.add(notice)
        db.session.commit()
        row = jobNotice.query.filter_by(email = email).first()
        rows = jobApplicants.query.filter_by(Remail = email).all()
        return render_template('jobnotice.html',check=False,notice=row,count=len(rows),email=email)

    else:
        row = jobNotice.query.filter_by(email = email).first()
        rows = jobApplicants.query.filter_by(Remail = email).all()
        if row is None:
            return render_template('jobnotice.html',check=True,email = email)
        else:
            return render_template('jobnotice.html',check=False,notice=row,count=len(rows),email = email)

@app.route('/shortlist.html',methods=['GET', 'POST'])
def shortlist():
    email  = session['email']
    rows = jobApplicants.query.filter_by(Remail = email).all()
    if len(rows) == 0:
        return render_template('shortlist.html',check = True)
    else:
        row = jobNotice.query.filter_by(email=email).one()
        jd=eval(row.Jinfo)
        for i in rows:
            score=0
            resumeinfo=eval(i.Ainfo)
            if i.scores==-1:
                for j,k in jd.items():
                    if j in resumeinfo:
                        for l in k:
                            if l in resumeinfo[j]:
                                score+=1
                i.scores=score
                db.session.commit()

        rows = jobApplicants.query.filter_by(Remail=email).order_by(desc(jobApplicants.scores)).all()

        return render_template('shortlist.html',check = False, applicants = rows)

@app.route('/job.html',methods=['GET', 'POST'])
def job():
    appEmail =  session['email']

    if request.method=='POST':
        appEmail =  session['email']
        print(request.form)
        recEmail = request.form['Remail']
        resume = request.files['resume']
        resume.save(os.path.join(app.config["UPLOAD_FOLDER3"],appEmail+".pdf"))

        fname = app.config["UPLOAD_FOLDER3"]+"\\"+appEmail+".pdf"
        doc = fitz.open(fname)
        text = ""
        for page in doc:
            text = text + str(page.get_text())
        tx = " ".join(text.split('\n'))

        doc = nlp_model(tx)
        info={}
        for ent in doc.ents:
            entityName = ent.label_.upper()
            entity = ent.text.strip()
            lst=[]
            for i in re.split(r"[-;,:!.\s@\\\/+\*(){}<>\[\]']\s*",entity):
                if i!="":
                    lst.append(i.lower())

            if entityName in info:
                info[entityName].extend(lst)
            else:
                info[entityName]=lst
        
        jobApp = jobApplicants(Aemail = appEmail, Remail = recEmail, Ainfo=str(info))
        print(jobApp)
        db.session.add(jobApp)
        db.session.commit()

    jobs = jobNotice.query.all()
    applied = jobApplicants.query.filter_by(Aemail = appEmail).all()




    for i in jobs:

        for j in applied:
            if i.email == j.Remail:
                print(jobs)
                print(i)

                jobs.remove(i)
                
    if len(jobs) == 0:
        return render_template('job.html',check = True)
    else:
        return render_template('job.html',check = False, jobs = jobs)

if __name__ =="__main__":
    app.run(debug=True)