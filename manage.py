from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager, Shell
from app import create_app, db

app = create_app()
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def profile(length=30, profile_dir=None):
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    app.run()


if __name__ == '__main__':
    manager.run()
