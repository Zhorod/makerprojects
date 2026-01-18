import datetime


one_time = datetime.datetime.now()
print(one_time)
two_time = one_time + datetime.timedelta(hours=6)
print(two_time)

if one_time < two_time:
	print("yes")
else:
	print("no")

