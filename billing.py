import os
import string
import pprint
import sys
import sqlite3
import datetime
import time
import re

#TODO  Generate timesheet-appropriate output
#TODO  How to handle tasks that aren't matched at the end of a day?  (my mistake, probably)

CONF = {'DBPATH':"P:\\billing2.db"}

def insert(db,table,args):
    c=db.cursor()
    l=["NULL"]+["?"]*len(args)
    p="("  +  (",".join(l))  +  ")"
    c.execute("INSERT INTO %s VALUES %s" % (table,p),args)
    return c.lastrowid
def add_code(db,code,desc): return insert(db,"codes",(code,desc))
def add_requester(db,requester): return insert(db,"requesters",(string.capwords(requester),))
def add_task(db,code,requester,desc):
    return insert(db,"tasks",(code,requester,desc,"open",today_date()))

def today_date():
    return datetime.date.today().isoformat()
def now_time():
    return ("%02d:%02d" % time.localtime()[3:5])

def print_open_tasks(db):
    c=db.cursor()
    c.execute("SELECT DISTINCT tasks.id,requesters.requester,tasks.desc FROM tasks JOIN requesters WHERE tasks.requester=requesters.id AND tasks.status=?",("open",))
    return c.fetchall()

def print_last_task(db):
    c=db.cursor()
    c.execute("SELECT tasks.id,tasks.desc,billing.date,billing.time FROM tasks JOIN billing WHERE billing.task=tasks.id ORDER BY billing.date DESC,billing.time DESC")
    return c.fetchone()

def punch_last_task(db):
    lt=print_last_task(db)
    if lt:
        return punch(db,first(lt))
    else:
        return -1

def print_table(db,table,order=""):
    c=db.cursor()
    if order!="":
        c.execute("SELECT * FROM %s ORDER BY %s" % (table,order))
    else:
        c.execute("SELECT * FROM %s" % (table,))
    return c.fetchall()

def pairs_from_list(lst):
    if len(lst) < 2: 
        return []
    if len(lst) == 2:
        return [lst]
    else:
        return [[lst[0],lst[1]]] + pairs_from_list(lst[2:])

def packed_duration(pair):
    if len(pair) <2:
        return 0
    return duration(pair[0],pair[1])

def iseven(num):
    if round(num,0)!=num: return False
    return round(num/2,0)==num/2.0
def isodd(num):
    return iseven(num+1)

def car(lst):
    if len(lst) > 0:
        return lst[0]
    else:
        return None
def first(lst):
    return car(lst)

def cdr(lst):
    if len(lst) > 1:
        return lst[1:]
    else:
        return []
def second(lst):
    return car(cdr(lst))

def freverse(lst):
    a=lst
    a.reverse()
    return a

def print_punchtimes_for_task(db,task):
    c=db.cursor()
    c.execute("SELECT date,time FROM billing WHERE task=?",(task,))
    return c.fetchall()

def group_pairs_by_key(lst):
    groups={}
    for x in lst:
        try:
            groups[first(x)]=groups[first(x)]+[second(x)]
        except KeyError:
            groups[first(x)]=[second(x)]
    return groups

def group_rest_by_first(lst):
    groups={}
    for x in lst:
        try:
            groups[first(x)]=groups[first(x)]+[cdr(x)]
        except KeyError:
            groups[first(x)]=[cdr(x)]
    return groups

def update(db,table,i,field,value):
    c=db.cursor()
    c.execute("UPDATE %s SET %s = ? WHERE id = ?" % (table,field), (value,i))
    return c.lastrowid

def punch_finish(db,task):
    punch(db,task)
    return finish(db,task)

def add_punch(db):
    return punch(db, interactive_add_task(db))

def get_unmatched_punches(db):
    c=db.cursor()
    c.execute("SELECT billing.task,billing.date,billing.time FROM billing JOIN tasks WHERE billing.task=tasks.id AND tasks.status !=?",("DONE",))
    tasks=group_rest_by_first(c.fetchall())
    return [a for a in tasks if isodd(len(tasks[a]))]

def punch_unmatched(db):
    c=db.cursor()
    unmatched=get_unmatched_punches(db)
    assert_unmatched=zip(["tasks.id"]*len(unmatched),["?"]*len(unmatched))
    c.execute("SELECT tasks.id,requesters.requester,tasks.desc FROM tasks JOIN requesters WHERE tasks.requester = requesters.id AND (%s)" % sql_or(assert_unmatched),unmatched)
    ch=choose_interactively(c.fetchall())
    if not ch: return -1
    return punch(db, first(ch))

def punch_recent(db):
    c=db.cursor()
    c.execute("SELECT DISTINCT tasks.id,requesters.requester,tasks.desc FROM tasks JOIN requesters JOIN billing WHERE tasks.requester = requesters.id AND billing.task=tasks.id AND tasks.status!=? ORDER BY billing.date DESC,billing.time DESC LIMIT 5",("DONE",))
    ch=choose_interactively(c.fetchall())
    if not ch: return -1
    return punch(db, first(ch))    

def sql_or(checks): return " OR ".join(["=".join([str(first(a)),str(second(a))]) for a in checks])

def punch(db,task):
    if get_id(db,"tasks","id",task) != task: return -1
    return insert(db,"billing",(task,today_date(),now_time()))

def finish(db,task):
    return update(db,"tasks",task,"status","DONE")

def search_table(db,table,field,s):
    c=db.cursor()
    c.execute("SELECT %s FROM %s" % (field,table))
    return fuzzy_filter([x[0] for x in c.fetchall()],s)

def task_time_billed_daily(db,task):
    g=group_pairs_by_key(print_punchtimes_for_task(db,task))
    return [(x,bill_time(g[x])) for x in g]
    
def bill_time(punchlist):
    total_time=sum([packed_duration(x) for x in pairs_from_list(punchlist)])
    return billed_time(total_time)

def ceil(num):
    return round(num+0.5,0)
def floor(num):
    return round(num-0.5,0)

def billed_time(minutes):
    return ceil(minutes/15)/4

def minutes_from_time(string):
    (hours,minutes)=string.split(":")
    return int(minutes)+60*int(hours)

def duration(time1,time2):
    return minutes_from_time(time2)-minutes_from_time(time1)

def list_sss(db):
    c=db.cursor()
    c.execute("SELECT tasks.id,requesters.requester,tasks.desc FROM requesters JOIN tasks WHERE tasks.code=? AND requesters.id = tasks.requester",(get_id(db,"codes","code","SSS"),))
    return c.fetchall()

def fix_sss(db):
    c=choose_interactively(list_sss(db))
    if c == None: return 0
    print("Find Billing Code")
    p=pick_from_table(db,"codes","code")
    if not p: return 0
    return update(db,"tasks",c[0],"code", p)

def get_val(db,get,table,field,s):
    c=db.cursor()
    c.execute("SELECT %s FROM %s WHERE %s=?" % (get,table,field),(s,))
    r=c.fetchone()
    if r: r=r[0]
    return r

def get_id(db,table,field,s):
    c=db.cursor()
    return get_val(db,'id',table,field,s)
    
def fuzzy_filter(lst,s):
    return [a for a in lst if re.findall(s,a,re.IGNORECASE)]

def interactive_add_task(db):
    print("Find Requester")
    r=pick_from_table(db,"requesters","requester")
    if r == None: return 0
    print("Find Billing Code")
    c=pick_from_table(db,"codes","code")
    if c == None: return 0
    d=raw_input("Description: ")
    if d == None:
        print("Description required")
        return 0
    return add_task(db,c,r,d)

def quick_add_task(db,requester,description,code="SSS"):
    c=db.cursor()
    sr=search_table(db,"requesters","requester",requester)
    sc=search_table(db,"codes","code",code)
    if len(sr)==1 and len(sc)==1:
        r=get_id(db,"requesters","requester",first(sr))
        c=get_id(db,"codes","code",first(sc))
        t=add_task(db,c,r,description)
        punch(db,t)
        return t
    else:
        print("Failed to add task")
        raw_input("")
        return -1

def choose_interactively_once(lst):
    s=raw_input("Search: ")
    r=fuzzy_filter(lst,s)
    return choose_interactively(r)

def choose_interactively(r):
    if len(r) == 0:
        print("No match")
        return None
    if len(r) > 0:
        for (a,i) in zip(r,range(1,len(r)+1)):
            print("%d   %s" % (i,a))
        c = raw_input("Choice: ")
        if c==" ": c="1"
        if c in map(str,range(1,len(r)+1)):
            print(str(r[int(c)-1])+"\n")
            return r[int(c)-1]
        else:
            return None

def pick_from_table(db,table,sfield,order="id ASC"):
    c=db.cursor()
    s=search_table(db,table,sfield,r'.*')
    v=choose_interactively_once(s)
    if v not in s:
        return None
    else:
        return get_id(db,table,sfield, v)

def std_init(db):
    initialize_tables(db)
    CODES=[("AEADMIN","Administrative Non-Recharge"),("AESTAN","Campus Standards Non-Recharge"),("SSS", "Super Secret Scan!"),("IFORGOT", "Failure to Bill")]
    REQUESTERS=["Med","Bruce","Sadie","Kevin F","Kevin C","Felix","Julian","Tal","Rhonda","Bret","Dean F","Dean R","Mendel","Courtney","Diane","Diana","Raphael","Matt","Steve","Wenbo","Alisa"]
    for code in CODES:     add_code(db,code[0],code[1])
    for req in REQUESTERS: add_requester(db,req)
    db.commit()

def stddb():
    return sqlite3.connect(CONF['DBPATH'])

def initialize_tables(db):
    wipe_history(db)
    c=db.cursor()
    try:
        c.execute("CREATE TABLE codes (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT, desc TEXT)")
    except sqlite3.OperationalError:
        c.execute("DROP TABLE codes")
        c.execute("CREATE TABLE codes (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT, desc TEXT)")
    try:
        c.execute("CREATE TABLE requesters (id INTEGER PRIMARY KEY AUTOINCREMENT, requester TEXT)")
    except sqlite3.OperationalError:
        c.execute("DROP TABLE requesters")
        c.execute("CREATE TABLE requesters (id INTEGER PRIMARY KEY AUTOINCREMENT, requester TEXT)")

def wipe_history(db):
    c=db.cursor()
    try:
        c.execute("CREATE TABLE billing (id INTEGER PRIMARY KEY AUTOINCREMENT, task UNSIGNED INTEGER, date DATE, time TIME)")
    except sqlite3.OperationalError:
        c.execute("DROP TABLE billing")
        c.execute("CREATE TABLE billing (id INTEGER PRIMARY KEY AUTOINCREMENT, task UNSIGNED INTEGER, date DATE, time TIME)")
    try:
        c.execute("CREATE TABLE tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, code INTEGER, requester INTEGER, desc TEXT, status TEXT, created DATE)")
    except sqlite3.OperationalError:
        c.execute("DROP TABLE tasks")
        c.execute("CREATE TABLE tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, code INTEGER, requester INTEGER, desc TEXT, status TEXT, created DATE)")

def run_command(cmd,args=[]):
    db=stddb()

    pp=pprint.PrettyPrinter(indent=4,width=10)

    #QUICK ADD
    if cmd=="quick_add":
        if len(args) not in range(2,3): return -1
        if len(args) == 3:
            quick_add_task(db,args[0],args[1],args[2])
        else:
            quick_add_task(db,args[0],args[1])

    #LIST SSS
    if cmd=="list_sss":
        if len(args) != 0: return -1
        pp.pprint(list_sss(db))
        raw_input("")

    #FIX SSS
    if cmd=="fix_sss":
        if len(args) != 0: return -1
        fix_sss(db)

    #PUNCH LAST
    if cmd=="punch_last":
        if len(args) != 0: return -1
        punch_last_task(db)
    
    #SHOW LAST
    if cmd=="show_last":
        if len(args) != 0: return -1
        print(print_last_task(db))
        raw_input("")

    #PUNCH RECENT
    if cmd=="punch_recent":
        if len(args) != 0: return -1
        punch_recent(db)    

    #SHOW UNMATCHED
    if cmd=="list_unmatched":
        if len(args) != 0: return -1
        pp.pprint(get_unmatched_punches(db))
        raw_input("")

    #FIX UNMATCHED
    if cmd=="fix_unmatched":
        if len(args) != 0: return -1
        punch_unmatched(db)

    #SHOW OPEN
    if cmd=="list_open":
        if len(args) != 0: return -1
        pp.pprint(print_open_tasks(db))
        raw_input("")

    #ADD CODE
    if cmd=="add_code":
        if len(args) != 1: return -1
        add_code(db,args[0])

    #ADD REQUESTER
    if cmd=="add_requester":
        if len(args) != 1: return -1
        add_requester(db,args[0])

    if cmd=="add_punch":
    	if len(args) != 0: return -1
	add_punch(db)

    #FINISH TASK
    if cmd=="finish_last_task":
        if len(args) != 0: return -1
        l=print_last_task(db)
        if l:
            finish(db,first(l))
        else:
            return -1

    #FINISH SELECTED TASK
    if cmd=="finish_unfinished":
        if len(args) != 0: return -1
        o=print_open_tasks(db)
        if o:
            ch=choose_interactively(o)
            if ch:
                finish(db,first(ch))

    #TASK TIME DAILY
    if cmd=="time_summary":
        if len(args) != 0: return -1
        o=print_open_tasks(db)
        if o:
            ch=choose_interactively(o)
            if ch:
                pp.pprint(task_time_billed_daily(db,first(ch)))
                raw_input("")

    #TASK TIME DAILY - LAST TASK
    if cmd=="task_time":
        if len(args) != 0: return -1
        l=print_last_task(db)
        if l:
            pp.pprint(task_time_billed_daily(db,first(l)))
            raw_input("")
        else:
            return -1
    db.commit()
    db.close()

def main():
    if len(sys.argv) > 1:
        if len(sys.argv) > 2:
            run_command(sys.argv[1],sys.argv[2:])
        else:
            run_command(sys.argv[1])
    

if __name__=="__main__":
    main()
