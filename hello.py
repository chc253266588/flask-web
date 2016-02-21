from flask import Flask,render_template,redirect,session,url_for,flash
from flask_script import Manager,Shell
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask.ext.mail import Mail,Message
from threading import Thread
import os


from flask_wtf import Form
from wtforms import StringField,SubmitField,PasswordField
from wtforms.validators import Required,Length

class NameForm(Form):
	name = StringField("username ",validators=[Required()])
	passwd = PasswordField("password ",validators=[Length(6)]) 
	submit = SubmitField('Submit')

def make_shell_context():
	return dict(app=app,db=db,User=User,Role=Role)

app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app,db)
mail = Mail(app)

manager.add_command('db', MigrateCommand)
manager.add_command("shell",Shell(make_context=make_shell_context))

app.config['SECRET_KEY'] = 'hard to guess string!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost/database'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['MAIL_SERVER'] = 'postbox.jianke.com'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') 
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]' 
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <chenhongchen@jianke.com>'
app.config['FLASK_ADMIN'] = os.environ.get('FLASK_ADMIN')

class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	users = db.relationship('User', backref='role')
	def __repr__(self):
		return '<Role %r>' % self.name
class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True, index=True)
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
	def __repr__(self):
		return '<User %r>' % self.username

def send_email(to, subject, template, **kwargs):
	msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to]) 
	msg.html = render_template(template + '.txt', **kwargs)
	msg.html = render_template(template + '.html', **kwargs)
	thr = Thread(target=send_async_email,args=[app,msg])
	thr.start()
	return thr

def send_async_email(app,msg):
	with app.app_context():
		mail.send(msg)

@app.route("/",methods=['GET','POST'])
def index():
	form = NameForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.name.data).first()
		if user is None:
			user = User(username = form.name.data)
			db.session.add(user)
			session['known'] = False
			if app.config['FLASK_ADMIN']:
				send_email(app.config['FLASK_ADMIN'],'New User','mail/new_user',user=form.name.data)
		else:
			session['known'] = True
		session['name']=form.name.data
		session['password']=form.passwd.data
		form.name.data = ''
		return redirect(url_for('index'))	
	return render_template('index.html',name=session.get('name'),passwd=session.get('password'),form=form,known=session.get('known',False))

@app.route("/user/<name>")
def user(name):
	return render_template("user.html",name=name)

@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"),404

if __name__ == '__main__':
	manager.run()
