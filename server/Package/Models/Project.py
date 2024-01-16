from Package.Db import my_database
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text


class Project(my_database.Model):
    id = my_database.Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    name = my_database.Column(my_database.String(80), unique=True, nullable=False)
    manager = my_database.Column(UUID(as_uuid=True), my_database.ForeignKey('user.id'))
    description = my_database.Column(my_database.String(1000))
    repo_url = my_database.Column(my_database.String(255), nullable=False)
    state = my_database.Column(my_database.String(50))
    teams = my_database.relationship("Team", 
                                    secondary="team_project",
                                    back_populates="projects"
                                )
    def __init__(self,name="",manager="",repo_url=""):
        self.name = name
        self.manager = manager
        self.repo_url = repo_url
        self.description = "Default description you can update it later"
        self.state = "CREATED"
    #overwrite the constructor :
    def __init__(self, name="", manager="", repo_url="", description="", state=""):
        self.name = name
        self.manager = manager
        self.repo_url = repo_url
        self.description = description
        self.state = state
    #make seters needed for updating states : 
    def setDescription(self, description=""):
        self.description = description
        return
    #set state :
    def setState(self, state=""):
        self.state = state
        return
    #get all teams workin on the current project:
    def getTeamList(self):
        sql_statement = text(
            "SELECT team_id FROM team_project WHERE project_id= :project_id"
        )
        queryValues  = my_database.session.execute(sql_statement,{"project_id":self.id}).fetchall()
        id_list = [ item[0]  for item in queryValues ] 
        return id_list
    def toDict(self):
        return dict(
            id=self.id,
            name=self.name,
            manager=self.manager,
            description=self.description,
            state=self.state,
            url=self.repo_url
        )