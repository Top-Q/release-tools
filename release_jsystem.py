#!/usr/bin/env python
import os,sys,re,shutil
from common import *

################# Config ##################

DEBUG = False

################# Infra ###################


def print_usage():
	log("./release.py NEW_RELEASE_VERSION NEW_SNAPSHOT_VERSION")
	log("Example:\n ./release.py 6.2.00 6.3.00-SNAPSHOT ")	


def getParameters(sys):
	new_release_version = sys.argv[1]
	new_snapshot_version = sys.argv[2]
	if "SNAPSHOT" not in new_snapshot_version:
		error("New snapshot version should include suffix -SNAPSHOT")	
	log("New release version: " + new_release_version)
	log("New snapshot version: " + new_snapshot_version)
	return new_release_version,new_snapshot_version

################ GIT ####################

def clone():
	step("Clonning JSystem from the repository")
	if os.path.isdir("jsystem"):
		report("Found old JSystem repository folder. deleting")
		execute_command("rm -rf jsystem")
	os.mkdir("jsystem")
	os.chdir("jsystem")	
	log("Clonning JSystem repository")
	execute_command("git clone git@github.com:Top-Q/jsystem.git")

def push():
	would_you_like_to_continue("About to push version to remote repository")
	step("Pushing changes to remote repository")
	if DEBUG:
		return
	execute_command("git push origin")
	execute_command("git push origin --tags")

def tag(new_version):
	step("Creating tag for version")
	execute_command("git tag -a "+new_version+" -m \"Releasing version "+new_version+"\"")

def commit(message):
	step("Commiting with message '" + message + "'")
	execute_command("git commit -am \""+message+"\"")

################ Maven ####################

def deploy():
	would_you_like_to_continue("About to deploy artifacts")
	step("Deploying artifacts")		
	if DEBUG:
		return
	execute_command("mvn clean deploy -f jsystem-parent/pom.xml -DskipTests=true -P dist")
	

def build():
	step("Building JSystem version")
	execute_command("mvn clean install -f jsystem-parent/pom.xml -DskipTests=true -P dist")

def set_version(old_version,new_version):
	replace_versions_in_poms(old_version,new_version)

def assert_no_snapshots():
	""" We can not relase a version if it is dependent on SNAPSHOT versions """

	step("Checking for no snapshot version in POM files")
	for dname, dirs, files in os.walk("."):
		for fname in files:
			if fname != "pom.xml":
				continue
			fpath = os.path.join(dname, fname)
			log("Looking for SNAPSHOT dependency in " + fpath)			
			with open(fpath) as f:
				s = f.read()
				if "SNAPSHOT</version>" in s:				
					error("Found SNAPSHOT version in file: " + fpath + "\n" + s +"\n")


def find_version():
	step("Finding the current JSystem version")
	os.chdir("jsystem")	
	fname = "jsystem-parent/pom.xml"
	with open(fname) as f:
		s = f.read()
	m = re.search("<version>([\w|\.-]+)</version>",s)
	current_version = m.group(1)
	report("Current version: " + current_version) 
	return current_version

def replace_versions_in_poms(old_version,new_version):
	step("Changing version " + old_version + " to " + new_version +" in: ")
	for dname, dirs, files in os.walk("."):
	    for fname in files:
	    	if fname != "pom.xml":
	    		continue
	        fpath = os.path.join(dname, fname)
	        with open(fpath) as f:
	            s = f.read()
	        replaceStr = "<version>" + old_version + "</version>"
	        if replaceStr in s:
	        	report(fpath)
	        	s = s.replace(replaceStr, "<version>" + new_version + "</version>")
	        replaceStr = "<jsystem.version>" + old_version + "</jsystem.version>"
	        if replaceStr in s:
	        	report(fpath)
	        	s = s.replace(replaceStr, "<jsystem.version>" + new_version + "</jsystem.version>")
	        with open(fpath, "w") as f:
	            f.write(s)

#####################################


if __name__ == "__main__":
	if len(sys.argv) < 3:
		report("Not enough parametrs")
		print_usage()
		sys.exit(0)
	new_release_version, new_snapshot_version = getParameters(sys)
	clone()
	current_version = find_version()	
	set_version(current_version,new_release_version)	
	assert_no_snapshots()
	build()
	commit("Upgrading to version " + new_release_version)
	tag(new_release_version)
	push()
	deploy()
	
	set_version(new_release_version,new_snapshot_version)
	commit("Upgrading to version " + new_snapshot_version)	
	push()
	step("Finished Successfully")



