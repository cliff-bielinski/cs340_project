from flask import Flask, render_template
import os
from dotenv import load_dotenv

# Configuration
load_dotenv()
app = Flask(__name__)

# Routes
@app.route('/')
def index():
  return render_template('index.j2')

@app.route('/species')
def species():
  return render_template('species.j2')


# Listener
if __name__ == '__main__':
  port = os.getenv("PORT")  # set port in .env file as PORT=xxxxx

  app.run(port=port, debug=True)