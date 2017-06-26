import flask

import utils


app = flask.Flask(__name__)
db = utils.get_db_connection()


@app.route('/')
def index():
    slos = map(lambda x: (x[0], x[1], utils.is_fast_enough(x[0], x[1]),
                                x[2], utils.is_successful_enough(x[0], x[2])
                          ),
               utils.get_slos_from_db(db)
               )
    return flask.render_template('index.html', slos=slos)

if __name__ == '__main__':
    app.run()
