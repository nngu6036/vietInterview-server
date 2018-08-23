from career_api import app
from flask_cors  import CORS


app.config['DEBUG'] = True
CORS(app)
app.run(host='0.0.0.0', port=4000)
