from flask import Blueprint, request, jsonify
from services.ai_service import AIService
from database.models import Component

prompt_bp = Blueprint('prompt', __name__)



@prompt_bp.route('/api/prompt/generate', methods=['POST'])
def generate_circuit():
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        
        if not prompt or not prompt.strip():
            return jsonify({"success": False, "error": "Please describe the circuit you want to create."}), 400
            
        components_db = Component.query.all()
        component_list = [c.to_dict() for c in components_db]
        
        # If DB is empty, provide hardcoded defaults for now so AI can work
        if not component_list:
            component_list = [
                {"name": "Battery", "pin_configuration": "positive, negative"},
                {"name": "Resistor", "pin_configuration": "pin1, pin2"},
                {"name": "LED", "pin_configuration": "anode, cathode"},
                {"name": "Push Button", "pin_configuration": "pin1, pin2"},
                {"name": "Ground", "pin_configuration": "pin1"}
            ]
            
        result = AIService.generate_circuit(prompt, component_list)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Internal server error: {str(e)}"}), 500
