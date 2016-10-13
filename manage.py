from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
from app import create_app, db
import os

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage

    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

app = create_app('debug')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test(cov=False, which=None):
    if cov and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    if which:
        start_dir = 'tests.%s' % which
    else:
        start_dir = 'tests'

    tests = unittest.TestLoader().discover(start_dir, pattern='*.py')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def export_json():
    from database import export_json
    export_json.run()


@manager.command
def import_json():
    from database import import_json
    import_json.run()


if COV:
    COV.stop()
    COV.save()
    print('Coverage Summary:')
    COV.report()
    basedir = os.path.abspath(os.path.dirname(__file__))
    covdir = os.path.join(basedir, 'tmp/coverage')
    COV.html_report(directory=covdir)
    print('HTML version: file://%s/index.html' % covdir)
    COV.erase()


@manager.command
def profile(length=30, profile_dir=None):
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[
                                      length], profile_dir=profile_dir)
    app.run()


if __name__ == '__main__':
    manager.run()
