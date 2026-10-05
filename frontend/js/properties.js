class PropertiesUI {
    constructor(state, canvas) {
        this.state = state;
        this.canvas = canvas;
        this.panel = document.getElementById('properties-panel');
    }

    render() {
        const comp = this.state.getSelectedComponent();
        
        if (!comp) {
            this.panel.className = 'properties-empty';
            this.panel.innerHTML = '<p>Select a component to view and edit its properties.</p>';
            return;
        }

        this.panel.className = 'properties-filled';
        this.panel.innerHTML = `
            <div class="prop-row"><label>ID:</label><span>${comp.id}</span></div>
            <div class="prop-row"><label>Type:</label><span>${comp.type}</span></div>
            <div class="prop-row">
                <label>Value:</label>
                <input type="text" id="prop-val" value="${comp.value || ''}" />
            </div>
            <div class="prop-row">
                <label>Unit:</label>
                <input type="text" id="prop-unit" value="${comp.unit || ''}" />
            </div>
            <div class="prop-row"><label>Rotation:</label><span>${comp.rotation}°</span></div>
            <div class="prop-row"><label>Position:</label><span>${comp.x}, ${comp.y}</span></div>
        `;

        document.getElementById('prop-val').addEventListener('change', (e) => {
            this.state.updateComponent(comp.id, { value: e.target.value });
            this.canvas.render();
        });
        
        document.getElementById('prop-unit').addEventListener('change', (e) => {
            this.state.updateComponent(comp.id, { unit: e.target.value });
            this.canvas.render();
        });
    }
}
