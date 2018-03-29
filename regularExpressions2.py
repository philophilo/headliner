import re
print re.split(r'\s', 'here are some words')
print re.split(r'(\s)i', 'here are some words')
print re.split(r'(s)', 'here are some words')

#using the FLAGS I and M
#I = ignorecase
#M = Multiline

print re.split(r'[a-f][a-f]', 'kjadkjvjnfkjnjjnoejfoiqjfefn<kv',
        re.I|re.M)

print re.findall(r'\d', ocinwe324 main st.asdvce)
print re.findall(r'\d{1,5}\s\w+', 'ocinwe324 main st.asdvce')
print re.findall(r'\d{1,5}\s\w+\s\w+\.\w+', 'ocinwe324 main st.asdvce'i)

import re, urllib.request
try:
    import urllib.request
except:
    pass

sites = 'google yahoo cnn msn'.split()
pat = re.compile(r'<title>+.*</title>', re.I|re.M)

for s in sites:
    print "Searching: " + s
    try:
        u = urllib.urlopen("http://" + s +".com")
    except:
        u = urllib.request.urlopen("http://" + s +".com")
    text = u.read()
    title = re.findall(pat, str(text))
    print(title[0])
