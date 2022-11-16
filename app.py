import subprocess
import tempfile
import unicodedata

from flask import Flask, request
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def ssn():
    duration = True
    read_story = ''
    story = ''
    if request.method == 'POST':
        story = request.form['story']
        # Fix gremlins
        degremlin = unicodedata.normalize('NFKD', story.strip('\n').replace('“', '"').replace('”', '"').replace("’", "'").replace("‘", "'")).encode('ascii', 'ignore').decode()
        # Get time to read
        with tempfile.NamedTemporaryFile() as temp:
            temp.write(degremlin.encode('ascii', 'ignore'))
            how_long = float(subprocess.check_output('cat {} | espeak --stdout | wc --bytes'.format(temp.name), shell=True))
        minutes = how_long / 44000.0 / 60;
        duration = '%d minutes, %d seconds' % (int(minutes), int((minutes - int(minutes)) * 100 * (3/5)))
        # Prefix lines
        for line in degremlin.split('\n'):
            if len(line.strip()):
                read_story += 'st ' + line
    return '''
    <!DOCTYPE html>
    <html>
    <head>
    <title>Short Story Night!</title>
    <style>
    main {{
        max-width: 960px;
        margin: 0 auto;
        padding: 1rem;
    }}
    pre {{
        white-space: pre-wrap;
        border: 1px solid #ccc;
        background-color: #eee;
        padding: 1rem;
    }}
    form {{
        text-align: center;
    }}
    </style>
    </head>
    <body>
    <main>
    <h1>Short Story Night formatter!</h1>
    <p>De-gremlin, estimate read time, and provide the <code>st</code> commands! Just paste and click go~</p>
    <p>Ping Maddy if you run into problems.</p>
    <form method="post">
    <textarea name="story" rows="20" cols="80">{}</textarea><br>
    <input type="submit">
    </form>
    {}
    </main>
    </body>
    </html>
    '''.format(story, '''
        <pre class="result">
st >>> This story will take about {} to read
{}
        </pre>
        '''.format(duration, read_story) if read_story else '', '')


if __name__ == '__main__':
    app.run()
