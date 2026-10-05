class ComponentsUI {
    constructor(api) {
        this.api = api;
        this.container = document.getElementById('component-library');
        this.componentsData = {}; // store data by id
        this.componentsList = [];
        this.currentCategory = 'ALL';
        this.searchTerm = '';
    }

    async init() {
        if (!this.container) {
            this.container = document.getElementById('component-library');
        }
        if (!this.container) {
            console.error('Component library container not found');
            return;
        }
        
        try {
            const components = await this.api.getComponents();
            if (!Array.isArray(components)) {
                this.container.innerHTML = `<div style="color:red; padding:10px;">Error: Components is not an array. Found: ${typeof components}</div>`;
                return;
            }
            if (components.length === 0) {
                this.container.innerHTML = `<div style="color:yellow; padding:10px;">Warning: 0 components fetched from API.</div>`;
                return;
            }

            this.componentsList = components;
            
            const categories = new Set();
            components.forEach(comp => {
                this.componentsData[comp.name] = comp;
                categories.add(comp.category || 'Uncategorized');
            });

            this.setupFilters(Array.from(categories).sort());
            this.renderLibrary();

        } catch (error) {
            this.container.innerHTML = `<div style="color:red; padding:10px;">Error initializing components: ${error.message}</div>`;
            console.error('Init error:', error);
        }
    }

    setupFilters(categories) {
        const select = document.getElementById('component-category-filter');
        const searchInput = document.getElementById('component-search-input');
        
        if (select) {
            select.innerHTML = '<option value="ALL">All Categories</option>';
            categories.forEach(cat => {
                const opt = document.createElement('option');
                opt.value = cat;
                opt.textContent = cat;
                select.appendChild(opt);
            });
            
            select.addEventListener('change', (e) => {
                this.currentCategory = e.target.value;
                this.renderLibrary();
            });
        }

        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchTerm = e.target.value.toLowerCase();
                this.renderLibrary();
            });
        }
    }

    renderLibrary() {
        const grouped = this.componentsList.reduce((acc, comp) => {
            const cat = comp.category || "Uncategorized";
            
            if (this.currentCategory !== 'ALL' && cat !== this.currentCategory) return acc;
            if (this.searchTerm && !comp.name.toLowerCase().includes(this.searchTerm)) return acc;
            
            acc[cat] = acc[cat] || [];
            acc[cat].push(comp);
            return acc;
        }, {});

        this.container.innerHTML = '';
        
        if (Object.keys(grouped).length === 0) {
            this.container.innerHTML = `<div style="padding: 15px; color: var(--text-secondary); text-align: center;">No components found.</div>`;
            return;
        }

        for (const [category, items] of Object.entries(grouped)) {
            const groupDiv = document.createElement('div');
            groupDiv.className = 'category-group';
            
            const header = document.createElement('div');
            header.className = 'category-header';
            header.textContent = category;
            groupDiv.appendChild(header);

            const itemsDiv = document.createElement('div');
            itemsDiv.className = 'category-items';
            
            items.forEach(comp => {
                const itemDiv = document.createElement('div');
                itemDiv.className = 'component-item';
                itemDiv.draggable = true;
                itemDiv.dataset.name = comp.name;
                
                let iconClass = 'fa-microchip';
                if (comp.category === 'POWER') iconClass = 'fa-bolt';
                else if (comp.category === 'PASSIVE') iconClass = 'fa-wave-square';
                else if (comp.category === 'OUTPUT') iconClass = 'fa-lightbulb';
                else if (comp.category === 'SENSORS') iconClass = 'fa-satellite-dish';
                
                itemDiv.innerHTML = `
                    <div style="display:flex; align-items:center; gap: 10px;">
                        <i class="fa-solid ${iconClass}" style="color: var(--accent-primary);"></i>
                        <div>
                            <div class="comp-name">${comp.name}</div>
                            <div class="comp-desc">${comp.default_value ? 'Val: ' + comp.default_value + ' ' + (comp.unit || '') : ''}</div>
                        </div>
                    </div>
                `;
                
                itemDiv.addEventListener('dragstart', (e) => {
                    e.dataTransfer.setData('text/plain', comp.name);
                });
                
                itemDiv.addEventListener('click', () => {
                    if (window.canvas && window.state) {
                        const centerX = (window.canvas.svg.clientWidth / 2 - window.canvas.panX) / window.canvas.scale;
                        const centerY = (window.canvas.svg.clientHeight / 2 - window.canvas.panY) / window.canvas.scale;
                        const x = Math.round(centerX / 20) * 20;
                        const y = Math.round(centerY / 20) * 20;
                        const newComp = window.state.addComponent(comp, x, y);
                        window.state.selectComponent(newComp.id);
                        window.canvas.render();
                        if (window.propertiesUI) window.propertiesUI.render();
                    }
                });
                
                itemsDiv.appendChild(itemDiv);
            });
            
            groupDiv.appendChild(itemsDiv);
            this.container.appendChild(groupDiv);
        }
    }

    getComponentData(name) {
        return this.componentsData[name];
    }
}

window.componentsUI = new ComponentsUI(window.api);
