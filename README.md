<h1 align='center'>
  Discord Chores Manager <br/>
</h1>

<p align='center'>
  <img src='https://github.com/agupta231/ormond-chores-bot/workflows/Build/badge.svg?branch=main'>
  </br>
  <i>A Discord bot that keeps track of and notifies roommate chore responsibilities.</i>
</p>



# Overview
This is a little Discord bot to manage the chores between a group of people. 
The bot works off of a role, where everyone with that role in the server is
in the running to be "on-call" (the responsible party).

The bot will then ping the user in a **predefined, shared** channel, reminding
them to do their chores. Note that if the channel is public, then this is a 
great way to raise awareness and accountability within the group.

## Commands
The syntax for this bot is pretty simple: and remember that invoking `!help`
will display this menu in-chat as well.

```
schedule    List the schedule for the seven days
signoff     Sign off the on-call member for today
swap        Swap on call position with chosen person
today       Return the person who is on-call today
```



# Before Running
Before the bot can run, you **need** to supply it a `.env` file for all of the
tokens and associated IDs. This can easily be done by making a copy of 
`example.env`, filling in all of the respective fields, saving it as `.env` 
**in the root directory of the project**. 

Observe that this is a mono-server bot, and the guild/channel/role IDs are
the default IDs that you would like the bot to scrape to get the member lists.



# Execution Directions
Note that this repo can automatically be run by `docker-compose` via my 
[bots](https://github.com/agupta231/bots) repo. To run just this service, you 
can either use that repo, set up a virtual environment on your local machine, or
use the included Dockerfile to install all of the dependencies.

Only the virtual environment and Docker instructions will follow. If you are
interested in using my bots repo to run it, refer to that repo.


## Virtual Environment
Firstly, ensure that you have both python 3 and the `python3.x-venv` packages 
installed. If you aren't 100% sure what that means, check out a 
[quick primer to virtual environments](https://docs.python.org/3/library/venv.html)
to get the ball rolling.

Once you have that all installed, the repo cloned, and navigated to it in a
terminal:
1. Create your virtual environment: `python3 -m venv venv-chores`
2. Source to activate your environment: `source venv-chores/bin/activate`
3. Update your environment base deps: `pip install -U wheel pip`
4. Install the project dependencies: `pip install -r requirements.txt`
5. Run the bot: `python src/bot.py`


## Docker
A simple Dockerfile is also included for your convenience. To run the service
via Docker:

1. Build the image: `docker build -t chores-discord .`
2. Run it: `docker run -v $(pwd):/proj chores-discord`

Note that you only need to build the image when you are updating the 
dependencies: other times, you can skip that step and just run the image. Also,
since the repo is being mounted, all output logs can be found in the root-level
`logs` folder.