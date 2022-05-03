from flask import Flask, render_template
from flask_navigation import Navigation
import os

# Configuration
app = Flask(__name__)
nav = Navigation(app)

# Navigation
nav.Bar('top', [
  nav.Item('Home', 'index'),
  nav.Item('Add Species', 'species')
])

# Routes
@app.route('/')
def index():
  return render_template('index.j2')

@app.route('/species')
def species():
  return render_template('species.j2')

# Listener
if __name__ == '__main__':
  port = int(os.environ.get('PORT', 19133))

  app.run(port=port, debug=True)