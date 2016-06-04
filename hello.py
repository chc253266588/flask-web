from flask import Flask,render_template,redirect,session,url_for,flash
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
	form = NameForm()
	if form.validate_on_submit():
		old_name = session.get('name')
		if old_name is not None and old_name != form.name.data:
			flash('Looks like you have changed your name!')
		session['name']=form.name.data
		session['password']=form.passwd.data
		return redirect(url_for('index'))	
	return render_template('index.html',name=session.get('name'),passwd=session.get('password'),form=form)

@app.route("/user/<name>")
def user(name):
	return render_template("user.html",name=name)

@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"),404

if __name__ == '__main__':
	manager.run()
