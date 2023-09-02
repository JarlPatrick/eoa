
"""
The main utility file for importing a contest (possibly just a single
subcontest). `addContest` should be about the only function used from this
module, as it is the only one that tries to manage the connection state and
errors properly.

Currently, no checks are performed for similar names (even ones with just
differing case), so duplicates might occur. Care should be taken especially
with contest and subcontest identifiers (year, subject, type, age group, name).
"""

import mysql.connector
import logging

logging.basicConfig(level=logging.DEBUG)

# Credentials
mysql_user = ""
mysql_passwd = ""
mysql_db = "eoa"
mysql_host = "eoa.ee"

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

"""
Get the id of a row in a table based on parameters
Insert that row if it does not exist
"""
def getMakeRow(table, getId = True, **params):
    # Get params as ordered list
    paramsList = [(k, v) for k, v in params.items()]

    # Convert to statement and execute
    execute("SELECT " + ("id" if getId else "NULL") + f" FROM {table} WHERE " + ' and '.join(p[0] + (' is %s' if p[1] is None else ' = %s') for p in paramsList) + ' LIMIT 1', tuple(p[1] for p in paramsList))

    # Return id if one was found
    for id, in cur:
        return id

    # Otherwise create that row
    return createRow(table, **params)

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
    schoolId = getMakeRow('school', name = contestant['school'])
    
    # Create contestant
    contestantId = getMakeRow('contestant',
                         subcontest_id = str(subcontestId),
                         person_id = str(personId),
                         age_group_id = ageGroupId,
                         school_id = str(schoolId),
                              placement = contestant['placement'].strip() or None if contestant['placement'] else None)

    # Create fields for contestant
    for c, v in zip(columnIds, contestant['fields']):
        createRow('contestant_field',
              task_id = str(c),
              contestant_id = str(contestantId),
              entry = str(v))
    
    # Create people for mentors
    mentorIds = [getMakeRow('person', name = m) for m in contestant['instructors']]

    # Link mentors
    for m in mentorIds:
        getMakeRow('mentor', getId = False,
              contestant_id = str(contestantId),
              mentor_id = str(m))
    

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
    
    # Create subcontest
    subcontestId = getMakeRow('subcontest',
                         contest_id = str(contestId),
                         age_group_id = str(ageGroupId),
                         name = subcontest['name'])

    # Create columns
    columns = []
    for i, c in enumerate(subcontest['columns'], 1):
        columns.append(getMakeRow('subcontest_column',
                             subcontest_id = str(subcontestId),
                             name = c,
                             seq_no = i))

    # Create contestants
    for c in subcontest['contestants']:
        addContestant(c, subcontestId, columns)
    
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
        yearId = getMakeRow('year', name = contest['year'])
        typeId = getMakeRow('type', name = contest['type'])
        subjectId = getMakeRow('subject', name = contest['subject'])
        # Create contest
        contestId = getMakeRow('contest',
                              year_id = yearId,
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
        logging.exception(e)
        raise Exception()

