class State {
    constructor() {
        this.circuit = {
            components: [],
            connections: []
        };
        this.selectedConnectionId = null;
        this.history = [];
        this.historyIndex = -1;
        this.selectedComponentId = null;
        this.idCounters = {};
        
        this.saveState(); // Initial state
    }

    generateId(prefix) {
        if (!this.idCounters[prefix]) this.idCounters[prefix] = 1;
        else this.idCounters[prefix]++;
        return `${prefix}${this.idCounters[prefix]}`;
    }

    getPrefix(componentName) {
        const map = {
            'Resistor': 'R', 'Capacitor': 'C', 'Inductor': 'L',
            'Battery': 'B', 'DC Voltage Source': 'V',
            'LED': 'LED', 'Diode': 'D', 'Zener Diode': 'ZD',
            'Switch': 'SW', 'Push Button': 'PB',
            'NPN Transistor': 'Q', 'PNP Transistor': 'Q',
            'Ground': 'GND', 'Lamp': 'LAMP', 'Buzzer': 'BZ', 'Motor': 'M', 'Potentiometer': 'POT'
        };
        return map[componentName] || 'U';
    }

    addComponent(compData, x, y) {
        const prefix = this.getPrefix(compData.name);
        const id = this.generateId(prefix);
        const newComp = {
            id,
            type: compData.name,
            symbolId: this.getSymbolId(compData.name),
            value: compData.default_value,
            unit: compData.unit,
            x, y,
            rotation: 0
        };
        this.circuit.components.push(newComp);
        this.saveState();
        return newComp;
    }

    getSymbolId(name) {
        const map = {
            'Battery': 'sym-battery', 'DC Voltage Source': 'sym-battery',
            'Resistor': 'sym-resistor', 'Potentiometer': 'sym-resistor',
            'Ground': 'sym-ground',
            'LED': 'sym-led', 'Diode': 'sym-diode', 'Zener Diode': 'sym-diode',
            'Switch': 'sym-switch', 'Push Button': 'sym-switch',
            'Capacitor': 'sym-capacitor',
            'NPN Transistor': 'sym-transistor', 'PNP Transistor': 'sym-transistor'
        };
        return map[name] || 'sym-generic';
    }

    updateComponent(id, updates) {
        const comp = this.circuit.components.find(c => c.id === id);
        if (comp) {
            Object.assign(comp, updates);
            this.saveState();
        }
    }

    deleteComponent(id) {
        this.circuit.components = this.circuit.components.filter(c => c.id !== id);
        // Also delete associated connections
        this.circuit.connections = this.circuit.connections.filter(c => c.source !== id && c.target !== id);
        if (this.selectedComponentId === id) this.selectedComponentId = null;
        this.saveState();
    }

    addConnection(sourceCompId, sourcePin, targetCompId, targetPin) {
        const id = `wire_${Date.now()}_${Math.floor(Math.random()*1000)}`;
        const connection = {
            id,
            source: sourceCompId,
            sourcePin: sourcePin,
            target: targetCompId,
            targetPin: targetPin
        };
        // Check for duplicates
        const exists = this.circuit.connections.find(c => 
            (c.source === sourceCompId && c.sourcePin === sourcePin && c.target === targetCompId && c.targetPin === targetPin) ||
            (c.source === targetCompId && c.sourcePin === targetPin && c.target === sourceCompId && c.targetPin === sourcePin)
        );
        
        if (!exists) {
            this.circuit.connections.push(connection);
            this.saveState();
            return connection;
        }
        return null;
    }

    deleteConnection(id) {
        this.circuit.connections = this.circuit.connections.filter(c => c.id !== id);
        if (this.selectedConnectionId === id) this.selectedConnectionId = null;
        this.saveState();
    }

    selectConnection(id) {
        this.selectedConnectionId = id;
    }

    clear() {
        this.circuit.components = [];
        this.circuit.connections = [];
        this.selectedComponentId = null;
        this.selectedConnectionId = null;
        this.idCounters = {};
        this.saveState();
    }

    selectComponent(id) {
        this.selectedComponentId = id;
    }

    getSelectedComponent() {
        return this.circuit.components.find(c => c.id === this.selectedComponentId);
    }

    saveState() {
        const stateStr = JSON.stringify(this.circuit);
        // Avoid duplicate states
        if (this.historyIndex >= 0 && this.history[this.historyIndex] === stateStr) return;
        
        this.history = this.history.slice(0, this.historyIndex + 1);
        this.history.push(stateStr);
        this.historyIndex++;
        this.logHistory(`Action ${this.historyIndex}`);
    }

    undo() {
        if (this.historyIndex > 0) {
            this.historyIndex--;
            this.circuit = JSON.parse(this.history[this.historyIndex]);
            this.selectedComponentId = null;
            this.selectedConnectionId = null;
            return true;
        }
        return false;
    }

    redo() {
        if (this.historyIndex < this.history.length - 1) {
            this.historyIndex++;
            this.circuit = JSON.parse(this.history[this.historyIndex]);
            this.selectedComponentId = null;
            this.selectedConnectionId = null;
            return true;
        }
        return false;
    }

    getCircuitJSON() {
        return JSON.stringify(this.circuit, null, 2);
    }

    loadCircuitJSON(jsonStr) {
        this.circuit = JSON.parse(jsonStr);
        this.saveState();
    }

    logHistory(action) {
        const list = document.getElementById('history-list');
        if(list) {
            const li = document.createElement('li');
            li.textContent = `[${new Date().toLocaleTimeString()}] State updated`;
            list.prepend(li);
        }
        // Update components tab
        const compTab = document.getElementById('components-list');
        if(compTab) {
            if(this.circuit.components.length === 0) {
                compTab.innerHTML = '<p>No components placed yet.</p>';
            } else {
                compTab.innerHTML = '<ul>' + this.circuit.components.map(c => `<li>${c.id} (${c.type}): ${c.value}${c.unit} @ ${Math.round(c.x)},${Math.round(c.y)}</li>`).join('') + '</ul>';
            }
        }
        
        // Update connections tab
        const connTab = document.getElementById('connections-list');
        if(connTab) {
            if(this.circuit.connections.length === 0) {
                connTab.innerHTML = '<p>No wires connected yet.</p>';
            } else {
                connTab.innerHTML = '<ul>' + this.circuit.connections.map(c => `<li>${c.source}:${c.sourcePin} &harr; ${c.target}:${c.targetPin}</li>`).join('') + '</ul>';
            }
        }
    }
}

window.state = new State();
