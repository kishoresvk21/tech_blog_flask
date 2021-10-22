from flask import  request,jsonify
from app import app,db
from datetime import datetime
from flask_restplus import Resource
from app.authentication import authentication
from app.models_package.models import User, Queries, Comments
from app.pagination import get_paginated_list
from app.serializer import comments_serializer
from app.authentication import get_user_id
class CommentClass(Resource):
    @authentication
    def put(self):
        data = request.get_json() or {}
        if not data:
            app.logger.info("No input(s)")
            return jsonify(status=400, message="No input(s)")
        query_id = data.get('query_id')
        user_id = data.get('user_id')
        comment_id = data.get('comment_id')
        edited_comment = data.get('edited_comment')

        if not (user_id and edited_comment and comment_id):
            app.logger.info("User_id , edited_comment and comment_id are required fields")
            return jsonify(status=400, message="User_id , edited_comment and comment_id are required fields")

        edit_comment_by_id = Comments.query.filter_by(id=comment_id).first()
        check_user = User.query.filter_by(id=user_id).first()
        if not (check_user.roles == 2 or check_user.roles == 3):
            app.logger.info("User not allowed to edit")
            return jsonify(status=404, message="User not allowed to edit")

        if not edit_comment_by_id:
            app.logger.info("Comment not found")
            return jsonify(status=400, message="Comment not found")

        edit_comment_by_id.msg = edited_comment
        db.session.commit()
        app.logger.info("Comment edited")
        return jsonify(status=200, message="Comment edited",
                       data=comments_serializer(edit_comment_by_id,user_id))

    @authentication
    def delete(self):
        data = request.get_json() or {}
        if not data:
            app.logger.info("No input(s)")
            return jsonify(status=400, message="No input(s)")

        user_id = data.get('user_id')
        comment_id = data.get('comment_id')

        if not (user_id and comment_id):
            app.logger.info("user_id and query_id are required")
            return jsonify(status=400, message="user_id and query_id are required")

        user_check = User.query.filter_by(id=user_id).first()
        if not user_check:
            app.logger.info("User not found")
            return jsonify(status=400, message="User not found")

        comment_check = Comments.query.filter_by(id=comment_id).first()
        if not comment_check:
            app.logger.info("Comment not found")
            return jsonify(status=400, message="Comment not found")

        if not (user_check.roles == 2 or user_check.roles == 3):
            app.logger.info("User not allowed to delete")
            return jsonify(status=404, message="User not allowed to delete")

        db.session.delete(comment_check)
        db.session.commit()
        app.logger.info("Comment deleted successfully")
        return jsonify(status=200, message="Comment deleted successfully")
    def get(self):  # send all the comments based on comment_id or u_id or q_id or send all

        order_by_comment_obj = db.session.query(Comments).order_by(Comments.updated_at)
        if not order_by_comment_obj:
            app.logger.info("No Comments in DB")
            return jsonify(status=404, message="No comments in DB")

        c_list = []
        for itr in order_by_comment_obj:
            user_name = User.query.filter_by(id=itr.u_id).first()
            dt = comments_serializer(itr,itr.u_id)
            dt['name'] = user_name.name
            c_list.append(dt)

        app.logger.info("Return comments data")
        return jsonify(status=200, data=get_paginated_list(c_list, '/admin/comment', start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3),with_params=False),
                       message="Returning comments data")


class GetCommentByQuery(Resource):
    @authentication
    def get(self):
        user_id=get_user_id(self)
        query_id=request.args.get('query_id')
        comment_obj = Comments.query.filter_by(q_id=query_id).all()
        if not comment_obj:
            app.logger.info("No Comments found")
            return jsonify(status=404, message="No comments found")
        comment_list = []
        page = f'/admin/comment/query/{query_id}'
        for itr in comment_obj:
            dt = comments_serializer(itr,user_id)
            comment_list.append(dt)
        app.logger.info("Return comments data")
        return jsonify(status=200, data=get_paginated_list(comment_list, page,start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3),with_params=True),message="Returning queries data")


class GetCommentsByUserId(Resource):
    @authentication
    def get(self):  # send all the comments based on user_id
        c_list = []
        requested_user=get_user_id(self)
        user_id=request.args.get("user_id")
        comments_obj = Comments.query.filter_by(u_id=user_id).all()
        print(comments_obj)
        if not comments_obj:
            app.logger.info("No Comments in DB")
            return jsonify(status=404, message="No comments in DB")
        for itr in comments_obj:
            dt = comments_serializer(itr,requested_user)
            c_list.append(dt)
        print(c_list)
        page = '/admin/getcomments/user/' + str(user_id)

        app.logger.info("Return comments data")
        return jsonify(status=200, data=get_paginated_list(c_list, page, start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3),with_params=False),message="Returning comments data")

        # except:
        #     return jsonify(status=400, message="No inputs found")




