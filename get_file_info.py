import os, time
from stat import * # ST_SIZE etc
import hashlib
from functools import partial
import sys, getopt
import webbrowser
import tempfile
  
def md5sum(filename):
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()

def main(argv):
  
   pathlist = ''
   outputfile = ''
   rootdirlist = ''   
   try:
      opts, args = getopt.getopt(argv,"hi:r:o:",["pathlist=","rootdirlist="])
   except getopt.GetoptError:
      #print 'get_file_info.py -i <path list (comma separated)> -r <rootdir list (comma separated)> -o <outputfile>'
      print 'get_file_info.py -i <path list (comma separated)> -r <rootdir list (comma separated)>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'get_file_info.py -i <path list (comma separated)> -r <rootdir list (comma separated)>'
         sys.exit()
      elif opt in ("-i", "--pathlist"):
         pathlist = arg.split(',')
      elif opt in ("-r", "--rootdirlist"):
         rootdirlist = arg.split(',')         
      #elif opt in ("-o", "--ofile"):
       #  outputfile = arg
         
   outputfile=os.path.join(tempfile.gettempdir(), 'out.html')
   print 'Path list file is "', pathlist
   print 'Rootdir list is "', rootdirlist
   print 'Output file is "', outputfile
  
   alist_filter = ['bna','mrg'] #Hardcoded filters
      	      
   with open(outputfile, 'w') as the_file:
     
    txt='<HTML>'
    txt+='<h1>Report of BNA/MRG Files</h1>'
    txt+='<p>Path List: ' + str(pathlist)
    txt+='<p>Root List: ' + str(rootdirlist)

    txt+='<h2>Complete List of BNA/MRG Files</h2>'
    txt+='<ul>'
    txt+='<li>File: filename (including asbolute path)</li>'
    txt+='<li>Size: Size on disk (in bytes)</li>'
    txt+='<li>Date: Last Modified Date</li>'
    txt+='<li>Hash1: Content Hash (for detecting duplicates)</li>'
    txt+='<li>Hash2: Relative filename Hash (for detecting false duplicates)</li>'
    txt+='</ul>'
    
    txt+='<p><table border=1><tr> <th>File</th><th>Size</th> <th>Date</th> <th>Hash1</th><th>Hash2</th></tr>'
                      
    dict1=dict()
    dict2=dict()
        
    idx=0
    for path in pathlist:
      for root, subFolders, files in os.walk(path):
	for filename in files:
	  if filename[-3:].lower() in alist_filter:#case insensitive
	  
	    #print rootdirlist[idx]
	    filePath = os.path.join(root, filename)	
	    
	    a=filePath.find(rootdirlist[idx]);
	    b=len(rootdirlist[idx])
	    filePath2 = filePath[a+b:len(filePath)]
	    
	    #print filePath	    
	    #print filePath2
	    
	    try:
	      st = os.stat(filePath)
	    except IOError:
	      print "failed to get information about", filePath
	    else:
	      
	      filename_hash=hashlib.sha224(filePath2).hexdigest()		
	      #filename_size_date_hash=hashlib.sha224(filePath2+str(st[ST_SIZE])+str(time.asctime(time.localtime(st[ST_MTIME])))).hexdigest()	
	      content_hash=md5sum(filePath)
	      	      
	      if content_hash in dict1:
		aList=dict1[content_hash]
		aList.append(filePath)
		dict1[content_hash]=aList
	      else:
		aList=[]
		aList.append(filePath)
		dict1[content_hash]=aList
		
	      if filename_hash in dict2:

		dict3=dict2[filename_hash]
		dict3[str(st[ST_SIZE])]=filePath
		
		dict2[filename_hash]=dict3
		
	      else:
		
		dict3=dict()
		dict3[str(st[ST_SIZE])]=filePath
		
		dict2[filename_hash]=dict3
	      
	      txt+='<tr>'
	      
	      #txt= '"' + filePath + '",' + str(st[ST_SIZE]) + ',' + str(time.asctime(time.localtime(st[ST_MTIME])))+ "," + content_hash + "," + filename_hash
	      
	      txt+='<td><a href=''file://' + filePath + ' target="_self" type="application/vnd.ms-excel">' + filePath + '</a></td>'
	      txt+='<td>'+str(st[ST_SIZE])+'</td>'
	      txt+='<td>'+ str(time.asctime(time.localtime(st[ST_MTIME])))+'</td>'	      
	      txt+='<td>'+ content_hash +'</td>'
	      txt+='<td>'+ filename_hash +'</td>'
	      
	      txt+='</tr>'
	    	    
      idx=idx+1

    txt+='</table>'

    print 'Real duplicates:'
    txt+='<h2>List of Duplicates</h2>'
    txt+='<p><table border=1><tr><th>Hash1</th><th>File</th></tr>'
    
    for key, value in sorted(dict1.iteritems()):
      aList=value
      if len(aList)>1:

	txt+='<tr>'	
	txt+='<td>'+ key +'</td>'
	txt+='<td>'
	for s in value:
	  txt+='<a href=''file://' + s + ' target="_self" type="application/vnd.ms-excel">' + s + '</a><br>'
	txt+='</td>'
	print key, value
	txt+='</tr>'
    
    txt+='</table>'
    
    print 'False duplicates:'
    txt+='<h2>List of \"False\" Duplicates</h2>'    
    txt+='<p><table border=1><tr><th>Hash2</th><th>File</th><th>Size</th></tr>'
    
    for key, value in sorted(dict2.iteritems()):
      aList=value
      if len(aList)>1:
	txt+='<tr>'	
	txt+='<td>'+ key +'</td>'
	
	txt+='<td>'
	for key2,value2 in value.iteritems():
	  txt+='<a href=''file://' + value2 + ' target="_self" type="application/vnd.ms-excel">' + value2 + '</a><br>'
	txt+='</td>'
	
	txt+='<td>'
	for key2,value2 in value.iteritems():
	  txt+= key2 + '<br>'
	txt+='</td>'
	
	print key, value
	txt+='</tr>'

    txt+='</table>'
    
    txt+='</HTML>'
    
    url = outputfile
    webbrowser.open_new(url)
    
    the_file.write(txt)

if __name__ == "__main__":
  main(sys.argv[1:])
