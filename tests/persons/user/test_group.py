from somaafrica.persons.models import Group
from somaafrica.persons.serializers import GroupSerializer

from .crud import CRUD

class GroupTests(CRUD):
    model = Group
    base_url_name = 'group'
