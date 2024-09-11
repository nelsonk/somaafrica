from somaafrica.persons.models import Group

from .crud import CRUD


class GroupTests(CRUD):
    model = Group
    base_url_name = 'group'
