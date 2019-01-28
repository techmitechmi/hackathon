from flask import Flask, request, flash, render_template, flash, redirect, url_for, session, Blueprint
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt as sha
from flask_session import Session
from validate_email import validate_email
from app import *

main = Blueprint('main', __name__)


@main.route("/", methods=['POST', 'GET'])
def index():
    return render_template("index.html")


@main.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        captcha_response = request.form['g-recaptcha-response']
        if is_human(captcha_response):
            team_name = request.form['team_name']
            team_id = query_db("select team_id from teams where LOWER(team_name) = %s",(team_name.lower(),))
            if team_id is not None:
                flash("Team Name Already Exists!", 'danger')
                print('Team Name Already Exists!')
                return redirect(url_for("main.register"))
            else:
                rolls = []
                names = []
                years = []
                for i in range(1,5):
                    if i !=4:
                        rolls.append(request.form['roll'+str(i)])
                        names.append(request.form['name'+str(i)])
                        years.append(request.form['year'+str(i)])
                    else:
                        if request.form['roll'+str(i)] is None or request.form['name'+str(i)] is None:
                            rolls.append(None)
                            names.append(None)
                            years.append(None)
                        else:
                            rolls.append(request.form['roll'+str(i)])
                            names.append(request.form['name'+str(i)])
                            years.append(request.form['year'+str(i)])


                if len(rolls) > len(set(rolls)):
                    flash("Duplicate Entries not allowed!", "danger")
                    return redirect(url_for("main.register"))

                student_check = []
                for i in range(0,4):
                    student_check.append(query_db("select s"+str(i+1)+"_roll from teams where s1_roll=%s or s2_roll=%s or s3_roll=%s or s4_roll=%s",(rolls[i],rolls[i],rolls[i],rolls[i])))

                for check in student_check:
                    if check is not None:
                        flash("Some students already registered!", "danger")
                        return redirect(url_for("main.register"))

                execute_db("INSERT INTO teams(team_name, s1_roll, s2_roll, s3_roll, s4_roll, s1_name, s2_name, s3_name, s4_name, s1_year, s2_year, s3_year, s4_year) Values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(
                    team_name,
                    rolls[0],
                    rolls[1],
                    rolls[1],
                    rolls[3],
                    names[0],
                    names[1],
                    names[2],
                    names[3],
                    years[0],
                    years[1],
                    years[2],
                    years[3],
                ))
                flash("Applied Successfully", 'success')
                return redirect(url_for("main.register"))
            return render_template("register.html")
        else:
            flash("Sorry! Bots not allowed.","danger")
            return redirect(url_for("main.register"))