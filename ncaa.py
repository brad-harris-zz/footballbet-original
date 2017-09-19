def enterScores(cursor):
    unscoredQuery = """CREATE TEMPORARY TABLE unscored AS (
       SELECT 
         r.schoolID AS "schoolId",
         s1.name AS "school", 
         IFNULL(d1.owner, "Undrafted") AS "owner",
         r.opponentId AS "opponentId",
         s2.name AS "opponent", 
         IFNULL(d2.owner,"Undrafted") AS "oppOwner",
         r.location AS "location"
       FROM ncaa_results AS r
       LEFT OUTER JOIN fbs_schools AS s1 ON (s1.id = r.schoolId)
       LEFT OUTER JOIN fbs_schools AS s2 ON (s2.id = r.opponentId)
       LEFT OUTER JOIN ncaa_draft AS d1 ON (d1.schoolId = r.schoolId)
       LEFT OUTER JOIN ncaa_draft AS d2 ON (d2.schoolId = r.opponentId)
       WHERE
	r.gameDay < curdate() AND
       	score = 0 AND
       	oppScore = 0
    )"""

    ownedQuery = "SELECT * FROM unscored WHERE owner != 'Undrafted' OR oppOwner != 'Undrafted'"

    cursor.execute(unscoredQuery)
    cursor.execute(ownedQuery)

    def gameScored(school, opponent):
        for g in games:
            if g['schoolId'] == school and g['opponentId'] == opponent:
                return True
            return False

    games = []

    def addGame(game):
        for g in games:
            if g['schoolId'] == game['schoolId'] and g['oppId'] == game['oppId']:
                return
            if g['schoolId'] == game['oppId'] and g['oppId'] == game['schoolId']:
                return
        games.append(game)

    for row in cursor.fetchall():
        if row[6] == "H":
            game = {
                'schoolId': row[0],
                'schoolName': row[1],
                'schoolOwner': row[2],
                'oppId': row[3],
                'oppName': row[4],
                'oppOwner': row[5]
            }
        else:
            game = {
                'schoolId': row[3],
                'schoolName': row[4],
                'schoolOwner': row[5],
                'oppId': row[0],
                'oppName': row[1],
                'oppOwner': row[2]
            }

        addGame(game)

    gameFmt = "Enter score for {} ({}) vs {} ({}) ({}/{})"
    count = 0
    if len(games) == 0:
        print "No scores to update"
    for g in games:
        count = count + 1
        print gameFmt.format(g['oppName'], g['oppOwner'], g['schoolName'], g['schoolOwner'], count, len(games))
        scoreStr = "  {}: "
        oppScore = input(scoreStr.format(g['oppName']))
        score = input(scoreStr.format(g['schoolName']))

        scoreQuery = "UPDATE ncaa_results SET score={}, oppScore={} WHERE schoolId={} AND opponentId={}"
        cursor.execute(scoreQuery.format(score, oppScore, g['schoolId'], g['oppId']))
        cursor.execute(scoreQuery.format(oppScore, score, g['oppId'], g['schoolId']))


def results(cursor):
    cursor.execute('''
      SELECT owner, SUM(wins) AS "Wins", SUM(losses) AS "Losses"
      FROM ncaaRecords
      WHERE owner IS NOT NULL
      GROUP BY owner
      ORDER BY Wins DESC
    ''')
    count = 0
    print '''
------------------------------------------
- NCAA
------------------------------------------
    '''
    for row in cursor.fetchall():
        count = count + 1
        print "{} - {} ({}-{})".format(count, row[0], row[1], row[2])

def draft(cursor):
    owners = {
        1: 'Adam',
        2: 'Brad',
        3: 'Brian',
        4: 'Chad',
        5: 'Mike'
    }
    owner = 0
    while owner < 1 or owner > 6:
        print "Filter by owner"
        for key, value in owners.items():
            print "\t{} - {}".format(key, value)
        print "\t6 - All"
        owner = input("Make a selection: ")

    if owner == 6:
        cursor.execute('''
        SELECT pick, owner, name, IFNULL(wins,0), IFNULL(losses,0)
        FROM ncaa_draft
        LEFT OUTER JOIN fbs_schools ON (ncaa_draft.schoolId = fbs_schools.id)
        LEFT OUTER JOIN ncaaWins ON (ncaa_draft.schoolId = ncaaWins.schoolId)
        LEFT OUTER JOIN ncaaLosses ON (ncaa_draft.schoolId = ncaaLosses.schoolId)
        ORDER BY pick
        ''')
    else:
        cursor.execute('''
        SELECT pick, owner, name, IFNULL(wins,0), IFNULL(losses,0)
        FROM ncaa_draft
        LEFT OUTER JOIN fbs_schools ON (ncaa_draft.schoolId = fbs_schools.id)
        LEFT OUTER JOIN ncaaWins ON (ncaa_draft.schoolId = ncaaWins.schoolId)
        LEFT OUTER JOIN ncaaLosses ON (ncaa_draft.schoolId = ncaaLosses.schoolId)
        WHERE owner='{}'
        ORDER BY pick
        '''.format(owners[owner]))
    for row in cursor.fetchall():
        print "{}. {} - {} ({}-{})".format(row[0], row[1], row[2], row[3], row[4])
