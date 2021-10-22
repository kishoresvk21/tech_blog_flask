from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_restplus import Api
from flask_cors import CORS
from flask_migrate import Migrate
app = Flask(__name__)
CORS(app)
cors = CORS(app, resources={r"": {"origins": ""}, })
app.config['SECRET_KEY'] = 'rmijlkqqqawtre@1((11'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Root#123@localhost/tech_support_database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)
migrate=Migrate(app,db)
api = Api(app)

#USER MODULE
from app.user.users.views import Login,Register,UpdatePassword,ForgotPassword,Logout,GetProfile,UserProfile
api.add_resource(Login, "/login")
api.add_resource(Register,"/register")
api.add_resource(Logout,"/logout")
api.add_resource(UpdatePassword,"/changepassword") #profile/changepassword
api.add_resource(ForgotPassword,"/forgotpassword")
api.add_resource(GetProfile,"/getprofile/user/<int:user_id>")
api.add_resource(UserProfile,"/editprofile")
from app.user.queries.views import QueriesClass,GetQueryByUserId,GetQueryByTechnology,GetQueryByTitle
api.add_resource(QueriesClass,"/query")
api.add_resource(GetQueryByUserId,"/getqueries/user/<int:user_id>")
api.add_resource(GetQueryByTechnology,"/getqueries/technology/<string:technology>")
api.add_resource(GetQueryByTitle,"/getqueries/title/<string:title>")

from app.user.user_comments.views import GetCommentByQuery,GetCommentsByUserId,CommentCRUD
api.add_resource(CommentCRUD,"/comment")
api.add_resource(GetCommentsByUserId,"/getcomments/user/<int:user_id>")
api.add_resource(GetCommentByQuery,"/getcomments/query")

from app.user.technologies.views import TechFilter
api.add_resource(TechFilter,"/filter")

from app.user.likes_dislikes.views import Likes,DisLikes
api.add_resource(Likes,"/comment/like")
api.add_resource(DisLikes,"/comment/dislike")
#ADMIN APIs
from app.admin.users.views import Login,ForgotPassword,GetAllUsers,GetProfile,GetAllAdminUsers
api.add_resource(Login,"/admin/login")
api.add_resource(ForgotPassword,"/admin/forgotpassword")
api.add_resource(GetAllUsers,"/admin/getallusers")
api.add_resource(GetProfile,"/admin/getuserprofile/<int:user_id>")
api.add_resource(GetAllAdminUsers,"/admin/getalladminusers")

from app.admin.dashboards.views import FilterRecord,TopUsers
api.add_resource(FilterRecord,"/admin/datefilter") #,methods="[PUT]" #/<string:from_date>/<string:to_date>/<string:record_selection>
api.add_resource(TopUsers,"/admin/topusers/<int:users_limit>")

from app.admin.comments.views import CommentClass,GetCommentsByUserId,GetCommentByQuery
api.add_resource(CommentClass,"/admin/comment") #delete edit comments
api.add_resource(GetCommentByQuery,"/admin/comment/query")
api.add_resource(GetCommentsByUserId,"/admin/getcomments/user/<int:user_id>")

from app.admin.queries.views import QueriesClass,GetQueryByUserId,GetQueryByTechnology,GetQueryByTitle,Unanswered
api.add_resource(GetQueryByUserId,"/admin/getqueries/user/<int:user_id>")
api.add_resource(QueriesClass,"/admin/query") #edit delete
api.add_resource(Unanswered,"/admin/query/unanswered") #edit delete

from app.admin.technologies.views import TechnologiesCRUD,TechFilter,AdminTechClass
api.add_resource(TechFilter,"/admin/gettechnologies")
api.add_resource(AdminTechClass,"/admin/technologies")

from app.admin.admin_users.views import AdminUserDetails,EditProfile,RolesClass,ChangePassword,AdminUsersEditDel
api.add_resource(AdminUserDetails, "/admin/adminuserdetails")
api.add_resource(ChangePassword, "/admin/changepassword")
api.add_resource(EditProfile, "/admin/editadminuserdetails")
api.add_resource(RolesClass, "/admin/roles")
api.add_resource(AdminUsersEditDel, "/admin/users")
# api.add_resource(TopTenUsers,"/toptenusers") # methods="[GET]"
# from app.admin.technologies import
# from app.admin.users.views import
# from app.admin.queries.views import
# from app.admin.comments.views import
# from app.admin.likes_dislikes import
# from app.



# api.add_resource(CommentClass,"/comment")
# api.add_resource(TechFilter,"/filter")
# api.add_resource(UserProfile,"/profile")
# api.add_resource(GetProfile,"/getprofile/<int:user_id>")
# api.add_resource(GetCommentByQuery,"/getcomments/query/<int:query_id>")
# 

# api.add_resource(AdminTechClass,"/admin/technologies") #admin/addtechnologies
# api.add_resource(UserStatus,"/userstatuschange") #admin/userroles