#!/usr/bin/env python3
import sys,os

INTERACTIVE = True

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def log(message):
    print(message)
    sys.stdout.flush()

def step(description):
    log(bcolors.OKBLUE + f"========={description}==========" + bcolors.ENDC)

def report(message):
    log(bcolors.BOLD + message + bcolors.ENDC)    

def error(message):
    log(bcolors.FAIL + message + bcolors.ENDC)    
    raise Exception(message)

def would_you_like_to_continue(message):
    if not INTERACTIVE:
        return
    report(message + ". Would you like to continue (y/n):")    
    result = sys.stdin.readline()     
    if result.strip() != "y":
        sys.exit(0)

def execute_command(command):
    log(command)    
    result = os.system(command)
    if (result != 0):
        error(f"Failed while trying to execute: '{command}'")
