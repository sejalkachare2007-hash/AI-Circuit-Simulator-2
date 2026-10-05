class WiringUI {
    constructor(state, canvas) {
        this.state = state;
        this.canvas = canvas;
        this.svg = document.getElementById('circuit-canvas');
        this.connectionsLayer = document.getElementById('connections-layer');
        this.componentsLayer = document.getElementById('components-layer');
        
        this.wireMode = false;
        this.tempWire = null;
        this.startPinInfo = null;

        this.initEvents();
        
        // Override state save to also render connections
        const originalSave = this.state.saveState.bind(this.state);
        this.state.saveState = () => {
            originalSave();
            this.renderConnections();
        };
        // and initial render
        setTimeout(() => this.renderConnections(), 100);
    }

    setWireMode(active) {
        this.wireMode = active;
        const btn = document.getElementById('btn-wire');
        if (active) {
            btn.classList.add('wire-mode-active');
            this.svg.classList.add('wiring-active');
            this.canvas.state.selectComponent(null);
            this.canvas.propertiesUI.render();
            this.canvas.render(); // Redraw selection outline
        } else {
            btn.classList.remove('wire-mode-active');
            this.svg.classList.remove('wiring-active');
            this.cancelTempWire();
        }
    }

    toggleWireMode() {
        this.setWireMode(!this.wireMode);
    }

    getPinAbsolutePosition(compId, pinName) {
        const comp = this.state.circuit.components.find(c => c.id === compId);
        if (!comp) return { x: 0, y: 0 };
        
        const symbol = document.getElementById(comp.symbolId);
        if (!symbol) return { x: comp.x, y: comp.y };
        
        const pinElement = symbol.querySelector(`circle[data-pin="${pinName}"]`);
        if (!pinElement) return { x: comp.x, y: comp.y };
        
        const cx = parseFloat(pinElement.getAttribute('cx') || '0');
        const cy = parseFloat(pinElement.getAttribute('cy') || '0');
        
        const rad = (comp.rotation || 0) * Math.PI / 180;
        const absX = comp.x + (cx * Math.cos(rad) - cy * Math.sin(rad));
        const absY = comp.y + (cx * Math.sin(rad) + cy * Math.cos(rad));
        
        return { x: absX, y: absY };
    }

    initEvents() {
        // We use event delegation on the componentsLayer since `<use>` elements might have shadow DOM, 
        // but pointer events on the `<use>` element don't easily give us the target inside.
        // Actually, SVG 2 doesn't fully expose the used element events. 
        // A better way: Instead of relying on `<use>` for the pin hitboxes, wait, `use` clones everything.
        // We can capture events on the svg if we are in wire mode.

        this.svg.addEventListener('mousedown', e => {
            if (!this.wireMode) {
                // If not in wire mode, allow selecting connections
                const targetConnection = e.target.closest('.circuit-wire');
                if (targetConnection && targetConnection.id !== 'wire-temp') {
                    const id = targetConnection.dataset.id;
                    this.state.selectConnection(id);
                    this.state.selectComponent(null);
                    this.canvas.propertiesUI.render();
                    this.renderConnections();
                    this.canvas.render();
                    e.stopPropagation();
                } else if (!e.target.closest('.circuit-component')) {
                    if (this.state.selectedConnectionId) {
                        this.state.selectConnection(null);
                        this.renderConnections();
                    }
                }
                return;
            }

            // In Wire mode
            // We need to find if we clicked a pin-hitbox. 
            // In shadow DOM (from <use>), `e.target` might be the `<use>` element itself.
            // Let's calculate distance to all pins to see if we clicked one.
            const rect = this.svg.getBoundingClientRect();
            const rawX = e.clientX - rect.left;
            const rawY = e.clientY - rect.top;
            
            const mouseX = (rawX - this.canvas.panX) / this.canvas.scale;
            const mouseY = (rawY - this.canvas.panY) / this.canvas.scale;
            
            let clickedPin = this.findClosestPin(mouseX, mouseY, 10);
            
            if (clickedPin) {
                if (this.startPinInfo) {
                    // Clicked second pin -> Complete connection
                    if (clickedPin.compId !== this.startPinInfo.compId) {
                        this.state.addConnection(this.startPinInfo.compId, this.startPinInfo.pinName, clickedPin.compId, clickedPin.pinName);
                    }
                    this.cancelTempWire();
                } else {
                    // Clicked first pin -> Start connection
                    this.startPinInfo = clickedPin;
                    this.createTempWire(clickedPin.x, clickedPin.y);
                }
                e.stopPropagation();
            } else {
                // Clicked elsewhere -> cancel
                if (this.startPinInfo) {
                    this.cancelTempWire();
                }
            }
        });

        window.addEventListener('mousemove', e => {
            if (this.wireMode && this.tempWire && this.startPinInfo) {
                const rect = this.svg.getBoundingClientRect();
                const rawX = e.clientX - rect.left;
                const rawY = e.clientY - rect.top;
                
                const mouseX = (rawX - this.canvas.panX) / this.canvas.scale;
                const mouseY = (rawY - this.canvas.panY) / this.canvas.scale;
                
                // Snap to pins
                let targetPin = this.findClosestPin(mouseX, mouseY, 15);
                
                let endX = mouseX;
                let endY = mouseY;
                
                if (targetPin && (targetPin.compId !== this.startPinInfo.compId || targetPin.pinName !== this.startPinInfo.pinName)) {
                    endX = targetPin.x;
                    endY = targetPin.y;
                }
                
                this.updateTempWire(this.startPinInfo.x, this.startPinInfo.y, endX, endY);
            }
        });

        // Cancel with ESC
        window.addEventListener('keydown', e => {
            if (e.key === 'Escape') {
                if (this.tempWire) {
                    this.cancelTempWire();
                } else if (this.wireMode) {
                    this.setWireMode(false);
                } else if (this.state.selectedConnectionId) {
                    this.state.selectConnection(null);
                    this.renderConnections();
                }
            }
        });
    }

    findClosestPin(x, y, threshold = 10) {
        let closest = null;
        let minDist = threshold * threshold; // Use squared distance
        
        for (const comp of this.state.circuit.components) {
            const symbol = document.getElementById(comp.symbolId);
            if (!symbol) continue;
            
            const pins = symbol.querySelectorAll('circle.pin-hitbox');
            for (const pin of pins) {
                const pinName = pin.getAttribute('data-pin');
                const pos = this.getPinAbsolutePosition(comp.id, pinName);
                
                const dx = pos.x - x;
                const dy = pos.y - y;
                const distSq = dx*dx + dy*dy;
                
                if (distSq <= minDist) {
                    minDist = distSq;
                    closest = { compId: comp.id, pinName: pinName, x: pos.x, y: pos.y };
                }
            }
        }
        
        return closest;
    }

    createTempWire(startX, startY) {
        this.tempWire = document.createElementNS("http://www.w3.org/2000/svg", "path");
        this.tempWire.setAttribute('id', 'wire-temp');
        this.tempWire.setAttribute('class', 'circuit-wire');
        this.updateTempWire(startX, startY, startX, startY);
        this.connectionsLayer.appendChild(this.tempWire);
    }

    updateTempWire(x1, y1, x2, y2) {
        if (!this.tempWire) return;
        // Simple orthogonal routing
        const midX = x1 + (x2 - x1) / 2;
        const d = `M ${x1} ${y1} L ${midX} ${y1} L ${midX} ${y2} L ${x2} ${y2}`;
        this.tempWire.setAttribute('d', d);
    }

    cancelTempWire() {
        if (this.tempWire) {
            this.connectionsLayer.removeChild(this.tempWire);
            this.tempWire = null;
        }
        this.startPinInfo = null;
    }

    renderConnections() {
        this.connectionsLayer.innerHTML = '';
        this.state.circuit.connections.forEach(conn => {
            const startPos = this.getPinAbsolutePosition(conn.source, conn.sourcePin);
            const endPos = this.getPinAbsolutePosition(conn.target, conn.targetPin);
            
            const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
            path.setAttribute('class', `circuit-wire ${this.state.selectedConnectionId === conn.id ? 'selected' : ''}`);
            path.setAttribute('data-id', conn.id);
            
            // Manhattan routing
            const midX = startPos.x + (endPos.x - startPos.x) / 2;
            const d = `M ${startPos.x} ${startPos.y} L ${midX} ${startPos.y} L ${midX} ${endPos.y} L ${endPos.x} ${endPos.y}`;
            path.setAttribute('d', d);
            
            this.connectionsLayer.appendChild(path);
        });
    }
}

window.WiringUI = WiringUI;
