import praw
import re
import sqlite3 as sq3
import time

class GWScraper:
    def __init__(self,delta,maxFetch,uagent):
        """
        delta: int with the time in seconds between pull request. DO NOT GO BELOW 30s
        maxFetch: int containing the maximum number of posts to fetch per iteration.
        uagent: string containing the desired user agent
        """
        self.delta = delta
        self.maxFetch = maxFetch
        self.uagent = uagent
        self.rObj = praw.Reddit(user_agent=self.uagent)
        try:
            self.con = sq3.connect('content.db')
        except:
            sys.exit("Something's wrong with the db")
        self.cur = self.con.cursor()

    def imgurFilter(self,rsltArr):
        filt_rsltArr = []
        for result in rsltArr:
            if(re.search(r'imgur.com',result[2])):
                filt_rsltArr.append(result)
        return filt_rsltArr

    def pullOnce(self):
        try:
            self.rsltObj = self.rObj.get_subreddit('gonewild').get_new(limit=self.maxFetch)
        except:
            sys.exit("You dun goofed.")
        rsltL = [(x.created,x.author.name,x.url) for x in self.rsltObj]
        return self.imgurFilter(rsltL)

    def checkExists(self,entry):
        url = (entry[2],)
        """
        entry: A tuple containing the submission date, author name and URL
        """
        match = self.cur.execute("SELECT url FROM gwhistory WHERE url LIKE ?",url)
        if len(match.fetchall()) > 0:
            return True
        return False

    def addNew(self,entry):
        """
        entry: A tuple containing the submission date, author name and URL
        """
        if self.checkExists(entry):
            return 0
        self.cur.execute("INSERT INTO gwhistory VALUES (?,?,?)",entry)
        self.con.commit()
        return 1

    def runPerpet(self):
        i = 0
        while i < 5: #For testing only... use a fucking crontab
            results = self.pullOnce()
            counter = 0
            for entry in results:
                counter+= self.addNew(entry)
            print(str(counter)+" Results added")
            time.sleep(self.delta)
            i+=1

tst = GWScraper(32,100,'gonewildbot')
tst.runPerpet()
