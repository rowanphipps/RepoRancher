import json
import httplib2
import time
import random
import math
import base64
from flask import abort

class monster(object):
    def __init__(self, user, repo):
        self.user = user
        self.repo = repo
        self.name = repo
        self.log = [user+' '+repo]
        self.style = 'progress-success'
        #self.requestInfo()

    def requestInfo(self):
        baseURL = "https://api.github.com/repos/" + self.user + '/' + self.repo

        
        repoData = self.getDataFrom(baseURL)

        # test = self.basicAuthReq("https://api.github.com/rate_limit")
        # print test[0]
        # print test[1]

        #print type(repoData)
        #print repoData

        self.maxHealth = int(repoData['size'])
        self.current = self.maxHealth

        stats = self.getDataFrom(baseURL+"/stats/contributors")


        averages = self.getAverages(stats)

        self.strength = int(averages['additions']) #* math.log(self.maxHealth))

        self.defense = int(averages['commits'])

        self.accuracy = int(self.getAccuracy(averages['deletions']))
        
        self.percentStyle()


    def getDataFrom(self, baseURL):
        resp, data = self.basicAuthReq(baseURL)
        
        status = resp['status']
        

        #print baseURL, status
        for i in xrange(1,10):
            self.log.append(str(i+1) + " try status = "+status)
            print self.log[-1]
            if status == '200':
                break

            elif status == '202':
                time.sleep(0.1)
                resp, data = self.basicAuthReq(baseURL)
                status = resp['status']

            else:
                self.log.append(status + " called by github")  
                abort(int(status))

        if not data:
            print "git hub is not very nice. :("
            abort(404)

        # print len(data)

        
        return json.loads(data)

    def basicAuthReq(self, url):

        token="a7c07a37a228b264c9d139d2c476a97400c6d381"

        h = httplib2.Http()
        auth = base64.encodestring( 'rowanphipps' + ':' + token )
 
        resp, content = h.request(url, 'GET', headers={ 'Authorization' : 'Basic ' + auth })  

        # print type(resp)
        # print type(content)

        return resp, content

    def getAverages(self, stats):
        weeks = 0.0
        averages = {
            "additions": 0,
            "deletions": 0,
            "commits": 0
        }
        #print type(stats)
        #print len(stats)

        try:
            decodedStats = json.load(stats)
        except:
            decodedStats = stats

        for i in stats:

            # try:
            #     decodedStats = json.load(i)
            # except:
            #     decodedStats = i

            #decodedStats = json.load(i)

            # print decodedStats


            for week in i[u'weeks']:

                if week[u'c'] > 0:
                    weeks += 1
                    averages['additions'] += week[u'a']
                    averages['deletions'] -= week[u'd']
                    averages['commits'] += week[u'c']



        averages['additions'] /= weeks
        averages['deletions'] /= weeks
        averages['commits'] /= weeks

        return averages

    def getAccuracy(self, deletions):
        num = len(str(int(deletions)))*10
        num += deletions % 10
        num += 25
        return num

    def updatePercent(self):
        self.percent = int((self.current / float(self.maxHealth)) * 100)

    def percentStyle(self):
        self.updatePercent()

        if self.percent <= 15:
            self.style =  "progress-danger"

        elif self.percent <= 30:
            self.style = "progress-warning"

        else:
            self.style = "progress-success"

    def stillAlive(self):
        return self.current > 0

    def printStats(self):
        print self.name
        print self.maxHealth
        print self.strength
        print self.defense
        print self.accuracy
        print self.percent

    def fight(self, m2):
        record = []
        row = 1
        # print "fight called"
        live = True
        while live:
            # print "row {0} {1} {2}".format(row, self.current, m2.current)
            row += 1
            #m1 = self
        
            record.append(self.attack(m2))
            record.append(m2.attack(self))

            # print "done attacking"

            if not self.stillAlive() and not m2.stillAlive():
                # print "both dead"
                record.append("Both monsters died!")
                winner = "Tie game"
                live = False
                break

            elif not m2.stillAlive():
                # print "m2 dead"
                record.append(m2.name + " has died!")
                winner = self.name + " wins!"
                live = False
                break

            elif not self.stillAlive():
                # print "m1 dead"
                record.append(self.name + " has died!")
                winner = m2.name + " wins!"
                live = False
                break

            # if len(record)%10 == 0:
            #     print len(record)
        # print "exited loop"

        self.percentStyle()
        m2.percentStyle()

        # print "updated percentage", self.percent, self.style, m2.percent, m2.style

        return (record, winner)

    def attack(self, enemy):
        toHit = random.randint(1,100)

        # print "attacking"

        # print "{0} to hit, {1} strength, broken? defense".format(toHit, self.strength)
        # print random.triangular(0.8, 1.2)

        damage = max(1, int((self.strength - enemy.defense)*random.triangular(0.8, 1.2)))

        # print "{0} damage".format(damage)

        if toHit <= self.accuracy:

            # print "hits"
            
            enemy.current -= damage
            enemy.current = max(0, enemy.current)
            
            return self.name + " hits " + enemy.name + " for " + str(damage) + "!"

        else:
            # print "missed"
            return self.name + " missed!"

    # def defend(self, enemy):
    #     toHit = random.randint(1,100)

    #     print "attacking"

    #     print "{0} to hit, {1} strength, broken? defense".format(toHit, enemy.strength)
    #     print random.triangular(0.8, 1.2)

    #     damage = max(1, int((enemy.strength - self.defense)*random.triangular(0.8, 1.2)))

    #     print "{0} damage".format(damage)

    #     if toHit <= enemy.accuracy:

    #         print "hits"
            
    #         self.current -= damage
    #         self.current = max(0, self.current)
            
    #         return enemy.name + " hits " + self.name + " for " + str(damage) + "!"

    #     else:
    #         print "missed"
    #         return enemy.name + " missed!"

    # def attack(self, enemy):
    #     toHit = random.randint(1,100)

    #     print "{0} to hit, {1} strength, broken? defense".format(toHit, self.strength)
    #     print random.triangular(0.8, 1.2)

    #     damage = int((self.strength - enemy.defense)*random.triangular(0.8, 1.2))

    #     print "{0} damage".format(damage)

    #     if toHit <= self.accuracy:

    #         print "hits"
            
    #         enemy.current -= damage
    #         enemy.current = max(0, enemy.current)
            
    #         return self.name + " hits " + enemy.name + " for " + str(damage) + "!"

    #     else:
    #         print "missed"
    #         return self.name + " missed!"


# def fight(m1, m2):
#     record = []
#     row = 1
#     live = True
#     while True:
#         print "row", row
#         row += 1

#         record.append(m1.attack(m2))
#         record.append(m2.attack(m1))

#         if m1.stillAlive() and m2.stillAlive():
#             record.append("Both monsters died!")
#             winner = "Tie game"
#             live = False
#             break

#         elif m2.stillAlive():
#             record.append(m2.name + " has died!")
#             winner = m1.name + " wins!"
#             live = False
#             break

#         elif m1.stillAlive():
#             record.append(m1.name + " has died!")
#             winner = m2.name + " wins!"
#             live = False
#             break

#         if len(record)%10 == 0:
#             print len(record)

#     m1.updatePercent()
#     m2.updatePercent()

#     return (record, winner)

# m1=monster('git', "git")
# m1.requestInfo()

# print m1.name
# print m1.accuracy
# print m1.maxHealth
# print m1.defense
# print m1.strength
# print m1.log

# m2 = monster('mongodb', 'mongo')
# m2.requestInfo()
# print m2.name
# print m2.accuracy
# print m2.maxHealth
# print m2.defense
# print m2.strength

# record, winner = fight(m1, m2)

# print winner
# print len(record)

# m2 = monster('Bearded-Hen', 'Android-Bootstrap')
# m2.requestInfo()
# print m2.name
# print m2.accuracy
# print m1.maxHealth
# print m2.defense
# print m2.strength

# m2 = monster('airbnb', 'javascript')
# m2.requestInfo()
# print m2.name
# print m2.accuracy
# print m1.maxHealth
# print m2.defense
# print m2.strength




