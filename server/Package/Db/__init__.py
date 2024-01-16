from flask_sqlalchemy import SQLAlchemy
import uuid 
from sqlalchemy.dialects.postgresql import UUID




my_database = SQLAlchemy()



def setup_user_team_role():
# Define a many-to-many association table for User and Team with roles
    user_team_role = my_database.Table(
        'user_team_role',
        my_database.Column('user_id', 
            UUID(as_uuid=True), 
            my_database.ForeignKey('user.id'), 
            primary_key=True),
        my_database.Column('team_id', 
             UUID(as_uuid=True), 
            my_database.ForeignKey('team.id'), 
            primary_key=True),
        my_database.Column('role', 
            my_database.String(20), 
            nullable=False
        )  # You can define roles as needed
    )
    return

def setup_team_project():
    #team_project
    team_project = my_database.Table(
        "team_project",
        my_database.Column('team_id', 
            UUID(as_uuid=True), 
            my_database.ForeignKey('team.id'), 
            primary_key=True),
        my_database.Column('project_id', 
            UUID(as_uuid=True), 
            my_database.ForeignKey('project.id'), 
            primary_key=True
        )
    )
    return