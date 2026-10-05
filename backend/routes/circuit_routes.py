from flask import Blueprint, request, jsonify
from services.validation_service import ValidationService

circuit_bp = Blueprint('circuit', __name__)

@circuit_bp.route('/api/circuit/validate', methods=['POST'])
def validate_circuit():
    try:
        circuit_data = request.get_json()
        if not circuit_data or not isinstance(circuit_data, dict):
            return jsonify({"error": "Malformed request data"}), 400
            
        if 'components' not in circuit_data or 'connections' not in circuit_data:
            return jsonify({"error": "Missing components or connections"}), 400
            
        result = ValidationService.validate_circuit(circuit_data)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
