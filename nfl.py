def enterScores(cursor):

    cursor.execute("SELECT * FROM nfl_teams")

    teams = {}
    for row in cursor.fetchall():
        teams[row[1]] = row[0]

    week = input("Enter week number: ")

    weekQuery = """
    SELECT 
       r.teamId AS 'teamId',
       t1.name AS 'team',
       IFNULL(d1.owner, "Undrafted") AS 'owner',
       r.oppId AS 'opponentId',
       t2.name AS 'opponent',
       IFNULL(d2.owner, "Undrafted") AS 'oppOwner'
    FROM nfl_results AS r
    LEFT OUTER JOIN nfl_teams AS t1 ON (t1.id = r.teamId)
    LEFT OUTER JOIN nfl_draft AS d1 ON (d1.team = t1.name)
    LEFT OUTER JOIN nfl_teams AS t2 ON (t2.id = r.oppId)
    LEFT OUTER JOIN nfl_draft AS d2 ON (d2.team = t2.name)
    WHERE r.week={} AND location='A' AND score=0 AND oppScore=0
    """

    cursor.execute(weekQuery.format(week))

    for row in cursor.fetchall():
        print "Enter score for {} @ {}".format(row[1], row[4])
        score = input("   {}: ".format(row[1]))
        oppScore = input("   {}: ".format(row[4]))
        query = "UPDATE nfl_results SET score={}, oppScore={} WHERE teamId={} AND oppId={} AND week={}"
        cursor.execute(query.format(score, oppScore, row[0], row[3], week))
        cursor.execute(query.format(oppScore, score, row[3], row[0], week))


def results(cursor):
    cursor.execute('''
    SELECT owner, SUM(wins) AS "Wins", SUM(losses) AS "Losses"
    FROM nflRecords
    WHERE owner IS NOT NULL
    GROUP BY owner
    ORDER BY Wins DESC''')
    count = 0
    print '''
------------------------------------------
- NFL
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
          SELECT pick, owner, team, IFNULL(wins,0), IFNULL(losses,0)
          FROM nfl_draft
          LEFT OUTER JOIN nfl_teams ON (nfl_draft.team = nfl_teams.name)
          LEFT OUTER JOIN nflWins ON (nfl_teams.id = nflWins.teamId)
          LEFT OUTER JOIN nflLosses ON (nfl_teams.id = nflLosses.teamId)
          ORDER BY pick ASC
        ''')
    else:
        cursor.execute('''
          SELECT pick, owner, team, IFNULL(wins,0), IFNULL(losses,0)
          FROM nfl_draft
          LEFT OUTER JOIN nfl_teams ON (nfl_draft.team = nfl_teams.name)
          LEFT OUTER JOIN nflWins ON (nfl_teams.id = nflWins.teamId)
          LEFT OUTER JOIN nflLosses ON (nfl_teams.id = nflLosses.teamId)
          WHERE owner = '{}'
          ORDER BY pick ASC
        '''.format(owners[owner]))
    for row in cursor.fetchall():
        print "{}. {} - {} ({}-{})".format(row[0], row[1], row[2], row[3], row[4])
