
import sys
import sqlite3
from time import gmtime, strftime

sqliteDBFileName = 'timetracker.db'
commandList = ['start', 'stop', 'status']

class SQLiteHandler:
    def __init__(self):
        self.db = None
        self.cursor = None

    def connect(self):
        self.db = sqlite3.connect(sqliteDBFileName)
        self.cursor = self.db.cursor()

    def disconnect(self):
        self.db.close()

    def execute(self, command):
        self.cursor.execute(command)
        self.db.commit()
        return self.cursor.fetchall()

class Tracker:
    def __init__(self, subject):
        self.subject = subject
        self.sqliteHandler = SQLiteHandler()
        self.sqliteHandler.connect()

    def close(self):
        self.sqliteHandler.disconnect()

    def getCurrentTime(self):
        return strftime('%Y-%m-%d %H:%M:%S', gmtime())

    def starttracking(self):
        if not self.trackingIsStarted():
            self.sqliteHandler.execute('INSERT INTO track (starttime, subject, totalsec) VALUES ("' + self.getCurrentTime() + '", "' + self.subject + '", 0)')
            print('[*] started tracking')
        else:
            print('[!] tracking already started')

    def stoptracking(self):
        if self.trackingIsStarted():
            self.sqliteHandler.execute('UPDATE track SET stoptime = "' + self.getCurrentTime() + '" WHERE id = (SELECT MAX(id) FROM track)')
            self.sqliteHandler.execute('UPDATE track SET totalsec = (SELECT strftime("%s", stoptime) - strftime("%s", starttime) AS duration FROM track WHERE id = (SELECT MAX(id) FROM track)) WHERE id = (SELECT MAX(id) FROM track)')

            print('[*] stopped tracking')
        else:
            print('[!] tracking already stopped')

    def trackingIsStarted(self):
        result = self.sqliteHandler.execute('SELECT stoptime FROM track WHERE id = (SELECT MAX(id) FROM track)')
        if not len(result) == 1:
            return False

        return (result[0][0] == None)

    def status(self):
        print('[*] STATUS')
        if self.trackingIsStarted():
            result = self.sqliteHandler.execute('SELECT * FROM track WHERE id = (SELECT MAX(id) FROM track)')
            timeDifferenceSeconds = self.sqliteHandler.execute('SELECT strftime("%s", "now") - strftime("%s", starttime) AS duration FROM track WHERE id = (SELECT MAX(id) FROM track)')[0][0]

            print('    * tracking is started')
            print('    * active subject: ' + result[0][-1])
            print('    * running for ' + str(round(timeDifferenceSeconds/60, 2)) + ' min')
        else:
            print('    * tracking is NOT started')

        trackingData = self.sqliteHandler.execute('SELECT subject, SUM(totalsec) as total FROM track GROUP BY(subject) ORDER BY total DESC')
        print('-------------------')
        print('HOURS PER SUBJECT')
        for dataset in trackingData:
            print(' ' + str(dataset[0]) + ': ' + str(round(dataset[1] /3600, 2)) + ' h')


def main():
    if len(sys.argv) < 2:
        print('[!] no command given')
        quit()

    command = sys.argv[1]

    subject = 'general'
    if len(sys.argv) == 3:
        subject = sys.argv[2]

    if command not in commandList:
        print('[!] command not found')
        quit()

    tracker = Tracker(subject)
    if command == 'start':
        tracker.starttracking()
    elif command == 'stop':
        tracker.stoptracking()
    elif command == 'status':
        tracker.status()
    else:
        print('[!] command not found')

    print('')
    tracker.close()

if __name__ == '__main__':
    main()
