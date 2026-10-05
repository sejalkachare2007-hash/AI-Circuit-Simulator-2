import json
from database.models import Component, ConnectionRule

class ValidationService:
    @staticmethod
    def validate_circuit(circuit_data):
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        components = circuit_data.get('components', [])
        connections = circuit_data.get('connections', [])
        
        # 1. Check Empty Circuit
        if not components:
            result['errors'].append("No components placed in the circuit.")
            result['valid'] = False
            return result
            
        if not connections:
            result['errors'].append("No connections found.")
            result['valid'] = False
            return result
            
        # Build lookup dictionaries
        comp_dict = {c['id']: c for c in components}
        
        # Load expected pins from the database
        from database.models import ComponentPin
        expected_pins = {}
        for comp in components:
            c_type = comp.get('type')
            if c_type and c_type not in expected_pins:
                # Need to find the component ID by name
                db_comp = Component.query.filter_by(name=c_type).first()
                if db_comp:
                    pins = ComponentPin.query.filter_by(component_id=db_comp.id).all()
                    if pins:
                        expected_pins[c_type] = [p.pin_name for p in pins]
        
        # Track connected pins: comp_id -> set of pin_names
        connected_pins = {c['id']: set() for c in components}
        
        # Track edges for basic electrical rule checks
        # Adjacency list: node -> list of (neighbor, connection_id)
        # Here "node" is just the component id, which is a simplification.
        # But wait, electrical nodes are connected nets.
        
        # 2. Check Connections
        seen_connections = set()
        
        for conn in connections:
            src = conn.get('source')
            src_pin = conn.get('sourcePin')
            tgt = conn.get('target')
            tgt_pin = conn.get('targetPin')
            
            # Self connection
            if src == tgt and src_pin == tgt_pin:
                result['errors'].append(f"A component pin cannot be connected to itself ({src}.{src_pin}).")
                result['valid'] = False
                continue
                
            # Component reference check
            if src not in comp_dict:
                result['errors'].append(f"Connection {conn.get('id')} references an unknown component {src}.")
                result['valid'] = False
                continue
            if tgt not in comp_dict:
                result['errors'].append(f"Connection {conn.get('id')} references an unknown component {tgt}.")
                result['valid'] = False
                continue
                
            # Pin reference check
            src_type = comp_dict[src].get('type')
            tgt_type = comp_dict[tgt].get('type')
            
            if src_type in expected_pins and src_pin not in expected_pins[src_type]:
                result['errors'].append(f"{src}.{src_pin} is not a valid pin.")
                result['valid'] = False
            else:
                connected_pins[src].add(src_pin)
                
            if tgt_type in expected_pins and tgt_pin not in expected_pins[tgt_type]:
                result['errors'].append(f"{tgt}.{tgt_pin} is not a valid pin.")
                result['valid'] = False
            else:
                connected_pins[tgt].add(tgt_pin)
                
            # Duplicate connection check
            # Undirected connection signature
            conn_sig = tuple(sorted([f"{src}.{src_pin}", f"{tgt}.{tgt_pin}"]))
            if conn_sig in seen_connections:
                result['errors'].append(f"Duplicate connection detected between {src}.{src_pin} and {tgt}.{tgt_pin}.")
                result['valid'] = False
            else:
                seen_connections.add(conn_sig)

        # 3. Check Unconnected Pins
        for comp in components:
            c_id = comp['id']
            c_type = comp['type']
            if c_type in expected_pins:
                for pin in expected_pins[c_type]:
                    if pin not in connected_pins[c_id]:
                        # Optional: don't warn for Ground if it's placed but maybe warn anyway
                        result['warnings'].append(f"{c_type} {c_id} {pin} pin is not connected.")
                        
        # 4. Basic Electrical Rules & Node Analysis
        # Build electrical nodes (connected components)
        # We can use Union-Find for nodes
        parent = {}
        def find(i):
            if parent.get(i, i) == i: return i
            parent[i] = find(parent[i])
            return parent[i]
        def union(i, j):
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                parent[root_i] = root_j

        for conn in connections:
            if conn.get('source') in comp_dict and conn.get('target') in comp_dict:
                src_node = f"{conn.get('source')}.{conn.get('sourcePin')}"
                tgt_node = f"{conn.get('target')}.{conn.get('targetPin')}"
                parent[src_node] = src_node
                parent[tgt_node] = tgt_node
                union(src_node, tgt_node)

        # Check shorted battery
        for comp in components:
            if comp['type'] in ['Battery', 'DC Voltage Source']:
                p_node = f"{comp['id']}.positive"
                n_node = f"{comp['id']}.negative"
                if p_node in parent and n_node in parent:
                    if find(p_node) == find(n_node):
                        result['errors'].append("Power source terminals appear to be short-circuited.")
                        result['valid'] = False
                        
            # Check bypassed resistor
            if comp['type'] == 'Resistor':
                p1_node = f"{comp['id']}.pin1"
                p2_node = f"{comp['id']}.pin2"
                if p1_node in parent and p2_node in parent:
                    if find(p1_node) == find(p2_node):
                        result['warnings'].append("Resistor may be bypassed.")

            # Check LED directly across battery
            if comp['type'] == 'LED':
                # Simplified check: if LED is connected to battery without resistor
                # Let's see if LED anode and cathode are in the same net as Battery positive and negative
                led_a = f"{comp['id']}.anode"
                led_c = f"{comp['id']}.cathode"
                
                # Check all power sources
                for pwr in components:
                    if pwr['type'] in ['Battery', 'DC Voltage Source']:
                        pwr_p = f"{pwr['id']}.positive"
                        pwr_n = f"{pwr['id']}.negative"
                        
                        if led_a in parent and led_c in parent and pwr_p in parent and pwr_n in parent:
                            if (find(led_a) == find(pwr_p) and find(led_c) == find(pwr_n)) or \
                               (find(led_a) == find(pwr_n) and find(led_c) == find(pwr_p)):
                                result['warnings'].append("LED may require a current-limiting resistor.")

        # 5. DB Rules check (Optional advanced rules)
        try:
            db_rules = ConnectionRule.query.all()
            # If there are any rules in the DB, we can evaluate them
            # For simplicity, we stick to the hardcoded educational rules above 
            # unless specific DB rules are defined.
        except Exception:
            pass

        if result['valid']:
            result['info'].append("All component references are valid.")
            result['info'].append("Circuit validation completed.")
            
        return result
