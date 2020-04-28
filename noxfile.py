import nox


@nox.session(python=["3.6", "3.7", "3.8", "3.9"])
def tests(session):
    session.install(".[test]")
    session.run("pytest")


@nox.session
def format(session):
    session.install("black")
    session.run("black", "--target-version=py37", ".")


@nox.session
def lint(session):
    session.install("flake8")
    session.run("flake8")
