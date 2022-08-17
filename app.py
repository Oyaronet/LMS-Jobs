# IMPORT REQUIRED PACKAGES #
from enum import unique
from turtle import down
from flask import Flask, render_template, redirect, url_for, flash,request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField, SubmitField
from wtforms.validators import Length, DataRequired
from flask_sqlalchemy import SQLAlchemy
from openpyxl import Workbook 

app = Flask(__name__)
app.config["SECRET_KEY"] = "5155f718cc1702b2e8aba054bc1644f1"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://bdmleradqobudb:9f8162c6ed03243914b7040cd52d91f7cf180bd80584afc395c49c6ba1af73bc@ec2-44-193-178-122.compute-1.amazonaws.com:5432/d3g0h66s74t3q"

db = SQLAlchemy(app)

options = ["Select Download Option", "PDF", "Spreadsheet"]

# FORMS #
class RegistrationForm(FlaskForm):
    firstname = StringField('Firstname', validators=[DataRequired(),
                Length(max=20, min=2)])
    surname = StringField('Surname', validators=[DataRequired(), 
                Length(max=20, min=2)])
    id = IntegerField('ID No',  validators=[DataRequired()])
    submit = SubmitField('REGISTER')

class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    login = SubmitField('LOGIN')


class CheckStatusForm(FlaskForm):
    searchInput = IntegerField(validators=[DataRequired()])
    search_btn = SubmitField('Search')

class DownloadOption(FlaskForm):
    options = SelectField(choices=options)

# CLASSES TO BE MAPPED INTO DATABASE TABLES
class Applicant(db.Model):
    applicant_id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(20), nullable=False)
    idNo = db.Column(db.Integer, nullable=False, unique=True)

    def __repr__(self):
        return f'Fullname: {self.firstname} { self.surname} Id No: {self.idNo}'


# LANDING/REGISTRATION PAGE #
@app.route("/", methods=["GET", "POST"])
def registration():
    reg_form = RegistrationForm()
    alert = False
    # check the validity of submitted registration details
    if reg_form.validate_on_submit():
        registration_details = {
             # strip any blank spaces
            "firstname" : reg_form.firstname.data.strip(),
            "surname" : reg_form.surname.data.strip(), 
            "id" : reg_form.id.data   
        }

        # initantiate the Applicant class
        new_applicant = Applicant(
                firstname=registration_details["firstname"],
                surname=registration_details["surname"],
                idNo=registration_details["id"],
            )
        db.create_all() # create database

        # check if the applicant has already applied
        try:
            # add applicant to the database if there is nothing wrong
            db.session.add(new_applicant)
            db.session.commit()
            alert = flash("Congratulations! You have been Registered successfuly!", 'success')
        except:
            # give user warning that something went wrong
            alert = flash("Sorry there is a user with that ID in the System!", 'danger')
            return redirect(url_for("registration"))
    return render_template('registration.html', form=reg_form)


# ADMIN LOGIN #
@app.route("/adminLogin", methods=["GET", "POST"])
def adminLogin():
    adm_login_form = AdminLoginForm()
    if adm_login_form.validate_on_submit():
        if adm_login_form.username.data == "Oyaro" and adm_login_form.password.data == "code":
            # query applicants data from the database
            applicants = Applicant.query.all()
            download_form = DownloadOption()
            return render_template('admindashboard.html', 
                applicants=applicants, form=download_form)
        else:
            alert = flash('''Failed to log you in! Please check
                you login credentials and try again!''', 'danger')
            return render_template('admin.html', form=adm_login_form)
    return render_template('admin.html', form=adm_login_form)


# CHECK REGISTRATION STATUS #
@app.route("/checkRegStatus", methods=["GET", "POST"])
def checkRegStatus():
    search_form = CheckStatusForm()
    if search_form.validate_on_submit():
        search_id_value = search_form.searchInput.data
        # get applicant from the database
        search_result = Applicant.query.filter_by(idNo=search_id_value).first()

        # inform the user that he/she is registered and display his/her details
        if search_result != None:
            return render_template('registered.html', applicant_info=search_result)
        
        # redirect the user to the same page with an alert that they're not registred
        else:
            alert = flash('''Sorry You are not registered! Please visit 
                registration tab above to register!''', 'danger')
            return render_template('search.html', form=search_form)
    return render_template('search.html', form=search_form)


# DOWNLOAD APPLICANT LIST #
@app.route("/download_applicants_list", methods=["GET", "POST"])
def download_applicants_list():
    return 'Working on Download Functionality! Please be patient.'









# RUN THE APP #
if __name__ == "__main__":
    app.run(debug=True)