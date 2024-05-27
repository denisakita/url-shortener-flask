import json

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.config['DEBUG'] = True


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/your-url', methods=['GET', 'POST'])
def your_url():
    if request.method == 'POST':
        urls = {request.form['code']: {'url': request.form['url']}}
        with open('urls.json', 'w') as urls_file:
            json.dump(urls, urls_file)
        return render_template('your_url.html', code=request.form['code'])
    else:
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
