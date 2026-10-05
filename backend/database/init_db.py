import os
import sys

# Add parent directory to path to allow importing from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database.models import db, Component, ConnectionRule

def init_database():
    with app.app_context():
        # Create all tables
        db.create_all()

        # Seed components
        components_data = [
            # Basic
            {'name': 'Battery', 'category': 'Basic', 'default_value': '9', 'unit': 'V', 'description': 'DC Power Source', 'pin_configuration': '2 pins (+, -)', 'component_type': 'Power', 'simulation_model': 'V_DC'},
            {'name': 'DC Voltage Source', 'category': 'Basic', 'default_value': '5', 'unit': 'V', 'description': 'Ideal DC Voltage Source', 'pin_configuration': '2 pins (+, -)', 'component_type': 'Power', 'simulation_model': 'V_DC'},
            {'name': 'Ground', 'category': 'Basic', 'default_value': '0', 'unit': 'V', 'description': 'Reference point for the circuit', 'pin_configuration': '1 pin', 'component_type': 'Reference', 'simulation_model': 'GND'},
            
            # Passive
            {'name': 'Resistor', 'category': 'Passive', 'default_value': '1k', 'unit': 'Ohm', 'description': 'Resists the flow of electrical current', 'pin_configuration': '2 pins', 'component_type': 'Passive', 'simulation_model': 'R'},
            {'name': 'Capacitor', 'category': 'Passive', 'default_value': '10u', 'unit': 'F', 'description': 'Stores electrical energy', 'pin_configuration': '2 pins', 'component_type': 'Passive', 'simulation_model': 'C'},
            {'name': 'Inductor', 'category': 'Passive', 'default_value': '1m', 'unit': 'H', 'description': 'Stores energy in a magnetic field', 'pin_configuration': '2 pins', 'component_type': 'Passive', 'simulation_model': 'L'},
            {'name': 'Potentiometer', 'category': 'Passive', 'default_value': '10k', 'unit': 'Ohm', 'description': 'Variable resistor', 'pin_configuration': '3 pins', 'component_type': 'Passive', 'simulation_model': 'POT'},
            
            # Diodes
            {'name': 'LED', 'category': 'Diodes', 'default_value': '2V', 'unit': 'V', 'description': 'Light Emitting Diode', 'pin_configuration': '2 pins (Anode, Cathode)', 'component_type': 'Semiconductor', 'simulation_model': 'D_LED'},
            {'name': 'Diode', 'category': 'Diodes', 'default_value': '0.7V', 'unit': 'V', 'description': 'Allows current to flow in one direction', 'pin_configuration': '2 pins (Anode, Cathode)', 'component_type': 'Semiconductor', 'simulation_model': 'D'},
            {'name': 'Zener Diode', 'category': 'Diodes', 'default_value': '5.1V', 'unit': 'V', 'description': 'Allows current to flow backwards when breakdown voltage is reached', 'pin_configuration': '2 pins (Anode, Cathode)', 'component_type': 'Semiconductor', 'simulation_model': 'D_ZENER'},
            
            # Switches
            {'name': 'Switch', 'category': 'Switches', 'default_value': 'SPST', 'unit': '', 'description': 'Single Pole Single Throw Switch', 'pin_configuration': '2 pins', 'component_type': 'Electromechanical', 'simulation_model': 'SW'},
            {'name': 'Push Button', 'category': 'Switches', 'default_value': 'NO', 'unit': '', 'description': 'Normally Open Push Button', 'pin_configuration': '2 pins', 'component_type': 'Electromechanical', 'simulation_model': 'SW_PB'},
            
            # Transistors
            {'name': 'NPN Transistor', 'category': 'Transistors', 'default_value': '2N3904', 'unit': '', 'description': 'Bipolar Junction Transistor NPN', 'pin_configuration': '3 pins (Collector, Base, Emitter)', 'component_type': 'Semiconductor', 'simulation_model': 'Q_NPN'},
            {'name': 'PNP Transistor', 'category': 'Transistors', 'default_value': '2N3906', 'unit': '', 'description': 'Bipolar Junction Transistor PNP', 'pin_configuration': '3 pins (Collector, Base, Emitter)', 'component_type': 'Semiconductor', 'simulation_model': 'Q_PNP'},
            
            # Output
            {'name': 'Lamp', 'category': 'Output', 'default_value': '12V', 'unit': 'V', 'description': 'Incandescent light bulb', 'pin_configuration': '2 pins', 'component_type': 'Output', 'simulation_model': 'LAMP'},
            {'name': 'Buzzer', 'category': 'Output', 'default_value': '5V', 'unit': 'V', 'description': 'Piezoelectric buzzer', 'pin_configuration': '2 pins', 'component_type': 'Output', 'simulation_model': 'BUZZER'},
            {'name': 'Motor', 'category': 'Output', 'default_value': 'DC', 'unit': '', 'description': 'DC Motor', 'pin_configuration': '2 pins', 'component_type': 'Output', 'simulation_model': 'MOTOR_DC'}
        ]
        
        print(f"Seeding {len(components_data)} components...")
        components_added = 0
        for comp_data in components_data:
            existing = Component.query.filter_by(name=comp_data['name']).first()
            if not existing:
                comp = Component(**comp_data)
                db.session.add(comp)
                components_added += 1
                
        # Seed Connection Rules
        rules_data = [
            {'source': 'Battery', 'target': 'Resistor', 'message': 'Ensure resistor power rating is sufficient for the battery voltage.'},
            {'source': 'Resistor', 'target': 'LED', 'message': 'Resistor should be calculated to limit LED current.'},
            {'source': 'LED', 'target': 'Ground', 'message': 'Valid ground connection for LED cathode.'},
            {'source': 'Battery', 'target': 'Switch', 'message': 'Valid power to switch connection.'},
            {'source': 'Switch', 'target': 'Resistor', 'message': 'Valid switched current flow to resistor.'},
            {'source': 'Resistor', 'target': 'Ground', 'message': 'Valid path to ground.'},
            {'source': 'Battery', 'target': 'Motor', 'message': 'Consider adding a flyback diode for the motor.'},
            {'source': 'Battery', 'target': 'Buzzer', 'message': 'Check buzzer voltage rating.'}
        ]
        
        print(f"Seeding {len(rules_data)} connection rules...")
        rules_added = 0
        for rule in rules_data:
            existing = ConnectionRule.query.filter_by(source_component=rule['source'], target_component=rule['target']).first()
            if not existing:
                new_rule = ConnectionRule(
                    source_component=rule['source'],
                    target_component=rule['target'],
                    validation_message=rule['message']
                )
                db.session.add(new_rule)
                rules_added += 1
                
        # Seed Component Pins
        expected_pins = {
            'Battery': ['positive', 'negative'],
            'DC Voltage Source': ['positive', 'negative'],
            'Resistor': ['pin1', 'pin2'],
            'Potentiometer': ['pin1', 'pin2', 'wiper'],
            'Ground': ['pin1'],
            'LED': ['anode', 'cathode'],
            'Diode': ['anode', 'cathode'],
            'Zener Diode': ['anode', 'cathode'],
            'Switch': ['pin1', 'pin2'],
            'Push Button': ['pin1', 'pin2'],
            'Capacitor': ['positive', 'negative'],
            'NPN Transistor': ['base', 'collector', 'emitter'],
            'PNP Transistor': ['base', 'collector', 'emitter'],
            'Inductor': ['pin1', 'pin2'],
            'Lamp': ['pin1', 'pin2'],
            'Buzzer': ['positive', 'negative'],
            'Motor': ['positive', 'negative']
        }
        from database.models import ComponentPin
        
        print(f"Seeding component pins...")
        pins_added = 0
        for comp_name, pins in expected_pins.items():
            comp = Component.query.filter_by(name=comp_name).first()
            if comp:
                for i, pin_name in enumerate(pins):
                    existing_pin = ComponentPin.query.filter_by(component_id=comp.id, pin_name=pin_name).first()
                    if not existing_pin:
                        new_pin = ComponentPin(
                            component_id=comp.id,
                            pin_number=i+1,
                            pin_name=pin_name
                        )
                        db.session.add(new_pin)
                        pins_added += 1
                        
        db.session.commit()
        print(f"Done. Added {components_added} components, {rules_added} rules, and {pins_added} pins.")

if __name__ == '__main__':
    init_database()
