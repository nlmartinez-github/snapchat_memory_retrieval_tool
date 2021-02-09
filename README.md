# snapchat-memory-retrieval-tool
Handy dandy tool to get all of your memories from Snapchat (and fast!)

# Motivation
The purpose of this tool was less to accomplish a simple task, downloading memories off of snapchat, as it was a learning experience. I wanted all of my memories off of my Snapchat account, but also have been wanting to learn how to use multithreading/concurrency/parallelism to accomplish large tasks quicker. This tool uses a python library called `asyncio`, which is a library to write concurrent code using the async/await syntax. Read more about it here: https://docs.python.org/3/library/asyncio.html

I was able to accomplish what I wanted, and was able to download over 5000 videos (.mp4) and images (.jpg) from Snapchat's servers (hosted by AWS) in around 3-4 minutes. This was done over wired gigabit connection. The read/writes were handled by a Gen4 NVMe SSD. It was very entertaining to watch!

# **DISCLAIMER**
**WARNING**: THIS TOOL USES A LOT OF BANDWIDTH DUE TO SINGLE-THREADED CONCURRENCY. IT IS DESIGNED TO WORK EXTREMELY FAST, WHICH COMES AT A COST. DO NOT USE IF YOU ARE UNSURE OF YOUR HARDWARE & NETWORK LIMITS. THERE ARE ALTERNATIVES THAT AREN'T AS FAST BUT ALSO WON'T BE AS DEMANDING ON YOUR RESOURCES. YOU HAVE BEEN WARNED.

# Getting started
Before you even think about using this tool, you'll need to download your data from Snapchat.
<br/>See here for how to do that: https://support.snapchat.com/en-US/a/download-my-data

Once you have your data, you'll only need one file from it: `memories_history.json` 
<br/>You can find this under the json folder of your data. 

# Using the tool
*You may need to install some python libraries using `pip` or [insert other preferred way to install python librarys]*
1. Put your `memories_history.json` into this project's root folder
2. Run `snapchat-memory-retrieval-tool.py` 

<br/>That is all! Given there were no errors, all of your memories should be in a `media` folder under the project's root folder. 

ENJOY!
