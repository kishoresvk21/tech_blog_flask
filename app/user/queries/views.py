from flask_restplus import Resource
from app.authentication import authentication
from flask import request,jsonify
from app import app,db
from sqlalchemy import or_, and_
from app.models_package.models import User,Technologies,Queries,Comments
from datetime import datetime
from app.pagination import get_paginated_list
from app.serializer import query_serializer
from app.authentication import decode_auth_token
class QueriesClass(Resource):
    @authentication
    def post(self):
        data = request.get_json()
        if not data:
            app.logger.info("No input(s)")
            return jsonify(status=400, message="No input(s)")
        title = data.get('title')
        user_id = data.get('user_id')
        description = data.get('description')
        tech = data.get('technology')
        if not (title and description and tech and user_id):
            app.logger.info("title, description, user_id and technology are required")
            return jsonify(status=200, message="title, description, user_id and technology are required")

        user_check = User.query.filter_by(id=user_id).first()
        tech_check = Technologies.query.filter_by(name=tech).first()
        if not (tech_check and user_check):
            app.logger.info("user or technology not found")
            return jsonify(status=400, message="user or technology not found")
        query_insertion = Queries.query.filter(or_(Queries.title == title,
                                                   Queries.description == description)).first()
        if query_insertion:
            if query_insertion.title == title:
                app.logger.info("Data already exist")
                return jsonify(status=200, message="Data already exist")

        today = datetime.now()
        date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
        try:
            question = Queries(user_id, title, description, tech_check.id, date_time_obj, date_time_obj)
            db.session.add(question)
            db.session.commit()
        except:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")
        app.logger.info("Query inserted successfully")
        response = query_serializer(question)
        return jsonify(status=200, data=response, message="Query inserted successfully")

    @authentication
    def put(self):
        data = request.get_json()
        if not data:
            app.logger.info("No input(s)")
            return jsonify(status=400, message="No input(s)")
        query_id = data.get('query_id')
        user_id = data.get('user_id')
        tech = data.get('technology')
        title = data.get('title')
        description = data.get('description')
        user_check = User.query.filter_by(id=user_id).first()
        tech_check = Technologies.query.filter_by(name=tech).first()
        query_check = Queries.query.filter_by(id=query_id).first()

        if not (user_check and tech_check and query_check):
            app.logger.info("User or technology or query not found")
            return jsonify(status=400, message="User or technology or query not found")
        if query_check:
            if query_check.u_id == user_id:
                query_check.title = title
                query_check.description = description
                query_check.t_id = tech_check.id
                today = datetime.now()
                date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
                query_check.updated_at = date_time_obj
                db.session.commit()
                response = {"query_id": query_check.id, "title": query_check.title,
                            "description": query_check.description, "technology": tech}
                app.logger.info("Query changed successfully")
                return jsonify(status=200, data=response, message="Query changed successfully")
            app.logger.info("User not allowed to edit")
            return jsonify(status=404, message="User not allowed to edit")
        app.logger.info("Query didn't found")
        return jsonify(status=404, message="Query didn't found")

    @authentication
    def delete(self):
        data = request.get_json() or {}
        if not data:
            app.logger.info("No input(s)")
            return jsonify(status=400, message="No input(s)")
        try:
            query_id = data.get('query_id')
            user_id = data.get('user_id')
            query_check = Queries.query.filter_by(id=query_id).first()
            user_check = User.query.filter_by(id=user_id).first()
        except:
            app.logger.info("user_id/query_id not found")
            return jsonify(status=400, message="user_id/query_id not found")

        if not (query_id and user_id):
            app.logger.info("Query id, user_id required to delete")
            return jsonify(status=404, message="Query id, user_id required to delete")
        if query_check:
            if ((query_check.u_id == user_id) or (user_check.roles == 2) or (user_check.roles == 3)):
                delete_comment = Comments.query.filter_by(q_id=query_id).all()
                if delete_comment:
                    for itr in delete_comment:
                        db.session.delete(itr)
                        db.session.commit()
                else:
                    app.logger.info("No comments for this query, deleting this query ")
                db.session.delete(query_check)
                db.session.commit()
                app.logger.info("Query deleted successfully")
                return jsonify(status=200, message="Query deleted successfully")
            app.logger.info("User not allowed to delete")
            return jsonify(status=404, message="User not allowed to delete")

        app.logger.info("Query not found")
        return jsonify(status=400, message="Query not found")

    def get(self):

        order_by_query_obj = db.session.query(Queries).order_by(Queries.updated_at)
        if not order_by_query_obj:
            app.logger.info("No Queries in DB")
            return jsonify(status=404, message="No Queries in DB")

        c_list = []
        for itr in order_by_query_obj:
            dt = query_serializer(itr)
            c_list.append(dt)

        app.logger.info("Return queries data")
        return jsonify(status=200, data=get_paginated_list(c_list, '/query', start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3),with_params=False),
                       message="Returning queries data")

class GetQueryByUserId(Resource):
    def get(self, user_id):
        queries_obj = db.session.query(Queries).filter_by(u_id=user_id).all()
        if not queries_obj:
            app.logger.info("No queries found")
            return jsonify(status=404, message="No queries found")
        queries_list = []
        for itr in queries_obj:
            dt = query_serializer(itr)
            queries_list.append(dt)
        user_id_str = str(user_id)
        page = '/getqueries/user/' + user_id_str
        app.logger.info("Returning queries data")
        return jsonify(status=200, data=get_paginated_list(queries_list, page, start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3),with_params=False),
                       message="Returning queries data")


class GetQueryByTitle(Resource):
    def get(self, title):
        queries_obj = Queries.query.filter(Queries.title.ilike(f'%{title}%')).all()
        # queries_obj = Queries.query.filter_by(title=Queries.title.like(f'{title}%')).all()
        print(queries_obj)
        if not queries_obj:
            app.logger.info("No queries found")
            return jsonify(status=404, message="No queries found")
        queries_list = []
        for itr in queries_obj:
            dt = query_serializer(itr)
            queries_list.append(dt)
        page = '/getqueries/title/' + title
        app.logger.info("Returning query data")
        return jsonify(status=200,
            data=get_paginated_list(queries_list, page, start=request.args.get('start', 1),
            limit=request.args.get('limit', 3),with_params=False), message="Returning queries data")


class GetQueryByTechnology(Resource):
    def get(self, technology):
        tech_obj = Technologies.query.filter_by(name=technology).first()
        if not tech_obj:
            app.logger.info("technology not found")
            return jsonify(status=404, message="technology not found")
        queries_obj = Queries.query.filter_by(t_id=tech_obj.id).all()
        if not queries_obj:
            app.logger.info("No queries found")
            return jsonify(status=404, message="No queries found")
        queries_list = []
        for itr in queries_obj:
            dt = query_serializer(itr)
            queries_list.append(dt)
        page = '/getqueries/technology/' + technology
        app.logger.info("Returning queries data")
        return jsonify(status=200, data=get_paginated_list(queries_list, page, start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3),with_params=False),
                       message="Returning queries data")
