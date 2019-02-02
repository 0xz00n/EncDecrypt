#! /usr/bin/python

'''
EncDecrypt
Since I couldn't find a tool for bruting OpenSSL encrypted files.

This is a work in progress
'''

from termcolor import colored
import subprocess
import threading
import argparse
import os

# Argparse function
def get_args():
    # Assign description to the help doc
    parser = argparse.ArgumentParser(
        description='Script brute forces OpenSSL encrypted files')
    # Arguments
    parser.add_argument(
        '-e', '--encoding', type=str, help='OpenSSL encoding type', required=True)
    parser.add_argument(
        '-md', '--messagedigest', type=str, help='Set message digest type', required=False)
    parser.add_argument(
        '-l', '--wordlist', type=str, help='Specify the wordlist to use in attack', required=True)
    parser.add_argument(
        '-f', '--file', type=str, help='Specify the encrypted file to brute force', required=True)
    parser.add_argument(
        '-o', '--outfile', type=str, help='Desired name of output pass file', required=True)
    parser.add_argument(
        '-d', '--decryptfile', type=str, help='Location of decrypted file', required=True)
    parser.add_argument(
        '-s', '--startline', type=int, help='Start attack from specified line number in wordlist',
        required=false, default=1)

    # Array for all arguments passed to script
    args = parser.parse_args()

    # Assign args to variables
    enctype = args.enctype
    md = args.md
    wordlist = args.wordlist
    targfile = args.targfile
    outfile = args.outfile
    dcrypt = args.dcrypt
    startline = args.startline

    # Return all variable values
    return enctype, md, wordlist, targfile, outfile, dcrypt, startline

# A function for printing status every 10 seconds on its own thread
def statusreport():
    # Start thread for status printing.  Just need to figure out how to kill the thread later.
    # Insert condition here to prevent timer start
    threading.Timer(10.0, statusreport).start()
    print "[", colored("%i", "green") % (currentpos - 1), "/", colored("%i", "green") % wordcount, "] %s" % strippedword

# Run get_args()
get_args()

# Define additional variables
outputlist = open(outfile, "w+")
devnull = open(os.devnull, 'w')
currentpos = 1
firstrun = 0
md = '"-md" + %s' % md

# Begin reading provided wordlist
with open(wordlist, 'r') as passwords:
    # Get total lines in provided wordlist
    wordcount = len(passwords.readlines())
    for word in passwords:
        # Increment currentpos until it is greater than startline
        if startline > currentpos:
            currentpos += 1
        else:
            # Strip newline from word for use in OpenSSL command
            strippedword = word.rstrip()

            # Check if this is the first run, start the reporter thread, and prevent further exec
            if firstrun == 0:
                statusreport()
                firstrun += 1

            # Attempt to decrypt the file.
            dec = subprocess.Popen(["openssl",enctype,md,"-d","-k",strippedword,
                                    "-in",targfile,"-out",dcrypt],
                                    stderr=subprocess.PIPE,
                                    stdout=devnull)

            # Increment currentpos for execution tracking
            currentpos += 1

            # Store pipe info in output var
            output = dec.stderr.read()

            # Open dcrpyt file for reading and store in result var
            with open(dcrypt, 'r') as csvfile:
                result = csvfile.read()

            # Check if str exists in output var
            if "bad decrypt" in output:
                continue
            # Check if string exists in result var
            elif "flag" in result:
                outputlist.write(word)
                print "[", colored("*!*", "red"), "]"
                print "[", colored("*!*", "red"), "]"
                print "[", colored("*!*", "red"), "] Password found: ", colored("%s", "red") % strippedword
                print "[", colored("*!*", "red"), "] Decrypted file can be found in ", colored("result.csv", "red"), " in the directory this script was run."
                print "[", colored("*!*", "red"), "]"
                print "[", colored("*!*", "red"), "]"
                quit()
            else:
                continue
