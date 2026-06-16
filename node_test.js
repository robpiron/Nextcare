
const fs = require('fs');

global.window = global;
global.localStorage = {
    store: {},
    getItem(key) {
        return this.store[key] || null;
    },
    setItem(key, value) {
        this.store[key] = String(value);
    }
};

global.document = {
    querySelector: (sel) => {
        return {
            innerHTML: '',
            appendChild: () => {}
        };
    },
    getElementById: (id) => {
        if (id === 'user-role-select') return { value: 'admin' };
        if (id === 'ris-filter-status') return { value: '' };
        if (id === 'ris-filter-doctor') return { value: '' };
        return { value: '' };
    },
    createElement: () => ({ style: {} }),
    head: { appendChild: () => {} }
};

global.DB = {
    get(key) {
        const stored = localStorage.getItem(`nextcare_v8_${key}`);
        if (stored) return JSON.parse(stored);
        return SEED_DATA[key];
    },
    set(key, val) {
        localStorage.setItem(`nextcare_v8_${key}`, JSON.stringify(val));
    }
};

global.checkTestValueIsNormal = () => 'normal';
global.setupTablePagination = (id, list) => list;

const appCode = fs.readFileSync('app.js', 'utf8');
eval(appCode);

console.log("Starting DB simulation...");
// Seed the data using the self-executing function logic
window.seedValidationHistory();

try {
    console.log("Running renderRisStudies...");
    window.renderRisStudies();
    console.log("Success! No errors.");
} catch (e) {
    console.error("Error in renderRisStudies:", e.stack);
}
