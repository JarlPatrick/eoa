
"""
The main utility file for importing a contest (possibly just a single
subcontest). `addContest` should be about the only function used from this
module, as it is the only one that tries to manage the connection state and
errors properly.

Currently, no checks are performed for similar names (even ones with just
differing case), so duplicates might occur. Care should be taken especially
with contest and subcontest identifiers (year, subject, type, age group, name).
"""

import os
import json
import mysql.connector
import logging

logging.basicConfig(level=logging.DEBUG)

# Credentials
with open(os.path.join(os.path.dirname(__file__),"../credentials.json")) as f:
    config = json.loads(f.read())
mysql_user = config["user"]
mysql_passwd = config["password"]
mysql_db = config["database"]
mysql_host = config["host"]

conn = mysql.connector.connect(user=mysql_user, password=mysql_passwd, database=mysql_db, host=mysql_host)
cur = conn.cursor()

logging.info('Running!')

def info(msg):
    logging.info(msg)

def debug(msg):
    logging.debug(msg)

def execute(query, params):
    debug('Query: "' + query + '" ' + str(params))
    cur.execute(query, params)

"""
Create new record in the specified table

NOTE: use getMakeRow, as otherwise duplicates might be created
"""
def createRow(table, **params):
    paramsList = [(k, v) for k, v in params.items()]
    execute(f"INSERT INTO {table} (" + ', '.join((p[0] for p in paramsList)) + ") VALUES (" + ', '.join(['%s'] * len(paramsList)) + ")", tuple(p[1] for p in paramsList))
    return cur.lastrowid

# cache to prevent re-doing SELECTs on the same age_groups and schools all the time
row_cache = {}

"""
Get the id of a row in a table based on parameters
Insert that row if it does not exist
"""
def getMakeRow(table, getId = True, **params):
    # Get params as ordered list
    paramsList = [(k, v) for k, v in params.items()]
    if (table, *paramsList) in row_cache:
        debug("using cached row for " + str((table, *paramsList)))
        return row_cache[(table, *paramsList)]

    # Convert to statement and execute
    execute("SELECT " + ("id" if getId else "NULL") + f" FROM {table} WHERE " + ' and '.join(p[0] + (' is %s' if p[1] is None else ' = %s') for p in paramsList) + ' LIMIT 1', tuple(p[1] for p in paramsList))

    # Return id if one was found
    for id, in cur:
        row_cache[(table, *paramsList)] = id
        return id

    # Otherwise create that row
    result = createRow(table, **params)
    row_cache[(table, *paramsList)] = result
    return result

# separate from row_cache because we need to store info from 2 tables (sort of)
school_cache = {}
def getSchoolId(name: str):
    if name in school_cache:
        return school_cache[name]
    execute("SELECT correct FROM school_alias WHERE name = %s", (name,))
    for id, in cur:
        school_cache[name] = id
        return id
    execute("SELECT id FROM school WHERE name = %s", (name,))
    for id, in cur:
        school_cache[name] = id
        return id
    res = createRow("school", name = name)
    school_cache[name] = res
    return res

"""
Add a contestant
Expects a dictionary containing:
  * 'name'
  * 'class'
  * 'fields'
  * 'instructors'
  * 'school'
  * 'placement'
, the parent subcontest's id and the columns' ids
"""
def addContestant(contestant, subcontestId, columnIds):
    # Age group id could be NULL
    ageGroupId = None
    if contestant['class'] is not None and contestant['class'] != '':
        # Get age group
        ageGroupId = str(getMakeRow('age_group',
                                min_class = contestant['class'],
                                max_class = contestant['class']))

    # Get person
    personId = getMakeRow('person', name = contestant['name'])

    # Get school
    schoolId = None
    if contestant['school'] is not None and contestant['school'] != '':
        schoolId = getSchoolId(contestant['school'])

    # Create contestant
    contestantId = createRow('contestant',
                         subcontest_id = str(subcontestId),
                         person_id = str(personId),
                         age_group_id = ageGroupId,
                         school_id = schoolId,
                              placement = contestant['placement'].strip() or None if contestant['placement'] else None)

    # Create fields for contestant
    # these are inserted in batch later
    fieldsToInsert = []
    for c, v in zip(columnIds, contestant['fields']):
        # (task_id, contestant_id, entry)
        fieldsToInsert.append((str(c), str(contestantId), str(v) if v is not None else None))

    # Create people for mentors
    mentorIds = [getMakeRow('person', name = m) for m in contestant['instructors']]

    # Link mentors
    # same as with fields
    mentorsToInsert = []
    for m in mentorIds:
        # (contestant_id, mentor_id)
        mentorsToInsert.append((str(contestantId), str(m)))
    return fieldsToInsert, mentorsToInsert


"""
Add a subcontest
Expects a dictionary containing:
  * 'name'
  * 'class_range'
  * class_range_name
  * 'columns'
  * 'contestants'
and the parent contest's id
"""
def addSubcontest(subcontest, contestId):
    # Get age group
    ageGroupId = getMakeRow('age_group',
                       name = subcontest['class_range_name'],
                       min_class = str(subcontest['class_range'][0]),
                       max_class = str(subcontest['class_range'][1]))

    execute("SELECT id FROM subcontest WHERE contest_id = %s AND age_group_id = %s", (str(contestId), str(ageGroupId)))
    if cur.fetchone():
        raise Exception("this contest already has this subcontest")
    # Create subcontest
    subcontestId = createRow('subcontest',
                         contest_id = str(contestId),
                         age_group_id = str(ageGroupId),
                         name = subcontest['name'],
                         description = subcontest['description'])

    # Create columns
    columns = []
    for i, c in enumerate(subcontest['columns'], 1):
        columns.append(createRow('subcontest_column',
                             subcontest_id = str(subcontestId),
                             name = c,
                             seq_no = i))

    fieldsToInsert = []
    mentorsToInsert = []
    # Create contestants
    for c in subcontest['contestants']:
        res = addContestant(c, subcontestId, columns)
        fieldsToInsert += res[0]
        mentorsToInsert += res[1]
    if fieldsToInsert:
        query = "INSERT INTO contestant_field (task_id, contestant_id, entry) VALUES (%s, %s, %s)"
        debug('Query (executemany): "' + query + '" ' + str(fieldsToInsert))
        cur.executemany(query, fieldsToInsert)
    if mentorsToInsert:
        query = "INSERT INTO mentor (contestant_id, mentor_id) VALUES (%s, %s)"
        debug('Query (executemany): "' + query + '" ' + str(mentorsToInsert))
        cur.executemany(query, mentorsToInsert)


"""
Add a contest
Expects a dictionary containing:
  * 'year'
  * 'subject'
  * 'type'
  * 'name'
  * 'subcontests'

Additionally, whether to perform a "dry run" (rollback)
"""
def addContest(contest, dryRun = False):
    try:
        # Get parameters
        typeId = getMakeRow('type', name = contest['type'])
        subjectId = getMakeRow('subject', name = contest['subject'])
        # Create contest
        # todo should actually not be getMakeRow.... want year+type_id+subject_id to be unique
        contestId = getMakeRow('contest',
                              year = contest["year"],
                              type_id = typeId,
                              subject_id = subjectId,
                              name = contest['name'])

        # Create subcontests
        for sc in contest['subcontests']:
            addSubcontest(sc, contestId)

        if dryRun:
            conn.rollback()
            info("Contest added (dry run)")
        else:
            conn.commit()
            info("Contest added")
    except Exception as e:
        conn.rollback()
        row_cache.clear()
        school_cache.clear()
        logging.exception(e)
        raise Exception()

