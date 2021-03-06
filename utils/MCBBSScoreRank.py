import utils.getMcbbsScore as getMcbbsScore
import utils.database as database
import pandas as pd
from datetime import datetime,timedelta

def getProfile(n):
    profile = getMcbbsScore.getScoreFromUid(n)
    return profile

def delline(table,nlist):
    df = database.getTable(table)
    for n in nlist:
        df = df[~df.uid.isin([str(n)])]
    database.setTable(table,df)

def addline(table,profilelist):
    df = database.getTable(table)
    for profile in profilelist:
        addition = {
            'time' : profile.get('time'),
            'uid' : profile.get('uid'),
            'username' : profile.get('username'),
            'usergroup' : profile.get('usergroup'),
            'topic' : profile.get('topic'),
            'reply' : profile.get('reply'),
            'onlineTime' : profile.get('onlineTime'),
            'regTime' : profile.get('regTime'),
            'lastSeenTime' : profile.get('lastSeenTime'),
            'medal' : profile.get('medal'),
            'rq' : profile.get('score')[1],
            'jl' : profile.get('score')[2],
            'jd' : profile.get('score')[3],
            'lbs' : profile.get('score')[4],
            'xjzx' : profile.get('score')[5],
            'gx' : profile.get('score')[6],
            'ax' : profile.get('score')[7],
            'zs' : profile.get('score')[8],
            'score' : profile.get('score')[0],
        }
        df = df.append(addition,ignore_index=True)
    database.setTable(table,df)
    return 0

def updateProfile(uidlist):
    print('-----------------')
    print('现在获取: '+str(uidlist))
    print('-----------------')
    profilelist = []
    for uid in uidlist:
        profilelist.append(getProfile(uid))
    delline('score',uidlist)
    re1 = addline('score',profilelist)
    print('-----------------')
    print('获取成功: '+str(uidlist))
    print('-----------------')

def output():
    default()
    try:
        df = database.getTable('score')
        print(df)
        df['Rank'] = df['score'].rank(method='min',ascending=False)
        df['Rank'] = df['Rank'].astype(int)
        df = df.set_index('Rank',drop=False)
        df = df.sort_index()
        Delta = [0]
        len = int(df.shape[0])
        for i in range(1,len):
            numthis = df.at[df.index[i-1],'score']
            numnext = df.at[df.index[i],'score']
            try:
                diff = '+' + str(int(numthis)-int(numnext))
                if diff == 0:
                    diff = ''
            except TypeError:
                diff = '?'
            Delta.append(diff)
        Delta.append('-')
        df['Delta'] = pd.DataFrame(Delta)
        df = df.rename(columns={"Rank":"排名","time":"最近一次获取时间","username":"用户名","usergroup":"用户组","score":"积分","Delta":"","uid":'UID'})
        result = df.to_html(justify='center',table_id='result',escape=False,index=False,columns=['排名','最近一次获取时间','UID','用户名','用户组','积分',''])
        return result
    except ValueError:
        return '数据获取失败：数据仍未更新。'

def createTable():
    if ( database.getTable('score',True) ) :
        return
    else:
        database.createTable('score',['time','uid','username','usergroup','topic','reply','onlineTime','regTime','lastSeenTime','medal','rq','jl','jd','lbs','xjzx','gx','ax','zs','score'])

def forceUpdate(i=None):
    default()
    list = getUidList()
    n = list[0]
    if i and i<= n:
        getId = i
        interval = 60
    else:
        getId = int(database.getConf('rank.taskId'))
        interval = 1
        if getId > n:
            getId=1
        newId =getId+1
        database.setConf('rank.taskId',newId)
    ulist = list[getId]
    updateProfile(ulist)
    content = {
        'id' : getId,
        'uid' : ulist,
        'interval' : interval,
    }
    return content

def getUidList():
    file = open('./templates/mcbbs-score-rank/list.txt','r')
    uidlist = []
    for uid in file:
        uidlist.append(int(str(uid).replace('\n','')))
    #修改每次获取的数目
    O = 3
    l = len(uidlist)
    j = int(l/O)+1
    k = l%O
    list = [j]
    for i in range(0,j):
        temp = []
        if i == j-1:
            for z in range(0,k):
                x = uidlist[O*i+z]
                temp.append(x)
            list.append(temp)
            break
        for z in range(0,O):
            x = uidlist[O*i+z]
            temp.append(x)
        list.append(temp)
    return list

def default():
    try:
        id = database.getConf('rank.taskId',-1)
        if id != -1:
            return
        else: 
            database.getTable('score')
            createTable()
            ### 初始化taskid
            database.setConf('rank.taskId',1)
    except:
        database.getTable('score')
        createTable()
        ### 初始化taskid
        database.setConf('rank.taskId',1)