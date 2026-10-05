class ValidationUI {
    constructor(state, api, canvas, wiringUI, propertiesUI) {
        this.state = state;
        this.api = api;
        this.canvas = canvas;
        this.wiringUI = wiringUI;
        this.propertiesUI = propertiesUI;
        
        this.btnValidate = document.getElementById('btn-run-validation');
        this.resultsContainer = document.getElementById('validation-results');
        
        this.initEvents();
    }
    
    initEvents() {
        if (this.btnValidate) {
            this.btnValidate.addEventListener('click', () => this.runValidation());
        }
        
        // Handle clicking on interactive tokens in the validation messages
        this.resultsContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('val-token')) {
                const id = e.target.dataset.id;
                
                // Determine if it's a component or connection
                if (id.startsWith('wire_')) {
                    this.state.selectConnection(id);
                    this.state.selectComponent(null);
                } else {
                    this.state.selectComponent(id);
                    this.state.selectConnection(null);
                }
                
                this.canvas.render();
                if (this.wiringUI) this.wiringUI.renderConnections();
                if (this.propertiesUI) this.propertiesUI.render();
            }
        });
    }
    
    async runValidation() {
        this.resultsContainer.innerHTML = '<p>Running validation...</p>';
        this.btnValidate.disabled = true;
        
        const result = await this.api.validateCircuit(this.state.circuit);
        
        this.btnValidate.disabled = false;
        this.renderResults(result);
    }
    
    renderResults(result) {
        let html = '';
        
        if (result.errors && result.errors.length > 0) {
            html += '<div class="val-section val-errors">';
            html += '<h4>ERRORS</h4><ul>';
            result.errors.forEach(msg => {
                html += `<li>❌ ${this.tokenizeMessage(msg)}</li>`;
            });
            html += '</ul></div>';
        }
        
        if (result.warnings && result.warnings.length > 0) {
            html += '<div class="val-section val-warnings">';
            html += '<h4>WARNINGS</h4><ul>';
            result.warnings.forEach(msg => {
                html += `<li>⚠ ${this.tokenizeMessage(msg)}</li>`;
            });
            html += '</ul></div>';
        }
        
        if (result.info && result.info.length > 0) {
            html += '<div class="val-section val-info">';
            html += '<h4>INFO</h4><ul>';
            result.info.forEach(msg => {
                html += `<li>✓ ${this.tokenizeMessage(msg)}</li>`;
            });
            html += '</ul></div>';
        }
        
        if (result.valid && (!result.warnings || result.warnings.length === 0) && (!result.errors || result.errors.length === 0)) {
            html = '<div class="val-section val-success"><h4>✓ Circuit validation completed.</h4><p>No errors or warnings found.</p></div>' + html;
        }
        
        this.resultsContainer.innerHTML = html;
    }
    
    // Finds component IDs like 'B1', 'R1', or connection IDs like 'wire_123_456' and makes them clickable
    tokenizeMessage(msg) {
        // Regex to match wire IDs (wire_...) or Component IDs (A-Z followed by numbers)
        const regex = /\\b(wire_\\d+_\\d+|[A-Z]+\\d+)\\b/g;
        return msg.replace(regex, (match) => {
            // Check if it actually exists in the circuit
            const isComp = this.state.circuit.components.some(c => c.id === match);
            const isWire = this.state.circuit.connections.some(c => c.id === match);
            if (isComp || isWire) {
                return `<span class="val-token" data-id="${match}">${match}</span>`;
            }
            return match;
        });
    }
}

window.ValidationUI = ValidationUI;
