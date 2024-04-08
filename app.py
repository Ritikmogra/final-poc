from flask import Flask, jsonify
from abc_1 import app
from models import db
from user_routes import user_blueprint
from admin_routes import admin_blueprint




app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost:5432/ecommerce_pg' 
db.init_app(app)



app.register_blueprint(user_blueprint,url_prefix='/user')
app.register_blueprint(admin_blueprint,url_prefix='/admin')



@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404


with app.app_context():
    db.create_all() 
    db.session.commit()
if __name__ == "__main__":
    app.run(debug=True)