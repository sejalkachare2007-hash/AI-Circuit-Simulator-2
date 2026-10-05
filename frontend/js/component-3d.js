/**
 * Component Library & 3D Viewer Logic
 */

class ComponentLibrary3D {
    constructor() {
        this.components = [];
        this.selectedComponent = null;
        this.categories = new Set();
        
        // 3D Scene variables
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.animationId = null;
        this.currentMesh = null;
        this.autoRotate = false;
        
        this.init();
    }
    
    async init() {
        // Wait for DOM
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupUI());
        } else {
            this.setupUI();
        }
    }
    
    async setupUI() {
        this.fetchComponents();
        this.init3DScene();
        this.bindEvents();
    }
    
    async fetchComponents() {
        try {
            const res = await fetch('http://127.0.0.1:5000/api/components');
            if (res.ok) {
                this.components = await res.json();
                this.components.forEach(c => this.categories.add(c.category));
                this.populateCategories();
                this.renderList(this.components);
            }
        } catch (e) {
            console.error("Failed to fetch components:", e);
        }
    }
    
    populateCategories() {
        const select = document.getElementById('cl-category-filter');
        if (!select) return;
        select.innerHTML = '<option value="ALL">All Categories</option>';
        [...this.categories].sort().forEach(cat => {
            const opt = document.createElement('option');
            opt.value = cat;
            opt.innerText = cat;
            select.appendChild(opt);
        });
    }
    
    renderList(components) {
        const list = document.getElementById('cl-list');
        if (!list) return;
        list.innerHTML = '';
        
        if (components.length === 0) {
            list.innerHTML = '<div style="padding:15px;text-align:center;color:var(--text-secondary);">No components found</div>';
            return;
        }
        
        components.forEach(c => {
            const card = document.createElement('div');
            card.className = 'cl-card';
            card.onclick = () => this.selectComponent(c, card);
            
            card.innerHTML = `
                <div class="cl-card-title">${c.name}</div>
                <div class="cl-card-category">${c.category}</div>
                <div class="cl-card-desc" title="${c.description || ''}">${c.description || 'No description'}</div>
                <div class="cl-card-btn">View 3D →</div>
            `;
            list.appendChild(card);
        });
    }
    
    filterList() {
        const query = (document.getElementById('cl-search')?.value || '').toLowerCase();
        const category = document.getElementById('cl-category-filter')?.value || 'ALL';
        
        const filtered = this.components.filter(c => {
            const matchQuery = c.name.toLowerCase().includes(query) || (c.description && c.description.toLowerCase().includes(query));
            const matchCat = category === 'ALL' || c.category === category;
            return matchQuery && matchCat;
        });
        
        this.renderList(filtered);
    }
    
    selectComponent(component, cardEl) {
        this.selectedComponent = component;
        
        // Update active class
        document.querySelectorAll('.cl-card').forEach(el => el.classList.remove('active'));
        if (cardEl) cardEl.classList.add('active');
        
        // Update right details panel
        document.getElementById('cl-details-empty').style.display = 'none';
        document.getElementById('cl-details-content').classList.add('active');
        
        document.getElementById('cld-name').innerText = component.name;
        document.getElementById('cld-category').innerText = component.category;
        document.getElementById('cld-desc').innerText = component.description || 'N/A';
        document.getElementById('cld-default').innerText = component.default_value || 'N/A';
        document.getElementById('cld-unit').innerText = component.unit || 'N/A';
        document.getElementById('cld-sim').innerText = component.simulation_model || 'N/A';
        
        const pinsList = document.getElementById('cld-pins');
        pinsList.innerHTML = '';
        if (component.pins && component.pins.length > 0) {
            component.pins.forEach(pin => {
                pinsList.innerHTML += `
                    <div class="cl-pin-item">
                        <span class="cl-pin-name">Pin ${pin.pin_number}: ${pin.pin_name}</span>
                        <span class="cl-pin-type">Type: ${pin.pin_type || 'unknown'}</span>
                    </div>
                `;
            });
        } else {
            // Fallback to text configuration
            pinsList.innerHTML = `<div class="cl-pin-item"><span class="cl-pin-name">${component.pin_configuration || 'N/A'}</span></div>`;
        }
        
        // Render 3D Model
        this.generateProceduralModel(component);
    }
    
    init3DScene() {
        const container = document.getElementById('cl-3d-canvas');
        if (!container) return;
        
        if (typeof THREE === 'undefined') {
            document.getElementById('cl-3d-msg').innerText = "3D Preview Unavailable (Three.js not loaded)";
            return;
        }
        
        document.getElementById('cl-3d-msg').style.display = 'none';
        
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x111111);
        
        // Grid
        const gridHelper = new THREE.GridHelper(20, 20, 0x333333, 0x222222);
        this.scene.add(gridHelper);
        
        this.camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
        this.camera.position.set(5, 5, 5);
        
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        container.appendChild(this.renderer.domElement);
        
        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
        this.scene.add(ambientLight);
        
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(5, 10, 5);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.width = 1024;
        dirLight.shadow.mapSize.height = 1024;
        this.scene.add(dirLight);
        
        const fillLight = new THREE.DirectionalLight(0xabcfff, 0.3);
        fillLight.position.set(-5, 3, -5);
        this.scene.add(fillLight);
        
        if (typeof THREE.OrbitControls !== 'undefined') {
            this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
            this.controls.enableDamping = true;
            this.controls.dampingFactor = 0.05;
        }
        
        window.addEventListener('resize', () => {
            if (this.camera && this.renderer) {
                this.camera.aspect = container.clientWidth / container.clientHeight;
                this.camera.updateProjectionMatrix();
                this.renderer.setSize(container.clientWidth, container.clientHeight);
            }
        });
        
        this.animate();
    }
    
    generateProceduralModel(component) {
        if (!this.scene) return;
        
        if (this.currentMesh) {
            this.scene.remove(this.currentMesh);
            this.currentMesh = null;
        }
        
        const group = new THREE.Group();
        const type = (component.name || "").toLowerCase();
        
        if (type.includes('resistor') || type.includes('potentiometer')) {
            // Procedural Resistor
            const bodyGeo = new THREE.CylinderGeometry(0.3, 0.3, 1.5, 16);
            const bodyMat = new THREE.MeshPhongMaterial({ color: 0xd2b48c }); // Tan
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.rotation.z = Math.PI / 2;
            body.castShadow = true;
            group.add(body);
            
            // Bands
            const bandGeo = new THREE.CylinderGeometry(0.31, 0.31, 0.1, 16);
            const b1 = new THREE.Mesh(bandGeo, new THREE.MeshBasicMaterial({color: 0xff0000}));
            b1.rotation.z = Math.PI/2; b1.position.x = -0.4; group.add(b1);
            
            const b2 = new THREE.Mesh(bandGeo, new THREE.MeshBasicMaterial({color: 0x000000}));
            b2.rotation.z = Math.PI/2; b2.position.x = -0.1; group.add(b2);
            
            const b3 = new THREE.Mesh(bandGeo, new THREE.MeshBasicMaterial({color: 0xffa500}));
            b3.rotation.z = Math.PI/2; b3.position.x = 0.2; group.add(b3);
            
            // Leads
            const leadGeo = new THREE.CylinderGeometry(0.05, 0.05, 1.5, 8);
            const leadMat = new THREE.MeshStandardMaterial({color: 0x888888, metalness: 0.8, roughness: 0.3});
            const l1 = new THREE.Mesh(leadGeo, leadMat);
            l1.rotation.z = Math.PI/2; l1.position.x = -1.5; group.add(l1);
            const l2 = new THREE.Mesh(leadGeo, leadMat);
            l2.rotation.z = Math.PI/2; l2.position.x = 1.5; group.add(l2);
            
        } else if (type.includes('led')) {
            // Procedural LED
            const domeGeo = new THREE.SphereGeometry(0.5, 16, 16, 0, Math.PI*2, 0, Math.PI/2);
            const cylGeo = new THREE.CylinderGeometry(0.5, 0.5, 0.5, 16);
            const ledMat = new THREE.MeshPhongMaterial({color: 0xff0000, transparent: true, opacity: 0.8, shininess: 100});
            
            const dome = new THREE.Mesh(domeGeo, ledMat);
            dome.position.y = 0.25; group.add(dome);
            const cyl = new THREE.Mesh(cylGeo, ledMat);
            group.add(cyl);
            
            // Base ring
            const ringGeo = new THREE.CylinderGeometry(0.55, 0.55, 0.1, 16);
            const ring = new THREE.Mesh(ringGeo, ledMat);
            ring.position.y = -0.25; group.add(ring);
            
            // Leads
            const leadGeo = new THREE.CylinderGeometry(0.05, 0.05, 1.5, 8);
            const leadMat = new THREE.MeshStandardMaterial({color: 0x888888, metalness: 0.8, roughness: 0.3});
            const anode = new THREE.Mesh(leadGeo, leadMat);
            anode.position.set(0.2, -1, 0); group.add(anode);
            const cathode = new THREE.Mesh(leadGeo, leadMat);
            cathode.position.set(-0.2, -0.9, 0); group.add(cathode); // slightly shorter
            
        } else if (type.includes('capacitor')) {
            // Procedural Electrolytic Capacitor
            const cylGeo = new THREE.CylinderGeometry(0.4, 0.4, 1.2, 16);
            const bodyMat = new THREE.MeshPhongMaterial({color: 0x111111});
            const body = new THREE.Mesh(cylGeo, bodyMat);
            body.position.y = 0.6; group.add(body);
            
            // Band
            const bandGeo = new THREE.CylinderGeometry(0.41, 0.41, 1.2, 16, 1, false, 0, Math.PI/4);
            const bandMat = new THREE.MeshBasicMaterial({color: 0xaaaaaa, side: THREE.DoubleSide});
            const band = new THREE.Mesh(bandGeo, bandMat);
            band.position.y = 0.6; band.rotation.y = Math.PI; group.add(band);
            
            // Leads
            const leadGeo = new THREE.CylinderGeometry(0.05, 0.05, 1, 8);
            const leadMat = new THREE.MeshStandardMaterial({color: 0x888888, metalness: 0.8, roughness: 0.3});
            const l1 = new THREE.Mesh(leadGeo, leadMat); l1.position.set(0.15, -0.5, 0); group.add(l1);
            const l2 = new THREE.Mesh(leadGeo, leadMat); l2.position.set(-0.15, -0.4, 0); group.add(l2);
            
        } else if (type.includes('arduino') || type.includes('board') || type.includes('pico') || type.includes('esp')) {
            // Procedural Development Board (Arduino UNO style)
            const pcbGeo = new THREE.BoxGeometry(5.3, 0.1, 6.8);
            const pcbMat = new THREE.MeshPhongMaterial({color: 0x005a70}); // Teal PCB
            const pcb = new THREE.Mesh(pcbGeo, pcbMat);
            group.add(pcb);
            
            // USB
            const usbGeo = new THREE.BoxGeometry(1.2, 1.1, 1.6);
            const silverMat = new THREE.MeshStandardMaterial({color: 0xcccccc, metalness: 0.9, roughness: 0.2});
            const usb = new THREE.Mesh(usbGeo, silverMat);
            usb.position.set(-1.8, 0.6, -2.6); group.add(usb);
            
            // Barrel Jack
            const jackGeo = new THREE.BoxGeometry(0.9, 1.1, 1.3);
            const blackMat = new THREE.MeshPhongMaterial({color: 0x111111});
            const jack = new THREE.Mesh(jackGeo, blackMat);
            jack.position.set(-1.8, 0.6, 2); group.add(jack);
            
            // Headers
            const headerMat = new THREE.MeshPhongMaterial({color: 0x222222});
            const h1 = new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.5, 2.5), headerMat);
            h1.position.set(2.4, 0.3, -1.8); group.add(h1);
            const h2 = new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.5, 2.0), headerMat);
            h2.position.set(2.4, 0.3, 1.5); group.add(h2);
            const h3 = new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.5, 1.5), headerMat);
            h3.position.set(-2.4, 0.3, 1.5); group.add(h3);
            
            // Main IC
            const icGeo = new THREE.BoxGeometry(1.4, 0.2, 3.5);
            const ic = new THREE.Mesh(icGeo, blackMat);
            ic.position.set(0.5, 0.15, 1); group.add(ic);
            
        } else if (type.includes('battery')) {
            // 9V Battery
            const batGeo = new THREE.BoxGeometry(1.7, 2.6, 2.6);
            const batMat = new THREE.MeshPhongMaterial({color: 0x222222}); // Black body
            const bat = new THREE.Mesh(batGeo, batMat);
            bat.rotation.x = Math.PI/2;
            group.add(bat);
            
            const termMat = new THREE.MeshStandardMaterial({color: 0xcccccc, metalness: 0.8});
            const t1 = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.25, 0.2, 16), termMat);
            t1.position.set(0.4, 1.4, 0); group.add(t1);
            const t2 = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.2, 6), termMat);
            t2.position.set(-0.4, 1.4, 0); group.add(t2);
            
        } else if (type.includes('transistor') || type.includes('npn') || type.includes('pnp')) {
            // TO-92 Transistor
            const packGeo = new THREE.CylinderGeometry(0.3, 0.3, 0.5, 16, 1, false, 0, Math.PI);
            const packMat = new THREE.MeshPhongMaterial({color: 0x111111});
            const pack = new THREE.Mesh(packGeo, packMat);
            pack.position.y = 0.5; pack.scale.z = 0.5; group.add(pack);
            
            // Back plate
            const backGeo = new THREE.PlaneGeometry(0.6, 0.5);
            const back = new THREE.Mesh(backGeo, packMat);
            back.position.set(0, 0.5, 0); group.add(back);
            
            // Leads
            const leadGeo = new THREE.CylinderGeometry(0.02, 0.02, 0.8, 8);
            const leadMat = new THREE.MeshStandardMaterial({color: 0x888888});
            for(let i=-1; i<=1; i++){
                const l = new THREE.Mesh(leadGeo, leadMat);
                l.position.set(i*0.15, 0, 0); group.add(l);
            }
        } else {
            // Generic IC/Component fallback
            const boxGeo = new THREE.BoxGeometry(1, 0.5, 1);
            const boxMat = new THREE.MeshPhongMaterial({color: 0x333333});
            const box = new THREE.Mesh(boxGeo, boxMat);
            group.add(box);
        }
        
        group.castShadow = true;
        
        // Center the group
        const box = new THREE.Box3().setFromObject(group);
        const center = box.getCenter(new THREE.Vector3());
        group.position.sub(center);
        
        this.currentMesh = group;
        this.scene.add(this.currentMesh);
        
        // Reset camera
        this.resetCamera();
    }
    
    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());
        
        if (this.controls) this.controls.update();
        
        if (this.autoRotate && this.currentMesh) {
            this.currentMesh.rotation.y += 0.01;
        }
        
        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }
    }
    
    bindEvents() {
        document.getElementById('cl-search')?.addEventListener('input', () => this.filterList());
        document.getElementById('cl-category-filter')?.addEventListener('change', () => this.filterList());
        
        // 3D Controls
        document.getElementById('cl-btn-left')?.addEventListener('click', () => {
            if (this.currentMesh) this.currentMesh.rotation.y -= 0.2;
        });
        document.getElementById('cl-btn-right')?.addEventListener('click', () => {
            if (this.currentMesh) this.currentMesh.rotation.y += 0.2;
        });
        document.getElementById('cl-btn-zoom-in')?.addEventListener('click', () => {
            if (this.camera) this.camera.position.multiplyScalar(0.8);
        });
        document.getElementById('cl-btn-zoom-out')?.addEventListener('click', () => {
            if (this.camera) this.camera.position.multiplyScalar(1.2);
        });
        document.getElementById('cl-btn-reset')?.addEventListener('click', () => {
            this.resetCamera();
        });
        document.getElementById('cl-btn-autorotate')?.addEventListener('click', (e) => {
            this.autoRotate = !this.autoRotate;
            e.currentTarget.classList.toggle('active', this.autoRotate);
        });
        
        // Use in Design Button
        document.getElementById('cl-btn-use')?.addEventListener('click', () => {
            if (!this.selectedComponent) return;
            
            // Tell user and switch view
            if (window.showToast) window.showToast(`Selected ${this.selectedComponent.name} for design`);
            if (window.switchView) {
                window.switchView('view-design');
                
                // If the app has logic to auto-select it in the toolbar, we'd trigger it here.
                // For now, it just brings them to the workspace.
            }
        });
    }
    
    resetCamera() {
        if (this.camera && this.controls) {
            this.camera.position.set(3, 3, 3);
            this.controls.target.set(0, 0, 0);
            if (this.currentMesh) {
                this.currentMesh.rotation.set(0, 0, 0);
            }
        }
    }
}

// Initialize when imported
const cl3d = new ComponentLibrary3D();
