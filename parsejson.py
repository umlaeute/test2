#!/usr/bin/env python3

import json
from pprint import pprint
import sys
import requests
import re


def getdata(s):
    data=json.loads(sys.argv[1])
    
    if "filename" not in data:
      data["filename"] = "foobar"
    
    if "description" in data:
      data["description"] = data["description"].lstrip("```plain text").rstrip("```").replace("\\n", "\n").strip()
    
    if "image" in data:
      img = re.findall("!\[.*\]\(([^)]*)\)", data["image"])[0]
      if img.lower().endswith(".gif"):
        data["image"] = img
      else:
        del data["image"]

    return data

def makefile(filename, title="", description="", url="", **kwargs):
   data=[]
   if title:
      data.append("TITLE\t%s" % title)
   if description:
      data += ["DETAILS\t%s" % _ for _ in description.splitlines()]
   if url:
      data.append("URL\t%s" % url)
   with open("%s.txt" % filename, "w") as f:
      f.write("\n".join(data))
      f.write("\n")
      
def makeimage(filename, image="", **kwargs):
   if not image:
     return
   with requests.get(image, stream=True) as r:
        r.raise_for_status()
        with open("%s.gif" % filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk) 

data=getdata(sys.argv[1])
pprint(data)
makefile(**data)
makeimage(**data)

