# PayPlanner

Django budget tracking application

## Setup

###Clone Repo in Virtual Environment
```
git clone https://github.com/payplanners/greenprint.git
pip install -r requirements.txt
```

###Set up Database
```
python manage.py makemigrations payplanner
python manage.py migrate
python manage.py loaddata payplanner/fixtures/init_user.json
python manage.py loaddata payplanner/fixtures/init_payplanner.json
```


## Contributing

Push commits to own forked repo, then submit PR. 
