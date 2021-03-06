#!/usr/bin/env python
# -*- coding: utf-8 -*-

# <bitbar.title>Gitlab CI</bitbar.title>
# <bitbar.desc>Shows currently running pipelines from your GitLab in your bar. Interested in more advanced GitLab bar integration? Let me know (martin@kluska.cz). This implementation is just quick solution.</bitbar.desc>
# <bitbar.version>v0.21</bitbar.version>
# <bitbar.author>Martin Kluska</bitbar.author>
# <bitbar.author.github>pionl</bitbar.author.github>
# <bitbar.dependencies>python</bitbar.dependencies>
# <bitbar.image>https://raw.githubusercontent.com/pionl/bitbar-gitlab-ci/master/gitlab_ci.png</bitbar.image>
# <bitbar.abouturl>https://github.com/pionl/bitbar-gitlab-ci</bitbar.abouturl>
#

import json
import datetime

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen


INSTANCES = [
    {
        # Your private key for accessing gitlab: User -> Settings -> Access tokens -> add personal access token with api scope
        'privateToken': 'token',
        # Gitlab URL
        'url': 'https://gitlab.example.com',
        # Define your server and projects (name: id)
        # To get id go to project -> Settings -> General -> General project settings
        'projects': {
            "React": 3,
        },
    },
]

pipelines = []

# Converts the gitlab status to emoji
def stateIcon(status):
    return {
        "created": "💤",
        "pending": "💤",
        "running": "🚀",
        "failed": "❗",
        "success": "✔️",
        "skipped": "🚀",
        "manual": "💤"
    }[status]

# Calls gitlab API endpoint with private_token
def api (instance, method):
    url = instance['url'] + "/api/v4/" + method
    param = 'private_token=' + instance['privateToken']
    # Detect if method has query string (we need to append private token)
    url = url + (('&') if "?" in url else ('?')) + param
    body = urlopen(url).read()
    return json.loads(body.decode('utf-8'))

# Project details
class Project:
    def __init__ (self, name, id):
        self.name = name
        self.id = id

# Pipile job
class Job:
    def __init__ (self, json):
        self.name = json["stage"] + (": " + json["name"] if json["name"] != json["stage"] else "" )
        self.status = json["status"]
        self.duration = 0 if json["duration"] is None or self.status == 'running' else int(json["duration"])
        self.commitTitle = json['commit']['title']
        self.commitAuthor = json['commit']['author_email']
        self.url = json['web_url']

    # Jobs name with duration
    def displayName(self):
        return self.name + (' ' + str(self.duration) + 's' if self.duration > 0 else '')

# Pipile
class Pipeline:
    def __init__ (self, projectName, projectId, json):
        self.project = Project(projectName, projectId)
        self.id = json["id"]
        self.jobs = []
        self.runningJobs = []
        self.sha = str(json["sha"])
        self.ref = str(json["ref"])
        self.commitTitle = None
        self.commitAuthor = None

    # Display name with current running jobs
    def displayName(self):
        jobsString = '💤'

        # Get running jobs and append the name
        if len(self.runningJobs) > 0:
            strings = []
            for job in self.runningJobs:
                strings.append(job.displayName())

            jobsString = ', '.join(strings)

        return self.project.name + ' - ' + self.ref + ' (' + jobsString + ')'

    # Add jobs array json
    def addJobs(self, jobsArray):
        for jobJson in jobsArray:
            # Parse the job
            job = Job(jobJson)
            # Add the jobs array
            self.jobs.append(job)

            # Get the commit from the first job
            if self.commitTitle is None:
                self.commitTitle = job.commitTitle
            if self.commitAuthor is None:
                self.commitAuthor = job.commitAuthor

            # Check if the job is running for running jobs array
            if job.status == 'running':
                self.runningJobs.append(job)

        # first jobs on top
        self.jobs.sort(key=lambda job: job.status, reverse=True)

# class Commit:
#     def __init__(self, json)
#         self.id = json["id"]
#         self.authorEmail = json["author_email"]

# some pipelines get stuck in running state; show only last week
today = datetime.date.today()
lastWeek = today - datetime.timedelta(days=7)

# Loop the projects and get thy jobs
<<<<<<< HEAD
for instance in INSTANCES:
    for name, project in instance['projects'].iteritems():
        runningPipelines = api(instance, "projects/"+str(project)+"/pipelines?scope=running&per_page=100&updated_after="+lastWeek.isoformat())

        for pipelineJson in runningPipelines:
            pipeline = Pipeline(name, project, pipelineJson)
            # commit = Commit(api("projects/"+str(project)+"/repository/commits/"+str(pipeline.id)+"/jobs?per_page=100"))
            jobsArray = api("projects/"+str(project)+"/pipelines/"+str(pipeline.id)+"/jobs?per_page=100&sort=desc&order_by=id")
            if jobsArray.count > 0:
                # TODO: https://docs.gitlab.com/ee/api/jobs.html#get-a-log-file
                pipeline.addJobs(jobsArray)
                pipelines.append(pipeline)

pipelineCount = len(pipelines)
if pipelineCount == 0:
    print "💤"
    exit

# Mini-UI
# print 'CI'
# print '---'

myPipelines = [p for p in pipelines if p.commitAuthor == 'me@tomasr.com']
otherPipelines = [p for p in pipelines if p not in myPipelines]

# TODO: loop only mine?
## Render the pipelines names (bitbar will loop)
for index, pipeline in enumerate(myPipelines):
    print '🚀 ',

    if pipelineCount > 1:
        print str(index + 1) + '/' + str(pipelineCount) + ' ',

    print pipeline.displayName()

if not len(myPipelines):
    print 'CI'

## Start menu
print "---"

def printPipelines(pipelines):
    for pipeline in pipelines:
        print '🚀 ' + pipeline.project.name + ' - ' + pipeline.ref #+ '| color=black'
        print '-- commit: ' + pipeline.commitTitle #+ '| color=black'
        print '-- author: ' + pipeline.commitAuthor
        print '---'
        for job in pipeline.jobs:
            print stateIcon(job.status) + " ",

            style = ''
            if job.status == 'success':
                style = '| color=green'
            elif job.status == 'running':
                style = '| color=blue'

            menu = "\n-- Open on web | href=%s" % job.url

            print job.displayName() + style + menu

if len(myPipelines):
    print 'My pipelines:'
    print '---'
    printPipelines(myPipelines)
else:
    print "You don't have any running pipelines"
    print '---'

if len(otherPipelines):
    print 'Other pipelines:'
    print '---'
    printPipelines(otherPipelines)

print '---'
print 'Update now | refresh=true'
