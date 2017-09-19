import ncaa
import nfl
import MySQLdb

db = MySQLdb.connect(host="localhost",
                     user="football",
                     passwd="",
                     db="football")

cursor = db.cursor()

# Create temporary tables
cursor.execute('''
CREATE TEMPORARY TABLE IF NOT EXISTS ncaaWins AS (
SELECT schoolId, IFNULL(COUNT(*),0) AS "wins"
FROM ncaa_results
WHERE score > oppScore
GROUP BY schoolId
)''')

cursor.execute('''
CREATE TEMPORARY TABLE IF NOT EXISTS ncaaLosses AS (
SELECT schoolId, IFNULL(COUNT(*),0) AS "losses"
FROM ncaa_results
WHERE score < oppScore
GROUP BY schoolId
)''')

cursor.execute('''
CREATE TEMPORARY TABLE IF NOT EXISTS ncaaRecords AS (
SELECT 
  s.name AS "name", 
  d.owner AS "owner", 
  IFNULL(w.wins,0) AS "wins", 
  IFNULL(l.losses,0) AS "losses"
FROM fbs_schools AS s
LEFT OUTER JOIN ncaa_draft AS d ON (s.id = d.schoolId)
LEFT OUTER JOIN ncaaWins as w ON (s.id = w.schoolId)
LEFT OUTER JOIN ncaaLosses as l ON (s.id = l.schoolId)
)''')

cursor.execute('''
CREATE TEMPORARY TABLE IF NOT EXISTS nflWins AS (
       SELECT teamId, IFNULL(COUNT(*),0) AS "wins"
       FROM nfl_results
       WHERE score > oppScore
       GROUP BY teamId
)''')

cursor.execute('''
CREATE TEMPORARY TABLE IF NOT EXISTS nflLosses AS (
       SELECT teamId, IFNULL(COUNT(*),0) AS "losses"
       FROM nfl_results
       WHERE score < oppScore
       GROUP BY teamId
)''')

cursor.execute('''
CREATE TEMPORARY TABLE IF NOT EXISTS nflRecords AS (
       SELECT
		t.name AS "team",
		d.owner AS "owner",
		IFNULL(w.wins,0) AS "wins",
		IFNULL(l.losses,0) AS "losses"
	FROM nfl_teams AS t
	LEFT OUTER JOIN nfl_draft AS d ON (t.name = d.team)
	LEFT OUTER JOIN nflWins as w ON (t.id = w.teamId)
	LEFT OUTER JOIN nflLosses as l ON (t.id = l.teamId)
)''')

menu = '''
Main Menu
   1 - Enter NCAA Scores
   2 - Enter NFL Scores
   3 - View Standings
   4 - View NCAA Draft
   5 - View NFL Draft
   6 - Exit
Make a selection: '''

choice = 0
while choice != 6:
    choice = input(menu)

    if choice == 1:
        ncaa.enterScores(cursor)
        db.commit()
    if choice == 2:
        nfl.enterScores(cursor)
        db.commit()
    if choice == 3:
        ncaa.results(cursor)
        nfl.results(cursor)
    if choice == 4:
        ncaa.draft(cursor)
    if choice == 5:
        nfl.draft(cursor)
    if choice == 6:
        print "\nGoodbye\n"

db.close()
