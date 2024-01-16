from Package.Models.Team import Team
from Package.Models.User import User
from Package.Db import my_database
from sqlalchemy import text

def create_team(team_data):
    # get connexion with atlas mongodb:
    path = dirname(abspath(__file__)) + '/.env'
    load_dotenv(path)
    connexion_uri = os.getenv('DBA_URI')
    # get connexion with atlas mongodb :
    response = 1
    my_client = MongoClient(connexion_uri)
    my_db = my_client.BUG_TRAKER_DBA
    # insert document :
    try:
        my_db.Team.insert_one({
            'TeamName':team_data['TeamName'],
            'TeamManager':team_data['TeamManeger'],
            'TeamGroup':[],
            'TeamProject':[],
            'ProjectState':[]
        })
    except Exception as e:
        response = -1
    return response

def add_user_to_team(user_target,team_target):
    # get connexion with atlas mongodb:
    path = dirname(abspath(__file__)) + '/.env'
    load_dotenv(path)
    connexion_uri = os.getenv('DBA_URI')
    # get connexion with atlas mongodb :
    response = 1
    my_client = MongoClient(connexion_uri)
    my_db = my_client.BUG_TRAKER_DBA
    # try  update contrib liste :
    try:
        my_db.Team.update_one({
            #filter:
            'TeamName':team_target
        },{
            #update scope:
            '$addToSet':{
                'TeamGroup':user_target
            }
        })
    except Exception as e:
        print("[add user to team contrib error ] : "+str(e))
        response = -1
    return response

def get_contributors(team):
    # define cofig vars : 
    path = dirname(abspath(__file__)) + '/.env'
    load_dotenv(path)
    connexion_uri = os.getenv('DBA_URI')
    # get connexion with atlas mongodb :
    my_client = MongoClient(connexion_uri)
    my_db = my_client.BUG_TRAKER_DBA
    try:
        return list(my_db.Team.find({
            # filter :
            'TeamName':team   
        },{
            '_id':0,
            'TeamName':0,
            'TeamManager':0,
            'TeamProject':0,
            'ProjectState':0
        }))[0]['TeamGroup']
    except Exception as e:
        print("[error get tema contribs ]:  "+str(e))
        return [] 



#define my service class : 
class TeamService:
    @staticmethod
    def getTeamListPaginated(page=1,per_page=10):
        teamList = Team.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        formated_data = {
            'items':[team.toDict() for team in teamList],
            'page':teamList.page,
            'per_page':teamList.per_page,
            'total_pages':teamList.pages,
            'total_items':teamList.total
        }
        return formated_data
    @staticmethod
    def alreadyExist(teamId=""):
        teamtarget = Team.query.filter_by(id=teamId).first()
        if teamtarget:
            return True
        return False
    @staticmethod
    def getTeamAdmin(teamId=""):
        #get the team data :
        teamTarget = Team.query.filter_by(id=teamId).first()
        if not teamTarget:
            return
        admin = teamTarget.toDict()["admin"]
        #get the admin data by id :
        adminTarget =  User.query.filter_by(id=admin).first()
        return adminTarget.toDict()
    @staticmethod
    def checkTeamByName(teamName):
        target = Team.query.filter_by(name=teamName).first()
        if not target:
            return False
        return True
    @staticmethod
    def updateteamName(teamId, newTeamName):
        try:
            target = Team.query.filter_by(id=teamId).first()
            target.name = newTeamName
            #save the session updates : 
            my_database.session.commit()
            return True
        except Exception as e:
            print( e )
            my_database.session.rollback()
            return False
    @staticmethod
    def getTeamMembers(teamId):
        teamtarget = Team.query.filter_by(id=teamId).first()
        return teamtarget.get_contributors()
    @staticmethod
    def setNewTeamAdmin(teamId, userId):
        try:
            #get the team target : 
            target = Team.query.filter_by(id=teamId).first()
            #set the new admin id : 
            target.admin = userId
            #save the session updates : 
            my_database.session.commit()
            return True
        except Exception as e:
            print( e )
            my_database.session.rollback()
            return False 
    @staticmethod
    def createNewTeam(teamName, teamAdminId):
        try:
            teamToInsert = Team(teamName, teamAdminId)
            #save new team item :
            my_database.session.add(teamToInsert)
            my_database.session.commit()
            return { "created": True, "target": teamToInsert.toDict()}
        except Exception as e:
            print( e )
            return { "created": False, "target": {}}
    #add user to team :
    @staticmethod
    def add_contributor(team_id, user_id, role_name):
        try:
            # try to add the user to the team
            new_team_user_relation = {
                "user_id": user_id,
                "team_id": team_id,
                "role": role_name
            }
            # use SQLAlchemy's text function to define the SQL statement
            sql_statement = text(
                "INSERT INTO user_team_role (user_id, team_id, role) VALUES (:user_id, :team_id, :role)"
            )
            # execute the statement with parameters using the session
            my_database.session.execute(sql_statement, new_team_user_relation)
            my_database.session.commit()

            return True
        except Exception as e:
            print(e)
            return False
    #check if a user is a member of the team .
    @staticmethod
    def is_team_member(team_id, user_id):
        # Use SQLAlchemy's text function to define the SQL SELECT statement
        select_statement = text(
            "SELECT * FROM user_team_role WHERE team_id = :team_id AND user_id = :user_id"
        )
        # Execute the SELECT statement with parameters using the session
        user_relationship = my_database.session.execute(select_statement, {"team_id": team_id, "user_id": user_id}).fetchone()
        if user_relationship:
            return True
        return False
    
    #update member role in a team :
    @staticmethod
    def update_member_role( team_id, member_id, new_role ):
        try:
            # Use SQLAlchemy's text function to define the SQL UPDATE statement
            update_statement = text(
                "UPDATE user_team_role SET role = :new_role WHERE team_id = :team_id AND user_id = :user_id"
            )
            # Execute the UPDATE statement with parameters using the session
            my_database.session.execute(update_statement, {"team_id": team_id, "user_id": member_id, "new_role": new_role})
            my_database.session.commit()
            return True
        except Exception as e:
            print( e )
            return False
        return
    
    
    #delete ( block ) user for team access :
    def remove_contributor(team_id, user_id):
        try:
            sql_statement = text(
                "DELETE FROM user_team_role WHERE team_id = :team_id AND user_id = :user_id"
            )
            my_database.session.execute(sql_statement, {"team_id": team_id, "user_id": user_id}).fetchall()
            my_database.session.commit()
            return True
        except Exception as e:
            print( e )
            return False
    #get all the role belongs to the team :
    def get_team_roles(team_id):
        try:
            roles = []
            sql_statement = text(
                "SELECT role FROM user_team_role WHERE team_id = :team_id"
            )
            roleList  = my_database.session.execute(sql_statement,{"team_id": team_id} )
            roles = [row[0] for row in roleList]
            return roles
        except Exception as e:
            print( e )
            return []
