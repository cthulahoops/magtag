import subprocess
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    calendar = subprocess.run(["khal", "list", "now"], capture_output=True, check=True)
    return calendar.stdout.decode('utf-8').encode('ascii', 'ignore').decode('ascii')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
