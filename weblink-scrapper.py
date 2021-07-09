#Web Link Scrapper of any website (might stuck at very big website)       --- can take longer than expected (because extracting of weblink from single website takes time)

from bs4 import BeautifulSoup
import urllib.request, urllib.parse, urllib.error
from  django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import requests
from treelib import Node , Tree
webtree = Tree()
validate=URLValidator()
link="http://w3schools.com/"
root=webtree.create_node("",data=link)
p=root
q=[root]
visited=[]
while(q!=[]):
    #print("\n"+p.data)
    try:
        webpage=urllib.request.urlopen(p.data).read()
        soup = BeautifulSoup(webpage, 'html.parser')
        p.tag=soup.title.string
        visited.append(q.pop(0))
        tags=soup("a")
        for tag in tags:
            x=tag.get("href",None)
            try:
                #response = requests.get(x)
                validate(x)
                if (visited.count(x)==0):
                    l=webtree.create_node("",parent=p,data=x) 
                    q.append(l)  
            # except requests.ConnectionError as exception:
            #     print(" ")
            except ValidationError as exception:
                webtree.show()
                print("",end="")
        p=q[0]
    except:
        q.pop(0)
        p=q[0]
        webtree.show()
        print("",end="")
#webtree.show()
        
