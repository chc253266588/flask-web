from flask import Flask,render_template
from flask_script import Manager
from flask_bootstrap import Bootstrap

from flask_wtf import Form
from wtforms import StringField,SubmitField,PasswordField
from wtforms.validators import Required,Length

class NameForm(Form):
	name = StringField("username ",validators=[Required()])
	passwd = PasswordField("password ",validators=[Length(6)]) 
	submit = SubmitField('Submit')

app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'hard to guess string!'

@app.route("/",methods=['GET','POST'])
def index():
	name = None
	alert = None
	form = NameForm()
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
		alert = 'please input you username!'
	return render_template('index.html')

@app.route("/user/<name>")
def user(name):
	return render_template("user.html",name=name)

@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"),404

if __name__ == '__main__':
	manager.run()
