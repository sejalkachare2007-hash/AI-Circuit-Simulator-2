from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config
from database.models import db, Component, ConnectionRule
from routes.circuit_routes import circuit_bp
from routes.prompt_routes import prompt_bp
import os

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')
app = Flask(__name__, static_folder=frontend_dir, static_url_path='/')

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(frontend_dir, path)):
        return app.send_static_file(path)
    return app.send_static_file('index.html')

app.config.from_object(Config)
CORS(app)
db.init_app(app)

app.register_blueprint(circuit_bp)
app.register_blueprint(prompt_bp)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route('/api/components', methods=['GET'])
def get_components():
    try:
        components = Component.query.all()
        return jsonify([c.to_dict() for c in components]), 200
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/api/components/<int:id>', methods=['GET'])
def get_component(id):
    try:
        component = Component.query.get(id)
        if component:
            return jsonify(component.to_dict()), 200
        return jsonify({"error": "Component not found"}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/api/components/category/<string:category>', methods=['GET'])
def get_components_by_category(category):
    try:
        components = Component.query.filter(Component.category.ilike(category)).all()
        return jsonify([c.to_dict() for c in components]), 200
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/api/connection-rules', methods=['GET'])
def get_connection_rules():
    try:
        rules = ConnectionRule.query.all()
        return jsonify([r.to_dict() for r in rules]), 200
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
