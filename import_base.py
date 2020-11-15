import json
from data import *


with open("data/goals.json", "w") as w:
   json.dump(goals, w)


with open("data/teachers.json", "w") as w:
   json.dump(teachers, w)
