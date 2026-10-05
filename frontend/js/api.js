class Api {
    constructor(baseUrl = 'http://127.0.0.1:5000/api') {
        this.baseUrl = baseUrl;
    }

    async getComponents() {
        try {
            const response = await fetch(`${this.baseUrl}/components`);
            if (!response.ok) throw new Error('Failed to fetch components');
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return [];
        }
    }

    async validateCircuit(circuitData) {
        try {
            const response = await fetch(`${this.baseUrl}/circuit/validate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(circuitData)
            });
            if (!response.ok) throw new Error('Validation failed');
            return await response.json();
        } catch (error) {
            console.error('Validation API Error:', error);
            return {
                valid: false,
                errors: ["Failed to contact validation server."],
                warnings: [],
                info: []
            };
        }
    }

    async generateCircuit(prompt) {
        try {
            const response = await fetch(`${this.baseUrl}/prompt/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt })
            });
            return await response.json();
        } catch (error) {
            console.error('AI Generation API Error:', error);
            return {
                success: false,
                error: "Failed to contact AI service."
            };
        }
    }
}

const api = new Api();
window.api = api;
