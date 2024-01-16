from flask import jsonify
from Package.Models.Project import Project
from Package.Models.Team import Team
from Package.Db import my_database



class ProjectService:
    @staticmethod
    def get_project_list(page,per_page):
        Project_list = Project.query.paginate(
            page=page, 
            per_page=per_page,
            error_out=False
        )
        formated_data = {
            "items":[ project.toDict() for project in Project_list ],
            "page": Project_list.page,
            "per_page":Project_list.per_page,
            "total_pages":Project_list.pages,
            "total_items":Project_list.total
        }
        return formated_data
    @staticmethod
    def get_project_by_id(project_id):
        #define the return object :
        returnValues = {
            "state":False,
            "data":{}
        }
        projetTarget = Project.query.filter_by(id=project_id).first()
        if not projetTarget:
            return returnValues
        #update the return values:
        returnValues["state"] = True
        returnValues["data"] = projetTarget.toDict()
        return returnValues 
    @staticmethod
    def get_project_by_name(project_name):
        #make sure that the project name is in lowercase:
        name = str(project_name).lower()
        returnValues = {
            "state":False,
            "data":{}
        }
        #try to find the project by name:
        projectToFind = Project.query.filter_by(name=name).first()
        if not projectToFind:
            return returnValues
        #update states :
        returnValues["state"] = True
        returnValues["data"] = projectToFind.toDict()
        return returnValues
    #get the list of teams information that working on the project:
    @staticmethod
    def get_project_team_list(project_id):
        #get the lis of team id as a first step:
        team_id_list = Project.getTeamList(project_id)
        #check if the project is already has team :
        if len(team_id_list) == 0:
            return []
        team_list = []
        for team_id in team_id_list:
            #get the current team info by id :
            target = Team.query.filter_by(id=team_id).first()
            if target:
                team_list.append( target.toDict())
        return team_list
    #update project manager :
    @staticmethod
    def update_project_manager(project_id, manager_id):
        try:
            projectToUpdate = Project.query.filter_by(id=project_id).first()
            #set the new manager id :
            projectToUpdate["manager"] = manager_id
            #save the session : 
            my_database.session.commit()
            return True
        except Exception as e:
            print("Error updating project manager: ", e)
            my_database.session.rollback()
            return False
    #update project status :
    @staticmethod
    def update_project_status(project_id, new_status):
        try:
            projectToUpdate = Project.query.filter_by(id=project_id).first()
            projectToUpdate["state"] = new_status
            my_database.session.commit()
            return True
        except Exception as e:
            print("Error updating project status: ", e)
            my_database.session.rollback()
            return False
    #update project details :
    @staticmethod
    def update_project_details(newName="", newDescription="", newRepository=""):
        #check the project new name :
        try:
            projectTarget = Project.query.filter_by(name=newName).first()
            if projectTarget :
                return False
            
            #update the provided information : 
            if not newName == "":
                projectTarget["name"] = newName
            if not newDescription == "":
                projectTarget["description"] = newDescription
            if not newRepository == "":
                projectTarget["url"] = newRepository
            #sve the new project info : 
            my_database.session.commit()
            return True
        except Exception as e:
            print("Error updating project details : ", e)
            my_database.session.rollback()
            return False
    #create new project static method :
    @staticmethod
    def create_project(
        name="", manager="", 
        description="", state="", url=""
        ):
        #try to create new project instance :
        try:
            projectTarget = Project(name, manager,url, description,state)
            #insert it to the sessions : 
            my_database.session.add(projectTarget)
            #save the state :
            my_database.session.commit()
            return True
        except Exception as e:
            print("Error creating project instance ", e)
            my_database.session.rollback()            
            return False  