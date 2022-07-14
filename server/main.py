from flask import Flask,request,jsonify
from Package import *
from flask_cors import CORS, cross_origin



my_app = Flask(__name__)
cors = CORS(my_app)
my_app.config['CORS_HEADERS'] = 'Content-Type'


@my_app.route("/get-auth",methods=["POST"])
@cross_origin()
def authentification():
    if request.method == "POST":
        data = request.form.to_dict()
        print("server authentification is loaded !! ")
        user_name = data['name']
        user_email = data['email']
        user_pswd = data['pswd']
        connexion_state = 0
        response = get_connexion_details(user_name,user_email,user_pswd)
        print(response)
        if response == "welcom back again  "+str(user_name):
            connexion_state = 1
        return jsonify({"message":response,"statelogin":connexion_state})

@my_app.route("/get-registration",methods=["POST"])
@cross_origin()
def registration():
    if request.method == "POST":
        registration_data = request.form.to_dict()
        registration_state = 0
        response = check_account_registration(registration_data['FerstName'],
                                              registration_data['LastName'],
                                              registration_data['Email'],
                                              registration_data['Password'])
        if response == 1: 
            return jsonify({"message": "account already exists ",'RegistrationState':registration_state })
        else:
             # creation new user document :
            registration_state = 1 
            response_insert_user = create_user_document(registration_data['FerstName'],
                                              registration_data['LastName'],
                                              registration_data['Email'],
                                              registration_data['Password'])
            return jsonify({"message": response_insert_user,'RegistrationState':registration_state})


@my_app.route("/add/<subject>",methods=["POST"])
@cross_origin()
def add_data(subject):
    list_subject_dispo = ['Project','Team']
    message_response = ""
    state = ""
    if request.method=='POST':
        if subject in list_subject_dispo:
            if subject == 'Project':
                response_project_creator = create_project(request.form.to_dict())
                if response_project_creator < 0:
                    message_response = "We cannot create a project at this time, please try again."
                    state = "error"
                else:
                    message_response = "Project created successfully"
                    state = "success"
    return jsonify({"message": message_response,'CreateState':state})

@my_app.route("/add/Team/Project",methods=["POST"])
@cross_origin()
def add_project_to_team():
    if request.method == "POST":
        message_response = ""
        data = request.form.to_dict()
        print(data)
        team_name = data['Team']
        project_name = data['Project']
        project_state = data['State']
        response_insert = add_project_team(team_name,project_name,project_state)
        if response_insert < 0:
            message_response =  "We can not add selected project to the team target "
        else:
            message_response = " add project to team project list done :) ......"
        return jsonify({"message": message_response})

@my_app.route("/invitation",methods=["POST", "GET"])
@cross_origin()
def manage_invit():
    if request.method == "POST":
        response_message = ""
        state = ""
        current_invitation = request.form.to_dict()
        response_add_invit = create_invitation(current_invitation)
        if response_add_invit < 0:
            response_message = "There is an error in sending an invitation, please try later."
            state = "error"
        else:
            response_message = "Invitation sent successfully"
            state = "success"
    return jsonify({"message":response_message, "state":state})



@my_app.route("/get-all-project/<subject>/<key>",methods=["GET"])
@cross_origin()
def fetch_data_endpoint(subject,key):
    subject_list_enable = ['Id','User','Team']
    message_response = ""
    if subject in subject_list_enable:
        # get connexion wit the dba :
        if subject == 'Id':
            project_list = get_project_Id(key)
            print(project_list)
        if subject == 'User':
            project_list = get_project_user(key)
            print(project_list)
        if subject == 'Team':
            project_list = get_project_team(key)
            print(project_list)
        message_response = "fetch data from dba : get "+str(subject)+" with key :  "+str(key)
    else:
        message_response = "fetch data from dba : get subject not enable yet "
    return jsonify({"message": message_response,"reponse_data":project_list})






if __name__=="__main__":
    my_app.secret_key = 'super secret key'
    my_app.config['SESSION_TYPE'] = 'filesystem'
    my_app.run(debug=True)