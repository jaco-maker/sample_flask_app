# Flask abstracts (simplifies) web development
# render_template allows you to render html templates with specific inputs
# requests lets you extract POSTed user input via request.form['<input namer>']
# url_for allows you to change between webpages
from flask import Flask, render_template, request, url_for, escape
# this imports our own python module
from vsearch4web import Search4Letters
# this makes it easier to open and read/write to databases
from DBcm import UseDatabase

app = Flask(__name__)

# def log_request(req: 'flask_request', res: 'str') -> None:
#    with open('vsearch.log', 'a') as log:
#        print(req, res, file = log)

app.config['dbconfig'] = {'host': '127.0.0.1',
                          'user': 'vsearch',
                          'password': 'pw',
                          'database': 'vsearchlogDB',}

def log_request(req: 'flask_request', res: 'str') -> None:
    """Log data onto MySQL database"""
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """ insert into log
                (phrase, letters, confidence, results)
                values
                (%s, %s, %s, %s)"""
        cursor.execute(_SQL, (req.form['phrase'],
                            req.form['letters'],
                            req.form['confidence'],
                            res,))
                            
# this page just provides a rendering of the data stored in the database
@app.route('/viewlog')
def view_the_log() -> 'html':
    """Display the contents of the log file as a HTML"""
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """select phrase, letters, confidence, results
                  from log"""
        cursor.execute(_SQL)
        contents = cursor.fetchall()
        titles = ('Phrase', 'Letters', 'Confidence', 'Results')
        return render_template('viewlog.html',
                               the_title = 'View Log',
                               the_row_titles = titles,
                               the_data = contents,)

# POST must be included if you wish to recieve user input on the page
# app.route() is a function decorator, in this case it converts a function into a webpage 
@app.route("/search4", methods = ['POST'])
def do_search() -> str:
    user_input_phrase = request.form['phrase']
    user_input_letters = request.form['letters']
    user_input_slider = request.form['confidence']
    function_results = str(Search4Letters(phrase = user_input_phrase, letters = user_input_letters))
    log_request(req = request, res = function_results)
    return render_template('requests.html',
                          the_title = 'Your Results',
                          the_letters = user_input_letters,
                          the_phrase = user_input_phrase,
                          the_conf = user_input_slider,
                          the_results = function_results)

@app.route("/")
def entry_page() -> 'html':
    return render_template('entry.html', the_title = 'Welcome to Search4Letters Webapp')

if __name__ == "__main__":
    app.run(debug = True)