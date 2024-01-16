
from Package.Db import my_database
import uuid 
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text

class Team(my_database.Model):
    id = my_database.Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    name = my_database.Column(my_database.String(80), unique=True, nullable=False)
    admin = my_database.Column(UUID(as_uuid=True),nullable=False)
    projects = my_database.relationship('Project', 
                                        secondary="team_project",
                                        back_populates='teams')
    users = my_database.relationship('User', 
                                    secondary='user_team_role', 
                                    back_populates='teams'
                                    )
    def __init__(self,name="", admin=""):
        self.name = name
        self.admin = admin
    #add class method to fetch for all users :
    def get_contributors(self):
        # Use SQLAlchemy's text function to define the SQL statement
        sql_statement = text(
            "SELECT user_id, role FROM user_team_role WHERE team_id = :team_id"
        )
        # Execute the statement with parameters using the session
        user_list = my_database.session.execute(sql_statement, {"team_id": self.id}).fetchall()
        # Convert the result to a list of dictionaries
        id_list = [ {"id":item[0], "role":item[1]} for item in user_list]
        return id_list
    def toDict(self):
        return dict(
            id=self.id,
            admin=self.admin,
            name=self.name
        )