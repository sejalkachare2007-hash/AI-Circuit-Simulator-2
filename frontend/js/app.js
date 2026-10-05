document.addEventListener('DOMContentLoaded', async () => {
    // 1. Initialize API & UI singletons (defined globally)
    const api = window.api;
    const state = window.state;
    const componentsUI = window.componentsUI;
    
    // Load components list
    await componentsUI.init();

    // 2. Initialize Canvas & Properties
    const propertiesUI = new PropertiesUI(state, null); // Will set canvas below
    const canvas = new CircuitCanvas(state, componentsUI, propertiesUI);
    propertiesUI.canvas = canvas;
    
    // 3. Initialize Toolbar & Wiring
    const wiringUI = new window.WiringUI(state, canvas);
    window.wiringUI = wiringUI;
    const toolbarUI = new ToolbarUI(state, canvas, propertiesUI, wiringUI);
    
    // Initialize Validation
    const validationUI = new ValidationUI(state, api, canvas, wiringUI, propertiesUI);
    window.validationUI = validationUI;
    
    // Initialize AI
    const aiUI = new AIUI(state, api, canvas, wiringUI, validationUI, componentsUI);
    window.aiUI = aiUI;

    // 4. Initialize Tabs
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active classes
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Add active class
            btn.classList.add('active');
            document.getElementById(btn.dataset.tab).classList.add('active');
        });
    });

    // 5. Initial Render
    canvas.render();
    
    // 6. Render Components View Grid
    const compGrid = document.getElementById('components-view-grid');
    if (compGrid) {
        const comps = Object.values(componentsUI.componentsData);
        if (comps.length > 0) {
            compGrid.innerHTML = comps.map(c => `
                <div class="project-card">
                    <h3>${c.name}</h3>
                    <div class="project-meta">${c.category}</div>
                    <div class="project-meta">Def: ${c.default_value || ''} ${c.unit || ''}</div>
                    <p style="font-size: 11px; margin-top: 10px; color: var(--text-secondary);">${c.description || ''}</p>
                </div>
            `).join('');
        } else {
            compGrid.innerHTML = '<p style="color:red;">Failed to load components from database.</p>';
        }
    }
    
    console.log("IDE Initialized.");
});
