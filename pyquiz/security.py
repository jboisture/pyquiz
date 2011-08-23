USERS = {'student':'password',
          'teacher':'password',
          'teacher2':'password'}
GROUPS = {'teacher':['group:teachers']}

def groupfinder(userid, request):
    if userid in USERS:
        return GROUPS.get(userid, [])
        
#Does this file actually do anything? Can we depreceate this?
