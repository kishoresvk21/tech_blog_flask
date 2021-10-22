from flask_restplus import Resource
from flask import request
from app.models_package.models import Comments
from flask import jsonify
from app import app,db
from app.models_package.models import User,LikesDislikes
from datetime import datetime
from sqlalchemy import and_
from app.utils.update_like_dislike_count import update_like_dislike_count
from app.serializer import like_dislike_serializer
from app.authentication import authentication
from app.authentication import get_user_id
class Likes(Resource):
    @authentication
    def post(self):
        data=request.get_json() or {}
        user_id=get_user_id(self)
        comment_id=data.get('comment_id')
        if not comment_id:
             app.logger.info("comment_id is required")
             return jsonify(status=400,message="comment_id is required")
        user_obj=User.query.filter_by(id=user_id).first()
        comment_obj=Comments.query.filter_by(id=comment_id).first()
        if not user_obj:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")
        if not comment_obj:
            app.logger.info("comment not found")
            return jsonify(status=400, message="comment not found")
        likes_dislikes_obj=LikesDislikes.query.filter(and_(LikesDislikes.u_id==user_id,
                                                           LikesDislikes.c_id==comment_id)).first()
        if  likes_dislikes_obj:
            if likes_dislikes_obj.dislike_status: #already disliked then wanted to like then turned to like
                likes_dislikes_obj.like_status = True
                likes_dislikes_obj.dislike_status = False
                db.session.commit()
                update_like_dislike_count(self)
                app.logger.info("liked")
                return jsonify(status=200,data=like_dislike_serializer(likes_dislikes_obj),message="liked")
            elif likes_dislikes_obj.like_status:
                likes_dislikes_obj.like_status = False
                likes_dislikes_obj.dislike_status = False
                db.session.commit()
                update_like_dislike_count(self)
                app.logger.info("like removed")
                return jsonify(status=200, data=like_dislike_serializer(likes_dislikes_obj), message="like removed")
            else:
                likes_dislikes_obj.like_status = True
                likes_dislikes_obj.dislike_status=False
                db.session.commit()
                update_like_dislike_count(self)
                app.logger.info("liked")
                return jsonify(status=200,data=like_dislike_serializer(likes_dislikes_obj),message="liked")

        today = datetime.now()
        date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
        like = True
        dislike = False
        like_dislike_record = LikesDislikes(user_id, comment_id, like, dislike, date_time_obj, date_time_obj)
        db.session.add(like_dislike_record)
        db.session.commit()
        update_like_dislike_count(self)
        app.logger.info("Liked")
        return jsonify(status=200, data=like_dislike_serializer(like_dislike_record), message="Liked")


class DisLikes(Resource):
    @authentication
    def post(self):
        data=request.get_json() or {}
        user_id=get_user_id(self)
        comment_id=data.get('comment_id')
        if not (comment_id):
             app.logger.info("comment_id is required")
             return jsonify(status=400,message="comment_id is required")
        user_obj=User.query.filter_by(id=user_id).first()
        comment_obj=Comments.query.filter_by(id=comment_id).first()
        if not user_obj:
            app.logger.info("user not found")
            return jsonify(status=400, message="user not found")
        if not comment_obj:
            app.logger.info("comment not found")
            return jsonify(status=400, message="comment not found")
        likes_dislikes_obj=LikesDislikes.query.filter(and_(LikesDislikes.u_id==user_id,
                                                           LikesDislikes.c_id==comment_id)).first()
        if  likes_dislikes_obj:
            if likes_dislikes_obj.like_status: #already disliked then wanted to like then turned to like
                likes_dislikes_obj.like_status = False
                likes_dislikes_obj.dislike_status = True
                db.session.commit()
                update_like_dislike_count(self)
                app.logger.info("disliked")
                return jsonify(status=200,data=like_dislike_serializer(likes_dislikes_obj),message="disliked")
            elif likes_dislikes_obj.dislike_status:
                likes_dislikes_obj.like_status = False
                likes_dislikes_obj.dislike_status = False
                db.session.commit()
                update_like_dislike_count(self)
                app.logger.info("dislike removed")
                return jsonify(status=200, data=like_dislike_serializer(likes_dislikes_obj), message="dislike removed")
            else:
                likes_dislikes_obj.like_status = False
                likes_dislikes_obj.dislike_status=True
                db.session.commit()
                update_like_dislike_count(self)
                app.logger.info("disliked")
                return jsonify(status=200,data=like_dislike_serializer(likes_dislikes_obj),message="disliked")

        today = datetime.now()
        date_time_obj = today.strftime('%Y/%m/%d %H:%M:%S')
        like = False
        dislike = True
        like_dislike_record = LikesDislikes(user_id, comment_id, like, dislike, date_time_obj, date_time_obj)
        db.session.add(like_dislike_record)
        db.session.commit()
        update_like_dislike_count(self)
        app.logger.info("disliked")
        return jsonify(status=200, data=like_dislike_serializer(like_dislike_record), message="disliked")
