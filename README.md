# thefinalwhistle

## github workflow
[see this stackoverflow post for some ideas](https://stackoverflow.com/questions/2428722/git-branch-strategy-for-small-dev-team)  
create a branch from develop, work on changes/features you want to make (which don't overlap too much with something which is being done in another branch) and then merge back into develop once your code is finished

## flask/sqlalchemy documentation
http://flask.pocoo.org/docs/0.12/api/  

http://flask.pocoo.org/docs/0.12/patterns/  

http://flask.pocoo.org/docs/0.12/patterns/sqlalchemy/  

http://flask-sqlalchemy.pocoo.org/2.3/quickstart/  

[stackoverflow post about timestamps and databases](https://stackoverflow.com/a/33532154)

http://flask.pocoo.org/docs/0.12/templating/  

http://jinja.pocoo.org/docs/2.10/templates/  

https://flask-wtf.readthedocs.io/en/stable/  

# Deploy app to Ubuntu 16.04 Server

Clone the repository
```
git clone https://github.com/tmoscrip/thefinalwhistle.git
```

Create python 3.6 environment
```
pyvenv-3.6 .env
```

Activate environment
```
source .env/bin/activate
```
Navigate to the folder with the setup.py
```
cd thefinalwhistle/
```
Install the finalwhistle & all remaining requirements
```
pip install -e .
pip install -r requirements.txt
```
Setup the environment
```
export FLASK_APP=finalwhistle
export FLASK_DEBUG=true
export FINALWHISTLE_SECRET_KEY=123123123123
```

**!! Make sure you are in the directory which includes the setup.py !!**

Start the application
```
flask run
```
