import os
from flask import current_app, jsonify, url_for
from app import create_app, db
from app.database import create_db
from flask_migrate import Migrate, upgrade
from app.models import User, UserInfo, Comment, Article


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.cli.command()
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command()
def urls2():
    '''return a json list of api endpoints'''
    urls = {}
    for rule in current_app.url_map.iter_rules():
        if rule.endpoint is not 'static' and rule.endpoint.startswith('api.'):
            options = {}
            for arg in rule.arguments:
                options[arg] = "[{0}]".format(arg)

            urls[rule.endpoint] = {
                'methods': ','.join(rule.methods),
                'url': url_for(rule.endpoint, **options)
            }
    return jsonify(urls)


@app.cli.command()
def urls(rule_filter=None):
    rule_filter = rule_filter or (lambda rule: True)
    app_rules = [
        rule.rule for rule in current_app.url_map.iter_rules()
        if rule_filter(rule)
    ]
    print(app_rules)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, UserInfo=UserInfo, Article=Article, Comment=Comment)


with app.app_context():
    create_db()

if __name__ == '__main__':
    app.run()
