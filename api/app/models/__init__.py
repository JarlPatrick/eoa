from app.models.age_group import AgeGroup
from app.models.contest import Contest
from app.models.contestant import Contestant
from app.models.contestant_field import ContestantField
from app.models.mentor import t_mentor
from app.models.person import Person
from app.models.person_alias import PersonAlias
from app.models.school import School
from app.models.school_alias import SchoolAlias
from app.models.subcontest import Subcontest
from app.models.subcontest_column import SubcontestColumn
from app.models.subject import Subject
from app.models.type import Type
from app.models.year import Year

__all__ = [
    "AgeGroup",
    "Contest",
    "Contestant",
    "ContestantField",
    "Person",
    "PersonAlias",
    "School",
    "SchoolAlias",
    "Subcontest",
    "SubcontestColumn",
    "Subject",
    "Type",
    "Year",
    "t_mentor",
]
