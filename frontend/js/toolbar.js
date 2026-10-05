class ToolbarUI {
    constructor(state, canvas, propertiesUI, wiringUI) {
        this.state = state;
        this.canvas = canvas;
        this.propertiesUI = propertiesUI;
        this.wiringUI = wiringUI;

        this.initEvents();
    }

    initEvents() {
        document.getElementById('btn-new').addEventListener('click', () => {
            if (confirm("Clear the canvas? Unsaved changes will be lost.")) {
                this.state.clear();
                this.canvas.resetView();
                this.canvas.render();
                this.propertiesUI.render();
            }
        });

        document.getElementById('btn-undo').addEventListener('click', () => {
            if(this.state.undo()) {
                this.canvas.render();
                this.propertiesUI.render();
            }
        });

        document.getElementById('btn-redo').addEventListener('click', () => {
            if(this.state.redo()) {
                this.canvas.render();
                this.propertiesUI.render();
            }
        });

        document.getElementById('btn-delete').addEventListener('click', () => {
            if (this.state.selectedComponentId) {
                this.state.deleteComponent(this.state.selectedComponentId);
                this.canvas.render();
                this.propertiesUI.render();
            } else if (this.state.selectedConnectionId) {
                this.state.deleteConnection(this.state.selectedConnectionId);
                if (this.wiringUI) this.wiringUI.renderConnections();
            }
        });

        document.getElementById('btn-wire').addEventListener('click', () => {
            if (this.wiringUI) {
                this.wiringUI.toggleWireMode();
            }
        });

        document.getElementById('btn-rotate').addEventListener('click', () => {
            if (this.state.selectedComponentId) {
                const comp = this.state.getSelectedComponent();
                if (comp) {
                    comp.rotation = (comp.rotation + 90) % 360;
                    this.state.saveState();
                    this.canvas.render();
                    this.propertiesUI.render();
                }
            }
        });

        document.getElementById('btn-zoom-in').addEventListener('click', () => {
            this.canvas.setZoom(Math.min(this.canvas.scale * 1.2, 5));
        });

        document.getElementById('btn-zoom-out').addEventListener('click', () => {
            this.canvas.setZoom(Math.max(this.canvas.scale / 1.2, 0.1));
        });

        document.getElementById('btn-fit').addEventListener('click', () => {
            this.canvas.resetView();
        });
        
        document.getElementById('btn-save').addEventListener('click', () => {
            const json = this.state.getCircuitJSON();
            console.log("Circuit saved to JSON:");
            console.log(json);
            alert("Circuit serialized to JSON. Check console.");
        });

        // Delete with keyboard
        window.addEventListener('keydown', e => {
            if (e.key === 'Delete' || e.key === 'Backspace') {
                // Ignore if editing text input
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
                
                if (this.state.selectedComponentId) {
                    this.state.deleteComponent(this.state.selectedComponentId);
                    this.canvas.render();
                    this.propertiesUI.render();
                } else if (this.state.selectedConnectionId) {
                    this.state.deleteConnection(this.state.selectedConnectionId);
                    if (this.wiringUI) this.wiringUI.renderConnections();
                }
            }
        });
    }
}
