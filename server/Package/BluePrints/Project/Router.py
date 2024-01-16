from Package.Models.Project import Project
from Package.Models.User import User
from Package.BluePrints.Project.Service import ProjectService
from Package.BluePrints import Project_PREFIXER, API_PREFIXER
from flask import request, jsonify, Blueprint 
# import flask cors configuration lib : 
from flask_cors import cross_origin

from Package.BluePrints.User.Service import UserService




project_api = Blueprint("project_api", __name__)
Prefixer = API_PREFIXER+Project_PREFIXER


#test ping :
@project_api.route(Prefixer+"/Ping", methods=["GET"])
@cross_origin()
def ping_handler():
        return jsonify({"Response": "Project Pong"}),200

#get all project list :
@project_api.route(Prefixer+"/List", methods=["GET"])
@cross_origin()
def get_project_list():
        #get metadata from request params :
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page",10))
        #call static method to get project list:
        projectList = ProjectService.get_project_list(page,per_page)
        return jsonify({"data": projectList}),200

#get a project by id :
@project_api.route(Prefixer+"/<project_id>", methods=["GET"])
@cross_origin()
def get_project_by_id(project_id):
        #try to get the project by id :
        projectFindResult = ProjectService.get_project_by_id(project_id)
        #check the values :
        if not projectFindResult["state"]:
                return jsonify({"message": "Project not found"}),404
        return jsonify({"data": projectFindResult["data"]}),200

#get project by name :
@project_api.route(Prefixer+"/Find/Name/<project_name>", methods=["GET"])
@cross_origin()
def get_project_by_name(project_name):
        try:
                projectTarget = ProjectService.get_project_by_name(project_name)
                if not projectTarget["state"]:
                        return jsonify({"message": "Project not found"}),404
                return jsonify({"data": projectTarget["data"]}),202
        except Exception as e:
                print( e )
                return jsonify({"message": "Faild to find Project"}),400

#get a project manager by the project id :
@project_api.route(Prefixer+"/Manager/<project_id>", methods=["GET"])
@cross_origin()
def get_project_manager(project_id):
        #check if the project exist :
        isProjectExist = ProjectService.get_project_by_id(project_id)
        if not isProjectExist:
                return jsonify({"message": "Project not found"}),404
        #project is already exit : extract the manager id from the project dict :
        manager_id = isProjectExist["manager"]
        #call user service to get the manager ( user ) by id :
        managerTarget = User.query.filter_by(id=manager_id).first()
        if not managerTarget:
                return jsonify({"message": "Manager not found"}),404
        return jsonify({"data":managerTarget.toDict()}),202

#get teams information that working on the project by project id :
@project_api.route(Prefixer+"/TeamList/<project_id>", methods=["GET"])
@cross_origin()
def get_prject_team_list(project_id):
        #check if the project exist or not : 
        projectTarget = ProjectService.get_project_by_id(project_id)
        if not projectTarget:
                return jsonify({"message": "Project not found"}),404
        #get the alist of teams id that workin on this project :
        project_team_list = ProjectService.get_project_team_list(project_id)
        return jsonify({"data": project_team_list}),200

#update project manager by id :
@project_api.route(Prefixer+"/<project_id>/Manger/New/<user_id>", methods=["PUT"])
@cross_origin()
def update_project_manager(project_id, user_id):
        #check if project exist :
        projectTarget = ProjectService.get_project_by_id( project_id )
        if not projectTarget: return jsonify({"message": "Project not found"}),404
        #check if the user exist :
        userTarget = UserService.alreadyExists( user_id )
        if not userTarget: return jsonify({"message": "User not found"}),404
        #call the static service to set the new project manager :
        updateManagerStatus = ProjectService.update_project_manager(project_id, user_id)
        if not updateManagerStatus: return jsonify({"message": "Faild to Update Project manager"}),500
        return jsonify({"message": "Manger Updated Successufully"}),202

#update project state by project id :
@project_api.route(Prefixer+"/<project_id>/State",methods=["PUT"])
@cross_origin()
def update_project_state(project_id):
        #check if project exist :
        projectTarget = ProjectService.get_project_by_id( project_id )
        if not projectTarget: return jsonify({"message": "Project not found"}),404
        #get the new state from request  body :
        paylaod = request.json
        if "state" in paylaod:
                newState = paylaod["state"]
                #update process :
                stateUpdated = ProjectService.update_project_status(project_id, newState)
                if not stateUpdated:
                        return jsonify({"message": "Failed to update project state"}),500
                return jsonify({"message": "Project status updated successfully"}),202
        return jsonify({"message": "New State is required"}),400

#update project infor ( name , description and repo ) by project id 
@project_api.route(Prefixer+"/<project_id>", methods=["PUT"])
@cross_origin()
def update_project_infor(project_id):
         #set to update state :
        toUpdate = False
        newName = ""
        newDescription = ""
        newRepo = ""
        #check if project is already exist :
        projectTarget = ProjectService.get_project_by_id( project_id )
        if not projectTarget: return jsonify({"message": "Project not found"}),404
       
        #get the new info  from request  body :
        newPayalod = request.json
        #check if containg some new props to set : 
        if "name" in newPayalod:
                newName = newPayalod["name"]
                toUpdate = True
        if "description" in newPayalod:
                newDescription = newPayalod["description"]
                toUpdate = True
        if "repo" in newPayalod:
                newRepo = newPayalod["repo"]
                toUpdate = True
        #check if the update state if on true :
        if not toUpdate:
                return jsonify({"message":"Project is up to date"}),200
        #call the update static service :
        updatedState = ProjectService.update_project_details(
                newName,
                newDescription,
                newRepo
        )
        #check update state :
        if not updatedState:
                return jsonify({"message": "Failed to update project"}),501
        return jsonify({"message": "Project details updated successufully"}),202

#create new project :
@project_api.route(Prefixer+"/<user_id>/new", methods=["POST"])
@cross_origin()
def create_project(user_id):
        #check if user already exists :
        userTarget = UserService.alreadyExists( user_id )
        if not userTarget: return jsonify({"message": "User not found"}),404
        #extract the new project data payload from the request :
        projectPayload = request.json
        if not "name" in projectPayload:
                return jsonify({"message": "Project name is required"}),404
        if not "manager" in projectPayload:
                return jsonify({"message": "Manager id is required"}),404
        if not "url" in projectPayload:
                return jsonify({"message": "ressource url is required"}),404
        projectName = str(projectPayload["name"]).capitalize()
        projectMangerId = projectPayload["manager"]
        projectUrl = projectPayload["url"]
        #check if the project name is unique :
        projectTarget = Project.query.filter_by(name=projectName).first()
        if projectTarget:
                return jsonify({"message":"Project name is already in use"}),403
        #create a new project:
        ProjectCreatedStatus = ProjectService.create_project(
                projectName,projectMangerId,"","",projectUrl
        )
        #check the status:
        if not ProjectCreatedStatus: 
                return jsonify({"message":"Faild to Create Project "}),403
        return jsonify({"message":"Project Created successufully "}),201