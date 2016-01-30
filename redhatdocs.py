#!/usr/bin/python

#import httplib
#import urllib

#import kerberos
import requests
import re
#import io
import sys
import os
import pprint
import json
from optparse import OptionParser

def getCatagories(json):
	cats=json['metadata']['category']
	return [i['title'] for i in cats]


#allurls={"openstack": "https://access.redhat.com/documentation/en/red-hat-enterprise-linux-openstack-platform",
#		"storage": "https://access.redhat.com/documentation/en/red-hat-storage",
#		"satellite": "https://access.redhat.com/documentation/en/red-hat-satellite",
#		"openshift": "https://access.redhat.com/documentation/en/openshift-enterprise",
#		"rhel": "https://access.redhat.com/documentation/en/red-hat-enterprise-linux",
#		}
allurls=dict()
doctype="PDF"

parser = OptionParser()
parser.add_option("-d", "--doctype", default="PDF", dest="doctype", help='type of doc to download (default PDF)')
parser.add_option("-s", "--section", action="append", default=[], dest="section", help='section to download (default all)')
parser.add_option("-p", "--product", action="append", default=None, dest="products", help='product to download (default all)')
parser.add_option("-f", "--force", action="store_true", dest="force", help='redownload all files even if they already exist')
parser.add_option("-l", "--list", action="store_true", dest="list", help='display availble downloads')
parser.add_option("-o", "--outdir", action="store", default=".", dest="outdir", help='directory to write to')

(opt,args) = parser.parse_args()
doctype = opt.doctype 
outputdir = opt.outdir 

if opt.products: 
	products = opt.products
else:
	products = allurls.keys()


s = requests.Session()
site="https://access.redhat.com"
path="/documentation/en/"

r = s.get(site+path, headers="", verify=True)
urls=re.findall("href=\"(.*?)\"",r.text)
for u in urls:
	m=re.match("^"+path+"(.*)",u)
	if m != None:
		allurls[m.group(1)]=site+u
		#print m.group(1) +"  "+site+u

if opt.products==None and opt.list:
	i=0
	print "available products:"
	for a in allurls.keys():
		if i==1:
			print " %-70s"%a
			i=0
		else:
			print " %-70s"%a,
			i+=1

	#print "  ".join(allurls.keys())
#print allurls
	sys.exit(0)


for product in products:
	url=allurls[product]

	r = s.get(url, headers="", verify=True)
	#print url
	#sys.stderr.write(" %s\n"%r.status_code)

	data=re.search(" +allTheData =(.*?)\<\/script\>",r.text)
	jsondocs=json.loads(data.group(1))
	#print pprint.pprint(jsondocs)
	#sys.exit(0)
	#getCatagories(jsondocs)
	docs=jsondocs["docs"]

	version=0.0
	for i in jsondocs['metadata']['version']:
		if float(i) > version:
			version=float(i)

	if opt.section==[]:
		sections=getCatagories(jsondocs)
	else:
		sections=opt.section


	if opt.list:
		print "Sections available for %s:"%product
		for i in sections:
			print "  \"%s\""%i
		continue
	#print product
	#print sections
	#sys.exit(0)

	
	if url[-1]=="/":
		dirname=url.split("/")[-2]
	else:
		dirname=url.split("/")[-1]

	try:
	    os.makedirs(dirname)
	except OSError:
	    if not os.path.isdir(dirname):
	        raise

	for doc in docs:
		if doc['category'] not in sections:
			continue

		#if doc['version']!= str(version):
		if float(doc['version'])!= version:
			#print "version="+doc['version']+"!="+str(version)
			continue

		try:
			os.makedirs(dirname+"/"+doc['category'])
		except OSError:
			if not os.path.isdir(dirname+"/"+doc['category']):
				raise

		try:
			docurl=doc['formats'][doctype]		
		except KeyError:
			print "\"%s\" not available as %s"%(doc['title'],doctype)
			continue
		filename = outputdir +"/"+ dirname +"/"+ doc['category'] +"/"+ docurl.split("/")[-1]

		if not opt.force and  os.path.isfile(filename):
			print " %s already exists"%filename
			continue
	
		print " downloading %s"%filename
		result = s.get(docurl, headers="", verify=True)
		fd = open(filename,"wb")
		fd.write(result.content)
		fd.close()


sys.exit()
