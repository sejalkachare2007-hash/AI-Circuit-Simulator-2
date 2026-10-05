class CircuitCanvas {
    constructor(state, componentsUI, propertiesUI) {
        this.state = state;
        this.componentsUI = componentsUI;
        this.propertiesUI = propertiesUI;
        this.svg = document.getElementById('circuit-canvas');
        this.transformGroup = document.getElementById('canvas-transform');
        this.componentsLayer = document.getElementById('components-layer');
        
        this.scale = 1;
        this.panX = 0;
        this.panY = 0;
        this.isPanning = false;
        this.startX = 0;
        this.startY = 0;
        
        this.draggedComponentId = null;

        this.initEvents();
    }

    initEvents() {
        this.svg.addEventListener('dragover', e => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
        });

        this.svg.addEventListener('drop', e => {
            e.preventDefault();
            const compName = e.dataTransfer.getData('text/plain');
            if (compName) {
                const compData = this.componentsUI.getComponentData(compName);
                if (compData) {
                    const rect = this.svg.getBoundingClientRect();
                    // Calculate drop coordinates factoring in pan and zoom
                    const rawX = e.clientX - rect.left;
                    const rawY = e.clientY - rect.top;
                    
                    // Snap to grid (grid size = 20)
                    let x = Math.round(((rawX - this.panX) / this.scale) / 20) * 20;
                    let y = Math.round(((rawY - this.panY) / this.scale) / 20) * 20;

                    const newComp = this.state.addComponent(compData, x, y);
                    this.state.selectComponent(newComp.id);
                    this.render();
                    this.propertiesUI.render();
                }
            }
        });

        // Panning and clicking
        this.svg.addEventListener('mousedown', e => {
            // If wiring mode is active, do not select or drag components
            if (window.wiringUI && window.wiringUI.wireMode) return;

            // Check if clicking a component
            const targetComp = e.target.closest('.circuit-component');
            if (targetComp) {
                const id = targetComp.dataset.id;
                this.state.selectComponent(id);
                this.propertiesUI.render();
                this.draggedComponentId = id;
                this.startX = e.clientX;
                this.startY = e.clientY;
                this.render();
                return;
            }

            // Otherwise, pan
            this.state.selectComponent(null);
            this.propertiesUI.render();
            this.render();
            
            if (e.button === 0 || e.button === 1) { // Left or middle click
                this.isPanning = true;
                this.startX = e.clientX - this.panX;
                this.startY = e.clientY - this.panY;
            }
        });

        window.addEventListener('mousemove', e => {
            if (window.wiringUI && window.wiringUI.wireMode) return;

            if (this.isPanning) {
                this.panX = e.clientX - this.startX;
                this.panY = e.clientY - this.startY;
                this.updateTransform();
            } else if (this.draggedComponentId) {
                const comp = this.state.circuit.components.find(c => c.id === this.draggedComponentId);
                if (comp) {
                    const dx = (e.clientX - this.startX) / this.scale;
                    const dy = (e.clientY - this.startY) / this.scale;
                    
                    let newX = Math.round((comp.x + dx) / 20) * 20;
                    let newY = Math.round((comp.y + dy) / 20) * 20;
                    
                    // Temporary visual update only for smooth dragging
                    // Actual state save happens on mouseup to avoid huge history
                    const g = this.componentsLayer.querySelector(`g[data-id="${comp.id}"]`);
                    if (g) {
                        g.setAttribute('transform', `translate(${newX},${newY}) rotate(${comp.rotation})`);
                    }
                }
            }
        });

        window.addEventListener('mouseup', e => {
            if (window.wiringUI && window.wiringUI.wireMode) return;

            this.isPanning = false;
            if (this.draggedComponentId) {
                const comp = this.state.circuit.components.find(c => c.id === this.draggedComponentId);
                if (comp) {
                    const dx = (e.clientX - this.startX) / this.scale;
                    const dy = (e.clientY - this.startY) / this.scale;
                    let newX = Math.round((comp.x + dx) / 20) * 20;
                    let newY = Math.round((comp.y + dy) / 20) * 20;
                    
                    if (newX !== comp.x || newY !== comp.y) {
                        comp.x = newX;
                        comp.y = newY;
                        this.state.saveState();
                        this.propertiesUI.render();
                    }
                }
                this.draggedComponentId = null;
                this.render();
            }
        });
        
        // Zooming with wheel
        this.svg.addEventListener('wheel', e => {
            e.preventDefault();
            const zoomFactor = 1.1;
            const direction = e.deltaY > 0 ? -1 : 1;
            
            const rect = this.svg.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            
            const oldScale = this.scale;
            if (direction > 0) this.scale *= zoomFactor;
            else this.scale /= zoomFactor;
            
            this.scale = Math.max(0.1, Math.min(this.scale, 5));
            
            // Adjust pan to zoom around mouse
            this.panX = mouseX - (mouseX - this.panX) * (this.scale / oldScale);
            this.panY = mouseY - (mouseY - this.panY) * (this.scale / oldScale);
            
            this.updateTransform();
        });
    }

    updateTransform() {
        this.transformGroup.setAttribute('transform', `matrix(${this.scale} 0 0 ${this.scale} ${this.panX} ${this.panY})`);
    }

    setZoom(scale) {
        this.scale = scale;
        this.updateTransform();
    }
    
    resetView() {
        this.scale = 1;
        this.panX = 0;
        this.panY = 0;
        this.updateTransform();
    }

    render() {
        this.componentsLayer.innerHTML = '';
        this.state.circuit.components.forEach(comp => {
            const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
            g.setAttribute('class', `circuit-component ${this.state.selectedComponentId === comp.id ? 'selected' : ''}`);
            g.setAttribute('data-id', comp.id);
            g.setAttribute('transform', `translate(${comp.x},${comp.y}) rotate(${comp.rotation})`);
            
            // Invisible bounds for easier clicking
            const bounds = document.createElementNS("http://www.w3.org/2000/svg", "rect");
            bounds.setAttribute('class', 'bounds');
            bounds.setAttribute('x', '-25');
            bounds.setAttribute('y', '-25');
            bounds.setAttribute('width', '50');
            bounds.setAttribute('height', '50');
            bounds.setAttribute('fill', 'transparent');
            bounds.setAttribute('stroke', 'transparent');
            g.appendChild(bounds);

            // Use defined symbol
            const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
            use.setAttribute('href', `#${comp.symbolId}`);
            g.appendChild(use);

            // Label (un-rotated to stay readable)
            const labelGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
            labelGroup.setAttribute('transform', `rotate(${-comp.rotation})`);
            
            const textID = document.createElementNS("http://www.w3.org/2000/svg", "text");
            textID.setAttribute('class', 'label');
            textID.setAttribute('x', '0');
            textID.setAttribute('y', '-30');
            textID.setAttribute('text-anchor', 'middle');
            textID.setAttribute('fill', 'currentColor');
            textID.setAttribute('font-size', '12px');
            textID.textContent = comp.id;
            
            const textVal = document.createElementNS("http://www.w3.org/2000/svg", "text");
            textVal.setAttribute('class', 'label');
            textVal.setAttribute('x', '0');
            textVal.setAttribute('y', '35');
            textVal.setAttribute('text-anchor', 'middle');
            textVal.setAttribute('fill', '#007acc');
            textVal.setAttribute('font-size', '10px');
            textVal.textContent = `${comp.value || ''}${comp.unit || ''}`;

            labelGroup.appendChild(textID);
            labelGroup.appendChild(textVal);
            g.appendChild(labelGroup);

            this.componentsLayer.appendChild(g);
        });
    }
}
