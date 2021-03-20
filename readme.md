# Dead simple `bulk_update` challenge

### Requirements
`pip install -r reqs.txt`

### Start up project
`python manage.py migrate`

### Filling in the initial data 
`python manage.py bulk_create`

### Run `bulk_update` by Django ORM QuerySet
`python manage.py bulk_update`

### Run data update by raw SQL query
`python manage.py bulk_update -q`

## My results
My local DB is dockerised PostgreSQL v 10
```
by bulk_update
>> 18.606669 seconds
```
```
by query
>> 5.477139 seconds
```
**x3.4 performance improvement**