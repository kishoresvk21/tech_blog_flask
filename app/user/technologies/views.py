from flask_restplus import Resource
from app.models_package.models import Technologies
from app.serializer import technology_serializer
from flask import jsonify
from app import app
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

