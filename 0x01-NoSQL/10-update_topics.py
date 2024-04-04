#!/usr/bin/env python3
""" Update topics of a school document based on the name """
import pymongo


def update_topics(mongo_collection, name, topics):
    """ Update topics of a school document based on the name """
    if not mongo_collection:
        return None
    return mongo_collection.update_many({"name": name}, {"$set": {"topics": topics}})
