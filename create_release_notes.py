#!/usr/bin/env python

import sys
import json
import urllib2
from common import *

class Issue(object):
	def __init__(self,json):
		self.number = json["number"]
		self.title = json["title"]
		self.url = json["url"]
		self.state = json["state"]
		self.labels = []
		for label in json["labels"]:
			self.labels.append(label["name"])

def get_parameters(sys):
	step(sys._getframe().f_code.co_name)
	owner = sys.argv[1]
	repository = sys.argv[2]
	milestone = sys.argv[3]
	log("Owner selected: " + owner)
	log("Repository selected: " + repository)
	log("Milestone selected: " + milestone)
	
	return owner,repository,milestone


def get_milestone_number(owner,repository,milestone_title):
	step(sys._getframe().f_code.co_name)
	url = "https://api.github.com/repos/"+owner+"/"+repository+"/milestones?state=all"
	result = json.load(urllib2.urlopen(url))
	for milestone in result:
		if milestone["title"] == milestone_title:
			log("Milestone number: "+ str(milestone["number"]))
			return milestone["number"]
	error("Failed to get milestone number for milestone " + milestone_title)
	

def format_issue(owner,repository,issue):
	return "1. Issue [#"+str(issue.number)+"](https://github.com/"+owner+"/"+repository+"/issues/"+str(issue.number)+") - "+issue.title+"\n"

def get_issues_per_milestone(owner,repository,milestone_number):
	step(sys._getframe().f_code.co_name)
	url = "https://api.github.com/repos/"+owner+"/"+repository+"/issues?milestone="+str(milestone_number)+"&state=closed"
	log(url)
	result = json.load(urllib2.urlopen(url))
	issues = []
	for json_issue in result:
		issues.append(Issue(json_issue))
	return issues

def sort_issues_by_labels(issues):
	step(sys._getframe().f_code.co_name)
	bugs = []
	enhancments = []
	for issue in issues:
		if "bug" in issue.labels:
			bugs.append(issue)
		if "enhancement" in issue.labels:
			enhancments.append(issue)
	return bugs,enhancments

def sort_issues_by_number(issues):
	step(sys._getframe().f_code.co_name)
	return sorted(issues, key=lambda issue: issue.number, reverse=False)

def generate_markdown(bugs,enhancments):
	step(sys._getframe().f_code.co_name)
	md = "## New Features\n\n"
	for issue in enhancments:
		md+= format_issue(owner,repository,issue)

	md += "\n\n## Bug Fixes\n\n"
	for issue in bugs:
		md+= format_issue(owner,repository,issue)
	return md

def write_to_file(md, file_name):
	step(sys._getframe().f_code.co_name)
	log("Writing release notes to file: " + file_name)
	with open(file_name, "w") as text_file:
			text_file.write(md)

def print_usage():
	log("./release_notes.py OWNER REPOSITORY MILESTONE")
	log("\nExample:")
	log("./release_notes.py Top-Q jsystem 6.1.04")

if __name__ == "__main__":
	if len(sys.argv) < 3:
		log("Not enough parametrs")
		print_usage()
		sys.exit(0)
	
	owner,repository,milestone = get_parameters(sys)
	milestone_number = get_milestone_number(owner,repository,milestone) 
	issues = get_issues_per_milestone(owner,repository,milestone_number)
	bugs,enhancments = sort_issues_by_labels(issues)
	bugs = sort_issues_by_number(bugs)
	enhancments = sort_issues_by_number(enhancments)
	md = generate_markdown(bugs,enhancments)	
	log(md)
	write_to_file(md,"release_notes.md")
