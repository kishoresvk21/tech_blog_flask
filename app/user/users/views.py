from flask import request,jsonify
from datetime import datetime
from app.models_package.models import User,Technologies
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restplus import Resource
from app import app, db
from sqlalchemy import or_, and_
import re
from app.authentication import encode_auth_token, authentication
from app.serializer import user_serializer, replace_with_ids
from app.utils.smtp_mail import send_mail_to_reset_password

class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        if not data:
            app.logger.info("No input(s)")
            return jsonify(status=400, message="No input(s)")
        email = data.get("email")
        mobile = data.get("mobile")
        password = data.get('password')
        if not ((email or mobile) and password):
            app.logger.info("email or mobile and password are required")
            return jsonify(status=400, message="email or mobile and password are required")
        user = User.query.filter(or_(User.email == email, User.mobile == mobile)).first()
        if user:
            if user.status == 0:
                app.logger.info("User is disabled temporarily")
                return jsonify(status=400,message="User is disabled temporarily")
            if check_password_hash(user.password, password):
                token = encode_auth_token(user)
                app.logger.info(token)
                response = user_serializer(user)
                app.logger.info(f'{user.name} Logged in successfully')
                return jsonify(status=200, data=response, message="Logged in successfully", token=token.decode('UTF-8'))
            else:
                app.logger.info(f"{user.name} Incorrect password")
                return jsonify(status=404, message="Incorrect password")
        else:
            app.logger.info(f"user not found")
            return jsonify(status=404, message="user not found")


class Logout(Resource):
    def post(self):
        app.logger.info("Logged out successfully")
        return jsonify(status=200, message="Logged out successfully")

    def get(self):
        app.logger.info("Logged out successfully")
        return jsonify(status=200, message="Logged out successfully")


class Register(Resource):
    def post(self):
        data = request.get_json()
        if not data:
            app.logger.info("No input(s)")
            return jsonify(status=400, message="No input(s)")
        name = data.get('name')
        email = data.get('email')
        mobile = data.get('mobile')
        list_of_tech = data.get('technology')
        password = data.get("password")
        # check all data exists or not
        if not (name and email and mobile and list_of_tech and password):
            msg = 'name, email, mobile, technology and password are required fields'
        # check valid email
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address'
        elif not (re.match(r'[0-9]+', mobile) and len(mobile) == 10):
            msg = 'Invalid phone number'
        # check valid name
        elif not re.match(r'[A-Za-z0-9]+', name):
            msg = 'Name must contain only characters and numbers'
        elif not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$', password):
            msg = 'Password should contain min 8 characters, a special character, Uppercase, lowercase and a number'
        # check user already exist
        else:
            try:
                user = User.query.filter(or_(User.email == email,
                                             User.mobile == mobile,
                                             User.name == name)).first()
                if user:
                    msg = 'User already exist'
                else:
                    ids_list = f"{replace_with_ids(list_of_tech)}"
                    # technology = ast.literal_eval(technology)
                    today = datetime.now()
                    date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
                    print(date_time_obj)
                    password = generate_password_hash(password, method='sha256')
                    user = User(name, email, mobile, ids_list, password, date_time_obj, date_time_obj)
                    db.session.add(user)
                    db.session.commit()
                    response = {"name": name, "email": email, "mobile": mobile, "technology": list_of_tech}
                    app.logger.info(f'{user.name} Registered successfully')
                    return jsonify(status=200, data=response, message="Registered successfully")
            except:
                app.logger.info("Database connection not established")
                return jsonify(status=404, message="Database connection not established")
        app.logger.info(msg)
        return jsonify(status=400, message=msg)


class UpdatePassword(Resource):
    @authentication
    def put(self):
        data = request.get_json()
        if not data:
            app.logger.info("No input(s)")
            return jsonify(status=400, message="No input(s)")
        email = data.get("email")
        mobile = data.get("mobile")
        old_password = data.get("old_password")
        new_password = data.get("new_password")
        confirm_new_password = data.get("confirm_new_password")

        if not ((email or mobile) and (old_password and new_password and confirm_new_password)):
            app.logger.info(f'email (or) mobile , old_password, new_password and confirm_new_password required')
            return jsonify(status=400,
                           message="email (or) mobile , old_password, new_password and confirm_new_password required")
        try:
            user = User.query.filter(or_(User.email == email, User.mobile == data.get("mobile"))).first()
            if user:

                if check_password_hash(user.password, data.get('old_password')):
                    if new_password == confirm_new_password:
                        if new_password == old_password:
                            app.logger.info("New password and old password should not be same")
                            return jsonify(status=400, message="New password and old password should not be same")
                        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$',
                                        new_password):
                            app.logger.info(
                                "Password should contain min 8 characters, a special character, Uppercase, lowercase and a number")
                            return jsonify(status=400,
                                           message='Password should contain min 8 characters, a special character, Uppercase, lowercase and a number')
                        user.password = generate_password_hash(new_password, method='sha256')
                        db.session.commit()
                        app.logger.info(f'{user.name} Password updated successfully')
                        return jsonify(status=200, message="Password updated successfully")
                    else:
                        app.logger.info(f'{user.name} New password and confirm new password doesnt match')
                        return jsonify(status=200, message="New password and confirm new password doesn't match")
                else:
                    app.logger.info(f"{user.name} Incorrect old password")
                    return jsonify(status=404, message="Incorrect old password")
            else:
                app.logger.info("User not found")
                return jsonify(status=404, message="User not found")
        except:
            app.logger.info("Unknown database")
            return jsonify(status=404, message="Unknown database")


class ForgotPassword(Resource):
    def post(self):
        data = request.get_json()
        email = data.get("email")

        if not email:
            app.logger.info("email field is required")
            return jsonify(status=400,message="email field is required")

        else:
            try:
                user = User.query.filter(User.email == email).first()
                if user:
                    new_password = send_mail_to_reset_password(user.email, user.name)
                    if new_password == 'Error':
                        app.logger.info("mail sending failed")
                        return jsonify(status=400,message="mail sending failed")
                    app.logger.info("Email sent successfully")
                    today = datetime.now()
                    date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
                    user.updated_at = date_time_obj
                    user.password = generate_password_hash(new_password, method='sha256')
                    db.session.commit()
                    app.logger.info(f'temporary password sent to {user.email}')
                    return jsonify(status=200, message=f'temporary password sent to {user.email}')
                app.logger.info("User not found")
                return jsonify(status=400, message="User not found")
            except:
                app.logger.info("database error")
                return jsonify(status=400, message="database error")


class UserProfile(Resource):
    @authentication
    def put(self):
        data = request.get_json() or {}
        try:
            user_id = data.get('user_id')
            user_update = User.query.filter_by(id=user_id).first()
        except:
            app.logger.info("User not found")
            return jsonify(status=404, message="user not found")
        name = data.get('name')
        technology = data.get('technology')
        if not (name and technology and user_id):
            app.logger.info("name,technology and user_id are required")
            return jsonify(status=400, message="name,technology and user_id are required")
        elif not re.match(r'[A-Za-z0-9]+', name):
            msg = 'name must contain only characters and numbers'
            app.logger.info(msg)
            return jsonify(status=404, message=msg)
        else:
            if user_update:
                if not user_update.name == name:
                    user_update.name = name
                tech_list = []
                for itr in technology:
                    tech_check = Technologies.query.filter_by(name=itr).first()
                    if tech_check:
                        tech_list.append(tech_check.id)
                user_update.technology = f"{tech_list}"
                today = datetime.now()
                user_update.date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
                db.session.commit()
                response = {"name": user_update.name, "technology": technology}
                app.logger.info(f'{user_update.name} Updated successfully')
                return jsonify(status=200, data=response, message="updated Successfully")


class GetProfile(Resource):
    def get(self, user_id):
        user_data = User.query.filter_by(id=user_id).first()
        if not user_data:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")
        return jsonify(status=200, data=user_serializer(user_data), message="user data")

# class GetCommentBycommentId(Resource):
#     def get(self,comment_id): #send all the comments based on user_id
#         try:
#             c_list = []
#             comments_obj = db.session.query(Comments).filter_by(id=comment_id).first()

#             if not comments_obj:
#                 app.logger.info("No Comments in DB")
#                 return jsonify(status=404, message="No comments in DB")

#             for itr in comments_obj:
#                 if itr.u_id == user_id:
#                     dt = comments_serializer(itr)
#                     c_list.append(dt)

#             if not c_list:
#                 app.logger.info("No comments in DB")
#                 return jsonify(status=404, message="No comments found")
#             user_id_str=str(user_id)
#             page = '/getcomments/user/'+user_id_str

#             app.logger.info("Return comments data")
#             return jsonify(status=200, data=get_paginated_list(c_list, page, start=request.args.get('start', 1),
#                                           limit=request.args.get('limit', 3)), message="Returning queries data")

#         except:
#             return jsonify(status=400, message="No inputs found")


# def get(self):
#     data=request.get_json() or {}
#     user_id=data.get('user_id')
#     user_data=db.session.query(User).filter_by(id=user_id).first()
#     if not user_data:
#         app.logger.info("user not found")
#         return jsonify(status=400, message="user not found")
#     return jsonify(status=200,data=user_serializer(user_data),message="user data")
