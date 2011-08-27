import datetime

t16=raw_input("")
t17=raw_input("")
t18=raw_input("")
n4=raw_input("")
n1=raw_input("")

if "" in [t16,t17,t18]:
	(t16,t17,t18)=(0,0,0)		

today=datetime.date.today()
friday=(today + datetime.timedelta(5-today.isoweekday())).day
if n4=="": n4=friday

if n1=="": 
	nl=[[1]*a for a in range(5,25)]
else:
	nl=[n1]

(t16,t17,t18,n4)=map(int,(t16,t17,t18,n4))
ans=map(int,[abs(round(0.5*t16+0.5*t18,0)-(n4-len(nn)*2)*(n4-len(nn)*2)+(t16-t18))+n4*5 for nn in nl])

if t17 in ans:
	print("OK")
	i=raw_input("")
else:
	print("FAIL")
	i=raw_input("")

if i: print(i)
