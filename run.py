from lessee import app, db
from lessee.models import populate_platforms


def init_db():
    db.create_all()
    populate_platforms()


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', debug=True)
