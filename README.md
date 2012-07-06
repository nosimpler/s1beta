# Jones et al., 2009 in Python+NEURON

Some useful guidelines to using version control:
================================================
0. BEFORE working on a clean copy, check to see if there is a new revision with 'git pull'
1. BEFORE working on an unclean copy, stash changes before you check new revisions
2. TEST code to ensure that it runs on your machine (at the very least)
3. DO NOT commit binary files (such as pyc or png files) without a specific reason
4. When replacing or removing code, there are two stages. First, COMMIT the changes with old code commented out. Once that commit has been stabilized, and you're certain the code won't be useful again, it can be removed in subsequent commits.
