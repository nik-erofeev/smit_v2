from app.dao.base import BaseDAO
from app.models import Role, User


class UsersDAO(BaseDAO):
    model = User


class RoleDAO(BaseDAO):
    model = Role
