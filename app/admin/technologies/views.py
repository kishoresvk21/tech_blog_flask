from flask_restplus import Resource
from app.models_package.models import Technologies,User
from app.serializer import technology_serializer
from app import app,db
from flask import jsonify,request
from app.authentication import authentication
from datetime import datetime
class TechFilter(Resource):
    def get(self):
        try:
            t_list = []
            order_by_technology_obj = Technologies.query.order_by(Technologies.updated_at)

            if not order_by_technology_obj:
                app.logger.info("No Technologies in DB")
                return jsonify(status=404, message="No Technologies in DB")

            for itr in order_by_technology_obj:
                dt = technology_serializer(itr)
                t_list.append(dt)

            if not t_list:
                app.logger.info("No Technologies in DB")
                return jsonify(status=404, message="No Technologies in DB")

            app.logger.info("Return Technologies data")
            return jsonify(status=200, data=t_list, message="Returning Technologies data")
        except:
            app.logger.info("No input found")
            return jsonify(status=400, message="No input found")

class AdminTechClass(Resource):
    @authentication
    def post(self):
        data = request.get_json() or {}
        if not data:
            app.logger.info("No input(s)")
            return jsonify(status=400, message="No input(s)")
        user_id = data.get('user_id')
        technologies = data.get('technologies')
        if not (user_id and technologies):
            app.logger.info("User_id and technologies are required")
            return jsonify(status=404, message="User_id and technologies are required")
        check_user = User.query.filter_by(id=user_id).first()
        if not check_user:
            app.logger.info("User not found")
            return jsonify(status=400, message="User not found")
        if not (check_user.roles == 2 or check_user.roles == 3):
            app.logger.info("User not allowed to add technologies")
            return jsonify(status=404, message="User not allowed to add technologies")
        for itr in technologies:
            check_tech_exist = Technologies.query.filter_by(name=itr).first()
            if check_tech_exist:
                app.logger.info(f"{itr} technology already exists")
                return jsonify(status=400, message=f"{itr} technology already exists")
        today = datetime.now()
        date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
        for itr in technologies:
            tech = Technologies(itr, date_time_obj, date_time_obj)
            db.session.add(tech)
            db.session.commit()
        return jsonify(status=200, message="added successfully")

    @authentication
    def delete(self):
        data = request.get_json() or {}
        if not data:
            app.logger.info("No input(s)")
            return jsonify(status=400, message="No input(s)")
        tech_id = data.get('tech_id')
        user_id = data.get('user_id')
        if not (tech_id and user_id):
            app.logger.info("tech_id, user_id required to delete")
            return jsonify(status=404, message="tech id, user_id required to delete")
        tech_check = Technologies.query.filter_by(id=tech_id).first()
        user_check = User.query.filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, message="User not found")
        if tech_check:
            if (user_check.roles == 2 or user_check.roles == 3):
                tech_check.status=0
                db.session.commit()
                app.logger.info("Technology deleted successfully")
                return jsonify(status=200, message="Technology deleted successfully")
            app.logger.info("User not allowed to delete")
            return jsonify(status=404, message="User not allowed to delete")

        app.logger.info("Technology not found")
        return jsonify(status=400, message="Technology not found")

    @authentication
    def put(self):
        data = request.get_json() or {}
        if not data:
            app.logger.info("No input(s)")
            return jsonify(status=400, message="No input(s)")
        user_id = data.get('user_id')
        tech_id = data.get('technology_id')
        technology_name = data.get('edited_technology_name')
        if not (user_id and tech_id and technology_name):
            app.logger.info("User_id, technology_id and technology name are required")
            return jsonify(status=404, message="User_id, technology_id and technology name are required")
        check_user = User.query.filter_by(id=user_id).first()
        check_tech = Technologies.query.filter_by(id=tech_id).first()
        print(check_tech,check_user)

        if not check_user:
            app.logger.info("User not found")
            return jsonify(status=400, message="User not found")
        if not check_tech:
            app.logger.info("tech not found")
            return jsonify(status=400, message="tech not found")


        if not (check_user.roles == 2 or check_user.roles == 3):
            app.logger.info("User not allowed to add technologies")
            return jsonify(status=404, message="User not allowed to add technologies")

        if check_tech and check_tech.status == 0:
            app.logger.info(f"{check_tech.name} technology does not exists")
            return jsonify(status=400, message=f"{check_tech.name} technology does not exists")

        today = datetime.now()
        date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')

        check_tech.name = technology_name
        check_tech.updated_at = date_time_obj
        db.session.commit()
        return jsonify(status=200, message="added successfully")

class TechnologiesCRUD(Resource):
    def get(self):
        pass

    def put(self):
        pass

    def post(self):
        pass

    def delete(self):
        pass

