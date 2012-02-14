import operator

def msg_rank(nick):
  
  loglines = [line for line in open('log')]
  
  names = [line.split(":::::")[0] for line in loglines]

  freqdist = {}
  
  for name in names:
    if name not in freqdist.keys():
        freqdist[name] = 1
    else:
        freqdist[name] += 1
  
  if nick not in freqdist.keys():
    return 'I have no records of that user.'
  else:
    return nick + ' has ' + str(freqdist[nick]) + ' messages in the log.'

def globals():  
    
    loglines = [line for line in open('log')]
  
    names = [line.split(":::::")[0] for line in loglines]
    freqdist = {}
  
    for name in names:
        if name not in freqdist.keys():
            freqdist[name] = 1
        else:
            freqdist[name] += 1
  
    return sorted(freqdist.iteritems(), key=operator.itemgetter(1))
  

if __name__ == "__main__":
  print msg_rank('emanuel')
  
  for a, b in reversed(globals()):
    print a, b