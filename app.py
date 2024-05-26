from flask import Flask, render_template

app = Flask(__name__)
app.config['DEBUG'] = True


@app.route('/')
def home():  # put application's code here
    return render_template('home.html')


@app.route('/about')
def about():
    return 'About'


if __name__ == '__main__':
    app.run(debug=True)
