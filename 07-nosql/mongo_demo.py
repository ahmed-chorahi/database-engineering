"""Tiny pymongo demo. Needs: docker run -p 27017:27017 -d mongo:7"""
from pymongo import MongoClient

db = MongoClient("mongodb://localhost:27017")["school_demo"]
db.students.drop()

db.students.insert_many([
    {"name": "Ayesha", "age": 21, "city": "Islamabad", "skills": ["sql", "python"]},
    {"name": "Bilal",  "age": 22, "city": "Lahore",    "skills": ["java"]},
    {"name": "Sara",   "age": 20, "city": "Islamabad", "skills": ["python", "ml"]},
])

print("python people:", [s["name"] for s in db.students.find({"skills": "python"})])

pipeline = [
    {"$group": {"_id": "$city", "avg_age": {"$avg": "$age"}, "n": {"$sum": 1}}},
    {"$sort": {"n": -1}},
]
for row in db.students.aggregate(pipeline):
    print(row)
