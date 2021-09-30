# Simple blog/forum with Flask framework

Deployed here:
https://shrekoblog.herokuapp.com/

## Lanuch locally

    $ git clone https://github.com/QQmberling/blog.git
	create .env in root folder and set SECRET_KEY and ADMIN_PSW variables
	run main.py

## Heroku way:
    install heroku CLI from offical website https://devcenter.heroku.com/articles/heroku-cli
## Lanuch locally with heroku on Windows
	$ heroku local web -f Procfile.windows
## Lanuch locally with heroku on Linux
	$ heroku local -f Procfile
## Lanuch with heroku hosting
	$ git clone https://github.com/QQmberling/blog.git
	make your own repo and push everything
	$ heroku login
	$ heroku apps:create app_name
	$ git push heroku master
####Also there is an option to create and launch app exactly from website by href of your repo.

###End
