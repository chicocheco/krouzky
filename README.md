# vyberaktivitu.online project

Guide for deploying
___________________
## 1. Hetzner VPS
- copy public ssh key from `cat ~/.ssh/id_rsa.pub` and paste to the initial set-up page
- create an ssh shortcut `nano ~/.ssh/config` so you can `root@aktivity_server`
```
Host aktivity_server
   ForwardAgent yes
   Hostname <ip-address>
   Port 22
   ServerAliveInterval 60
   ServerAliveCountMax 60
```
- change the permissions of the config file `chmod 644 ~/.ssh/config` to fix _Bad owner or permissions_ error
- ssh in `ssh root@<ip-address>` and create another account `adduser <name>` 
   and add to sudo group `usermod -aG sudo <name>`
- install dokku using root account (use first script from https://dokku.com/)
- from the local machine allow ssh access (no pass needed) for the new account as well 
 `ssh-copy-id <name>@aktivity_server`
## 2. domain
 - point A record to the IP of the server (`vyberaktivitu.online` and `*.vyberaktivitu.online`)
## 3. dokku
 - open ip or domain address of the server in a web browser
 - set _Hostname_ to the same as your domain name you bought, so `vyberaktivitu.online`
 - check _Use virtualhost naming for apps_
 - create app `dokku apps:create vyberaktivitu`
 - download plugin for the db `sudo dokku plugin:install https://github.com/dokku/dokku-postgres.git`
 - create database and pass `DATABASE_URL` to the app
 ```bash
export POSTGRES_IMAGE="postgres"
export POSTGRES_IMAGE_VERSION="11"
sudo dokku postgres:create vyberaktivitu_db
dokku postgres:link vyberaktivitu_db vyberaktivitu
```
 - add other env. variables
```bash
dokku config:set --no-restart vyberaktivitu DJANGO_ALLOWED_HOSTS=<ip-address>,vyberaktivitu.online,www.vyberaktivitu.online
dokku config:set --no-restart vyberaktivitu DEBUG=0
dokku config:set --no-restart vyberaktivitu EMAIL_HOST=smtp.seznam.cz
dokku config:set --no-restart vyberaktivitu EMAIL_HOST_USER=info@vyberaktivitu.online
dokku config:set --no-restart vyberaktivitu EMAIL_HOST_PASSWORD=<password>
dokku config:show vyberaktivitu
```
 - add domains to the app `dokku domains:add vyberaktivitu vyberaktivitu.online wwww.vyberaktivitu.online`
 - enable SSL (https) with letsencrypt plugin for these domains
```bash
dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git
# email address for renewal warnings for your certificate
dokku config:set --no-restart --global DOKKU_LETSENCRYPT_EMAIL=stanislav.matas@gmail.com
# enable command can also be used to renew
dokku letsencrypt:enable vyberaktivitu
dokku letsencrypt:cron-job --add
```  
 - enable Django security settings by setting `ENVIRONMENT` env. variable `dokku config:set vyberaktivitu ENVIRONMENT=production`
 - do a deploy check `dokku --rm run vyberaktivitu python manage.py check --deploy` and open the website to check
 whether there are no infinite redirects
 - add and link persistent storage for media files
 ```bash
sudo mkdir -p  /var/lib/dokku/data/storage/vyberaktivitu
dokku storage:mount vyberaktivitu /var/lib/dokku/data/storage/vyberaktivitu:/app/media
sudo chown -R dokku:dokku /var/lib/dokku/data/storage/vyberaktivitu/
dokku storage:report vyberaktivitu
 ```
- create alias in nginx config to media files `sudo nano /home/dokku/vyberaktivitu/nginx.conf.d/media.conf` and add 
 the following (the config file gets included to the main config file automatically):
```
location /media {
    alias /var/lib/dokku/data/storage/vyberaktivitu;
}
```
- restart the container `dokku ps:restart vyberaktivitu`
## 4. git and deployment
- add a remote repository for dokku user `git remote add dokku dokku@aktivity_server:vyberaktivitu`
- make sure that there are the latest migration files
- make sure that `.buildpacks` consists of `https://github.com/heroku/heroku-buildpack-python.git` so it gets used instead of Dockerfile 
- make sure that `DOKKU_SCALE` consists of `web=1`
- make sure that `Procfile` consists of the following:
```
web: gunicorn config.wsgi:application

release: python manage.py migrate --noinput 
```
- make sure that `runtime.txt` consists of `python-3.9.5`
- zero downtime deploy - make sure that `CHECKS` consists of `//vyberaktivitu.online                       Vyber online aktivitu`
## 5. dokku post-deploy
- create a super user(s) `dokku --rm run vyberaktivitu python manage.py createsuperuser`
- populate a week schedule table `dokku --rm run vyberaktivitu python manage.py fill_weekschedule`
- add age categories in django admin  
- rename `example.com` to `vyberaktivitu.online` in django admin
- fix _413 Request Entity Too Large_ error `dokku nginx:set vyberaktivitu client-max-body-size 50m`
- update system `sudo apt update && sudo apt upgrade`
- having created another non-root account, disable password access to root - open `sudo nano /etc/ssh/sshd_config` and
  change `PermitRootLogin` from `yes` to `prohibit-password`
- configure firewall - allow inbound only at TCP ports 22, 80 and 443

Dependencies:
```requirements.txt
# both
crispy-bootstrap5
Django
django-allauth
django-autoslug
django-crispy-forms
django-environ
django-filter
django-taggit
django-tinymce
Pillow
psycopg2-binary
whitenoise

# only production
gunicorn

# only local
django-debug-toolbar
```