from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Component(db.Model):
    __tablename__ = 'components'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    symbol_data = db.Column(db.Text, nullable=True)
    default_value = db.Column(db.String(100), nullable=True)
    unit = db.Column(db.String(50), nullable=True)
    pin_configuration = db.Column(db.String(100), nullable=True)
    component_type = db.Column(db.String(100), nullable=True)
    simulation_model = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    min_value = db.Column(db.String(100), nullable=True)
    max_value = db.Column(db.String(100), nullable=True)
    pins = db.relationship('ComponentPin', backref='component', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'symbol_data': self.symbol_data,
            'default_value': self.default_value,
            'unit': self.unit,
            'pin_configuration': self.pin_configuration,
            'component_type': self.component_type,
            'simulation_model': self.simulation_model,
            'description': self.description,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'pins': [{'pin_number': p.pin_number, 'pin_name': p.pin_name, 'pin_type': p.pin_type} for p in self.pins]
        }

class ComponentPin(db.Model):
    __tablename__ = 'component_pins'
    id = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.Integer, db.ForeignKey('components.id'), nullable=False)
    pin_number = db.Column(db.Integer, nullable=False)
    pin_name = db.Column(db.String(100), nullable=False)
    pin_type = db.Column(db.String(50), nullable=True)
    position_x = db.Column(db.Float, nullable=True)
    position_y = db.Column(db.Float, nullable=True)

class ConnectionRule(db.Model):
    __tablename__ = 'connection_rules'
    id = db.Column(db.Integer, primary_key=True)
    source_component = db.Column(db.String(100), nullable=False)
    target_component = db.Column(db.String(100), nullable=False)
    allowed_topology = db.Column(db.String(100), nullable=True)
    design_constraint = db.Column(db.Text, nullable=True)
    validation_message = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'source_component': self.source_component,
            'target_component': self.target_component,
            'allowed_topology': self.allowed_topology,
            'design_constraint': self.design_constraint,
            'validation_message': self.validation_message
        }

class PromptHistory(db.Model):
    __tablename__ = 'prompt_history'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    raw_text = db.Column(db.Text, nullable=False)
    extracted_components_json = db.Column(db.Text, nullable=True)
    generated_schematic_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
