import os
import requests
import json
import re
from config import Config
from services.validation_service import ValidationService

class AIService:
    @staticmethod
    def generate_circuit(prompt, component_list):
        """
        Communicates with Ollama to generate a circuit JSON from the user prompt.
        Validates the structure and components against the DB.
        """
        base_url = Config.OLLAMA_BASE_URL
        model = Config.OLLAMA_MODEL
        
        from database.models import ComponentPin
        
        # Prepare component dictionary for mapping and validation
        comp_dict = {c['name'].lower(): c for c in component_list}
        comp_valid_pins = {}
        comp_list_with_pins = []
        for c in component_list:
            pins = ComponentPin.query.filter_by(component_id=c['id']).all()
            pin_names = [p.pin_name for p in pins]
            comp_valid_pins[c['name'].lower()] = pin_names
            if pin_names:
                pin_str = f"Exact pin names to use: {', '.join(pin_names)}"
            else:
                pin_str = f"Pins: {c.get('pin_configuration', 'unknown')}"
            comp_list_with_pins.append(f"- {c['name']} ({pin_str})")
            
        comp_list_str = "\\n".join(comp_list_with_pins)        
        system_prompt = f"""You are an electronic circuit design assistant.
Convert the user's natural-language circuit request into structured JSON.
Use ONLY components available in the provided component library.
Return JSON ONLY. Do not return Markdown. Do not return HTML. Do not return JavaScript.
Do not invent component types. Do not invent pins.
Use the component library information provided below.

AVAILABLE COMPONENTS:
{comp_list_str}

REQUIRED JSON FORMAT:
{{
  "circuit_name": "Circuit Name",
  "description": "Educational explanation of the circuit.",
  "components": [
    {{
      "id": "C1",
      "type": "component_name_from_library",
      "value": 10,
      "unit": "ohm"
    }}
  ],
  "connections": [
    {{
      "from": {{
        "component": "C1",
        "pin": "pin1"
      }},
      "to": {{
        "component": "C2",
        "pin": "pin2"
      }}
    }}
  ]
}}
"""

        payload = {
            "model": model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False
        }
        
        # --- FAST HYBRID PARSER ---
        lower_prompt = prompt.lower()
        fast_keywords = {
            "battery": "Battery",
            "resistor": "Resistor",
            "led": "LED",
            "switch": "Switch",
            "push button": "Push Button",
            "capacitor": "Capacitor",
            "diode": "Diode",
            "motor": "Motor",
            "buzzer": "Buzzer"
        }
        
        found_comps = []
        for kw, comp_name in fast_keywords.items():
            if kw in lower_prompt:
                if comp_name.lower() in comp_dict:
                    found_comps.append(comp_name)
                    
        complex_words = ["parallel", "transistor", "amplifier", "microcontroller", "arduino", "ic", "timer", "relay"]
        is_complex = any(cw in lower_prompt for cw in complex_words)
        
        is_fast_path = False
        circuit_json = None
        
        # If simple prompt with battery and at least one other recognized component
        if "Battery" in found_comps and len(found_comps) >= 2 and not is_complex:
            is_fast_path = True
            
            components_json = []
            connections_json = []
            
            for i, c_name in enumerate(found_comps):
                c_data = comp_dict[c_name.lower()]
                components_json.append({
                    "id": f"C{i+1}",
                    "type": c_data['name'],
                    "value": c_data.get('default_value', ''),
                    "unit": c_data.get('unit', '')
                })
                
            for i in range(len(found_comps)):
                from_idx = i
                to_idx = (i + 1) % len(found_comps)
                
                from_c_name = found_comps[from_idx].lower()
                to_c_name = found_comps[to_idx].lower()
                
                from_pins = comp_valid_pins.get(from_c_name, [])
                to_pins = comp_valid_pins.get(to_c_name, [])
                
                from_pin = from_pins[1] if len(from_pins) > 1 else (from_pins[0] if from_pins else 'pin2')
                to_pin = to_pins[0] if to_pins else 'pin1'
                
                connections_json.append({
                    "from": {
                        "component": f"C{from_idx+1}",
                        "pin": from_pin
                    },
                    "to": {
                        "component": f"C{to_idx+1}",
                        "pin": to_pin
                    }
                })
                
            circuit_json = {
                "circuit_name": "Fast Series Circuit",
                "description": "Rule-based series circuit generated instantly without AI.",
                "components": components_json,
                "connections": connections_json
            }
        
        try:
            if is_fast_path:
                print("FAST PATH: Rule-based generation")
            else:
                print("AI PATH: Ollama generation")
                response = requests.post(f"{base_url}/api/generate", json=payload, timeout=15)
                response.raise_for_status()
                
                result = response.json()
                raw_text = result.get('response', '')
                
                # Extract JSON block if surrounded by markdown
                json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    json_str = raw_text
                    
                try:
                    circuit_json = json.loads(json_str)
                except json.JSONDecodeError:
                    return {"success": False, "error": "AI returned an invalid circuit format."}
            # Database mapping and validation
            mapped_components = []
            for comp in circuit_json.get('components', []):
                ctype = comp.get('type', '').lower()
                if ctype not in comp_dict:
                    return {"success": False, "error": f"Component '{comp.get('type')}' not found in the component library."}
                
                # Normalize type name to the authoritative library name
                comp['type'] = comp_dict[ctype]['name']
                mapped_components.append(comp)
                
            circuit_json['components'] = mapped_components
            
            def normalize_pin(comp_type, pin_requested):
                if not pin_requested:
                    return pin_requested
                c_type_lower = comp_type.lower()
                valid_pins = comp_valid_pins.get(c_type_lower, [])
                if not valid_pins:
                    return pin_requested
                if pin_requested in valid_pins:
                    return pin_requested
                req_lower = str(pin_requested).lower()
                for vp in valid_pins:
                    if vp.lower() == req_lower:
                        return vp
                aliases = {
                    '+': 'positive', '-': 'negative', 'p': 'positive', 'n': 'negative',
                    'pos': 'positive', 'neg': 'negative', 'anode': 'anode', 'cathode': 'cathode',
                    'a': 'anode', 'k': 'cathode', 'c': 'cathode', '1': 'pin1', '2': 'pin2',
                    'base': 'base', 'collector': 'collector', 'emitter': 'emitter',
                    'b': 'base', 'e': 'emitter'
                }
                mapped = aliases.get(req_lower)
                if mapped and mapped in valid_pins:
                    return mapped
                return pin_requested

            print("--- PIN MAPPING LOG ---")
            flat_connections = []
            for idx, conn in enumerate(circuit_json.get('connections', [])):
                from_c = conn.get('from', {})
                to_c = conn.get('to', {})
                
                from_comp_id = from_c.get('component')
                to_comp_id = to_c.get('component')
                
                from_comp_type = next((c['type'] for c in mapped_components if c['id'] == from_comp_id), "")
                to_comp_type = next((c['type'] for c in mapped_components if c['id'] == to_comp_id), "")
                
                from_pin = from_c.get('pin')
                to_pin = to_c.get('pin')
                
                norm_from_pin = normalize_pin(from_comp_type, from_pin)
                norm_to_pin = normalize_pin(to_comp_type, to_pin)
                
                print(f"{from_comp_type} -> {comp_valid_pins.get(from_comp_type.lower(), [])} -> AI requested: {from_pin} -> Final mapped: {norm_from_pin}")
                print(f"{to_comp_type} -> {comp_valid_pins.get(to_comp_type.lower(), [])} -> AI requested: {to_pin} -> Final mapped: {norm_to_pin}")
                
                from_c['pin'] = norm_from_pin
                to_c['pin'] = norm_to_pin
                
                flat_connections.append({
                    "id": f"wire_ai_{idx}",
                    "source": from_comp_id,
                    "sourcePin": norm_from_pin,
                    "target": to_comp_id,
                    "targetPin": norm_to_pin
                })
            print("-----------------------")
                
            validation_input = {
                "components": circuit_json['components'],
                "connections": flat_connections
            }
            
            # Run validation
            val_result = ValidationService.validate_circuit(validation_input)
            
            if not val_result['valid']:
                error_msg = "; ".join(val_result['errors'])
                return {"success": False, "error": f"Invalid circuit generated by AI: {error_msg}"}
                
            return {
                "success": True,
                "circuit": circuit_json,
                "explanation": circuit_json.get('description', ''),
                "components": circuit_json['components'],
                "warnings": val_result.get('warnings', [])
            }
            
        except requests.exceptions.Timeout:
            return {"success": False, "error": "AI service timed out after 15 seconds. Please try a simpler prompt or use recognized components."}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": "AI service is unavailable. Make sure Ollama is running."}
        except Exception as e:
            return {"success": False, "error": f"An error occurred: {str(e)}"}
