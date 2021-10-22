from flask import request,jsonify
from app import app,db
from flask_restplus import Resource
from sqlalchemy import and_
from app.models_package.models import User, Queries, Comments
from app.serializer import user_serializer
from app.pagination import get_paginated_list
from app.utils.update_like_dislike_count import update_like_dislike_count
import re
from datetime import timedelta,datetime
from dateutil import relativedelta
import monthdelta
class FilterRecord(Resource):
    def get(self):  # from_date,to_date,record_selection
        from_date = request.args.get("from_date")
        from_date= datetime.strptime(from_date, '%Y-%m-%d')
        # to_date = request.args.get("to_date")
        to_date = (from_date+monthdelta.monthdelta(months=1))-timedelta(days=1)
        print(from_date,to_date)
        get_records_from_to = Comments.query.filter(and_(Comments.updated_at >= from_date,
                                                         Comments.updated_at <= to_date)).count()
        print(get_records_from_to)
        return

        if not (from_date and to_date and filter_choice):
            app.logger.info("from_date, to_date or filter_choice parameters missing")
            return jsonify(status=400, message="from_date, to_date or filter_choice parameters missing")

        if not (re.match(r'^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$', from_date) and
                re.match(r'^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$', to_date)):
            app.logger.info("incorrect format of from_date to_date")
            return jsonify(status=400, message="incorrect format of from_date to_date")

        if filter_choice not in ("users", "queries", "comments"):
            app.logger.info("incorrect filter_choice")
            return jsonify(status=400, message="incorrect filter_choice")

        month_wise_count = []
        from_date_split = from_date.split('-')
        to_date_split = to_date.split('-')

        from_month = int(from_date_split[1])
        to_month = int(to_date_split[1])

        for month_itr in range(from_month, to_month):
            itr_from_date = f'{from_date_split[0]}-{month_itr}-01'
            itr_to_date = f'{from_date_split[0]}-{month_itr + 1}-01'
            if filter_choice == "users":
                get_records_from_to = User.query.filter(and_(User.updated_at >= itr_from_date,
                                                             User.updated_at < itr_to_date)).count()
            elif filter_choice == "queries":
                get_records_from_to = Queries.query.filter(and_(Queries.updated_at >= itr_from_date,
                                                                Queries.updated_at < itr_to_date)).count()
            elif filter_choice == "comments":
                get_records_from_to = Comments.query.filter(and_(Comments.updated_at >= itr_from_date,
                                                                 Comments.updated_at < itr_to_date)).count()
            else:
                app.logger.info("record selection should be users, queries, comments")
                return jsonify(status=400, message="record selection should be users, queries, comments")

            dt = dict(from_date=itr_from_date, to_date=itr_to_date, count=get_records_from_to)
            month_wise_count.append(dt)
        app.logger.info(f"month wise count from {from_date} to {to_date}")
        page = '/admin/datefilter?from_date=' + f'{from_date}' + \
               "&to_date=" + f'{to_date}' + "&filter_choice=" + f'{filter_choice}'
        return jsonify(status=200, data=get_paginated_list(month_wise_count, page, start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3),with_params=False), message=f"month wise count from {from_date} to {to_date}")


# class FilterRecord(Resource):
#     def get(self): #,from_date,to_date,record_selection
#         from_date=request.args.get("from_date")
#         to_date = request.args.get("to_date")
#         filter_choice=request.args.get("filter_choice")
#         month_wise_count=[]
#         from_date_split=from_date.split('-')
#         to_date_split=to_date.split('-')
#         from_month = int(from_date_split[1])
#         to_month=int(to_date_split[1])
#         for month_itr in range(from_month, to_month):
#             itr_from_date=f'{from_date_split[0]}-{month_itr}-01'
#             itr_to_date=f'{from_date_split[0]}-{month_itr+1}-01'
#             if filter_choice == "users":
#                 get_records_from_to = User.query.filter(and_(User.updated_at >= itr_from_date,
#                                                              User.updated_at < itr_to_date)).count()
#             elif filter_choice == "queries":
#                 get_records_from_to = Queries.query.filter(and_(Queries.updated_at >= itr_from_date,
#                                                                 Queries.updated_at < itr_to_date)).count()
#             elif filter_choice == "comments":
#                 get_records_from_to = Comments.query.filter(and_(Comments.updated_at >= itr_from_date,
#                                                                  Comments.updated_at < itr_to_date)).count()
#             else:
#                 app.logger.info("record selection should be users, queries, comments")
#                 return jsonify(status=400, message="record selection should be users, queries, comments")
#
#             dt= dict(from_date=itr_from_date, to_date=itr_to_date, count=get_records_from_to)
#             month_wise_count.append(dt)
#         app.logger.info(f"month wise count from {from_date} to {to_date}")
#         page = "/admin/datefilter"
#
#         return jsonify(status=200, data=month_wise_count,message=f"month wise count from {from_date} to {to_date}")

#fromdate=request.args.get('from_date',from_date),todate=request.args.get('to_date',to_date),filterchoice=request.args.get('filter_choice',filter_choice),
class TopUsers(Resource):
    def get(self, users_limit):
        update_like_dislike_count(self)
        top_list = []
        top_users_list = []
        count = 0

        comment_obj_list = Comments.query.filter(Comments.like_count >= Comments.dislike_count). \
            order_by(Comments.like_count.desc()).all()
        if not comment_obj_list:
            app.logger.info("No comments in db")
            return jsonify(status=400, message="No comments in db")

        for itr in comment_obj_list:
            if itr.like_count and count < users_limit:
                print("cmt_id=", itr.id, "Like count = ", itr.like_count, "dislike count =", itr.dislike_count)
                user_obj = User.query.filter_by(id=itr.u_id).first()
                if not user_obj:
                    app.logger.info("No user in db")
                    return jsonify(status=400, message="No user in db")
                top_users_list.append(user_obj)
                count = count + 1

        if not top_users_list:
            app.logger.info("No top users")
            return jsonify(status=400, message="No top users")

        for itr in top_users_list:
            print(itr)
            dt = user_serializer(itr)
            top_list.append(dt)
        app.logger.info(f"Return top {users_limit} user data")

        page = "/admin/topusers/" + f'{users_limit}'

        return jsonify(status=200, data=get_paginated_list(top_list, page, start=request.args.get('start', 1),
                                                           limit=request.args.get('limit', 3),with_params=False),
                       message=f"Returning top {users_limit} users data")



