
"""
Delete a subcontest by id.

Checks for that contest in the database, then prompts before deleting. The
response should be "yes" to proceed.

When confirmed, deletes all data related to this subcontest, including mentors,
extra columns and contestant data.
"""

import sys
import os
import json
import mysql.connector

if len(sys.argv) < 2:
    print("Missing id")
    sys.exit(1)

id = sys.argv[1]

# Credentials
with open(os.path.join(os.path.dirname(__file__),"credentials.json")) as f:
    config = json.loads(f.read())
mysql_user = config["user"]
mysql_passwd = config["password"]
mysql_db = config["database"]
mysql_host = config["host"]

conn = mysql.connector.connect(user=mysql_user, password=mysql_passwd, database=mysql_db, host=mysql_host)
cur = conn.cursor()

cur.execute('SELECT name, contest_id FROM subcontest WHERE id = %s', (id,))
name, contestId = next(cur)

cur.execute('SELECT name FROM contest WHERE id = %s', (contestId,))
contestName, = next(cur)

ans = input(f'Delete id {id}, "{contestName} {name}"? ')
print(ans)
if ans.upper() != 'YES':
    print('Cancel')
    sys.exit(0)
    
idt = (id,)
print('.', end='')
sys.stdout.flush()
cur.execute('DELETE FROM contestant_field WHERE contestant_id IN (SELECT id FROM contestant WHERE subcontest_id = %s)', idt)
print('.', end='')
sys.stdout.flush()
cur.execute('DELETE FROM subcontest_column WHERE subcontest_id = %s', idt)
print('.', end='')
sys.stdout.flush()
cur.execute('DELETE FROM mentor WHERE contestant_id IN (SELECT id FROM contestant WHERE subcontest_id = %s)', idt)
print('.', end='')
sys.stdout.flush()
cur.execute('DELETE FROM contestant WHERE subcontest_id = %s', idt)
print('.')
cur.execute('DELETE FROM subcontest WHERE id = %s', idt)

conn.commit()

print("Done")
