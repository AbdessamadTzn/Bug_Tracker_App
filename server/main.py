from flask import Flask,request,jsonify
from Package import *
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
from Package.Db import my_database,setup_user_team_role, setup_team_project
#impotrt all needed models : 
from Package.Models.User import User
from Package.Models.Team import Team
from Package.BluePrints import API_PREFIXER
import os

#import all the bluePrints :
from Package.BluePrints.User import UserController 
from Package.BluePrints.Team import TeamController
from Package.BluePrints.Project import ProjectController

#load env variables: 
load_dotenv()

my_app = Flask(__name__)
#setup a sqlalchemy database instance :

cors = CORS(my_app)
my_app.config['CORS_HEADERS'] = 'Content-Type'

my_app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
my_app.config["Mode"] = os.getenv("PY_MODE")
my_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

my_database.init_app(my_app)
#register all the bluePrints:

my_app.register_blueprint(UserController)
my_app.register_blueprint(TeamController)
my_app.register_blueprint(ProjectController)


@my_app.route(API_PREFIXER,methods=["GET"])
@cross_origin()
def ping():
	return jsonify({"message":"Api pong"}),200


if __name__=="__main__":
	my_app.secret_key = 'super secret key'
	my_app.config['SESSION_TYPE'] = 'filesystem'
	print(f"--> Bug tracker runing on : http://localhost:5000{API_PREFIXER} \n")
	with my_app.app_context():
		setup_user_team_role()
		setup_team_project()
		my_database.create_all()
		alreadyUser = User.query.filter_by(userName='BugAdminClient').first()
		if not alreadyUser:
			temp_user = User(
				username='BugAdminClient', 
				password='BugAdmin123456',
			)
			my_database.session.add(temp_user)
			my_database.session.commit()
	my_app.run(debug=(my_app.config["Mode"] =="Dev"))