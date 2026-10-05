class AIUI {
    constructor(state, api, canvas, wiringUI, validationUI, componentsUI) {
        this.state = state;
        this.api = api;
        this.canvas = canvas;
        this.wiringUI = wiringUI;
        this.validationUI = validationUI;
        this.componentsUI = componentsUI;
        
        this.btnGenerate = document.getElementById('btn-generate');
        this.promptInput = document.getElementById('ai-prompt-input');
        this.explanationText = document.getElementById('ai-explanation-text');
        
        this.initEvents();
    }
    
    initEvents() {
        if (this.btnGenerate) {
            this.btnGenerate.addEventListener('click', () => this.handleGenerate());
        }
        if (this.promptInput) {
            this.promptInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    this.handleGenerate();
                }
            });
        }
    }
    
    async handleGenerate() {
        const prompt = this.promptInput.value.trim();
        if (!prompt) {
            alert("Please describe the circuit you want to create.");
            return;
        }
        
        // Show loading state
        this.btnGenerate.disabled = true;
        const originalText = this.btnGenerate.innerText;
        this.btnGenerate.innerText = 'Generating...';
        this.explanationText.innerText = 'AI is designing your circuit...';
        
        // Call API
        const result = await this.api.generateCircuit(prompt);
        
        this.btnGenerate.disabled = false;
        this.btnGenerate.innerText = originalText;
        
        if (!result.success) {
            alert(result.error || 'An error occurred during generation.');
            this.explanationText.innerText = result.error || 'Generation failed.';
            return;
        }
        
        // Switch to Explanation tab
        const explainTabBtn = document.querySelector('.tab-btn[data-tab="tab-explanation"]');
        if (explainTabBtn) explainTabBtn.click();
        
        this.explanationText.innerText = result.explanation || 'Circuit generated successfully.';
        
        this.buildCircuit(result.circuit);
    }
    
    buildCircuit(circuit) {
        // Clear current circuit
        this.state.circuit.components = [];
        this.state.circuit.connections = [];
        this.state.selectComponent(null);
        this.state.selectConnection(null);
        
        const comps = circuit.components || [];
        const conns = circuit.connections || [];
        
        // 1. Layout components
        // Simple horizontal layout: spacing = 150px
        let currentX = 100;
        const currentY = 150;
        
        comps.forEach(c => {
            this.state.circuit.components.push({
                id: c.id,
                type: c.type,
                symbolId: this.state.getSymbolId(c.type),
                value: c.value ? String(c.value) : "",
                unit: c.unit || "",
                x: currentX,
                y: currentY,
                rotation: 0
            });
            currentX += 150;
            
            // Increment ID counter if necessary to avoid collision with manual drops
            const match = c.id.match(/^[a-zA-Z]+(\\d+)$/);
            if (match) {
                const num = parseInt(match[1]);
                const prefix = c.id.replace(num, '');
                if (!this.state.idCounters[prefix] || this.state.idCounters[prefix] <= num) {
                    this.state.idCounters[prefix] = num + 1;
                }
            }
        });
        
        // 2. Add connections
        conns.forEach((conn, index) => {
            this.state.circuit.connections.push({
                id: conn.id || `wire_ai_${Date.now()}_${index}`,
                source: conn.source || (conn.from ? conn.from.component : null),
                sourcePin: conn.sourcePin || (conn.from ? conn.from.pin : null),
                target: conn.target || (conn.to ? conn.to.component : null),
                targetPin: conn.targetPin || (conn.to ? conn.to.pin : null)
            });
        });
        
        this.state.saveState();
        
        // Render
        this.canvas.render();
        if (this.wiringUI) this.wiringUI.renderConnections();
        if (this.componentsUI) this.componentsUI.updateComponentsList();
        
        // Run validation automatically
        if (this.validationUI) {
            this.validationUI.runValidation();
            
            // Switch to Validation tab after 2 seconds
            setTimeout(() => {
                const valTabBtn = document.querySelector('.tab-btn[data-tab="tab-validation"]');
                if (valTabBtn) valTabBtn.click();
            }, 3000);
        }
    }
}

window.AIUI = AIUI;
