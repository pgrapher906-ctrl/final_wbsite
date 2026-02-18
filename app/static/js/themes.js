// Theme Configuration and Management
const themes = {
    blue: {
        name: 'Blue (Default)',
        colors: {
            '--primary-color': '#0088cc',
            '--secondary-color': '#00d4ff',
            '--danger-color': '#f44336',
            '--warning-color': '#ff9800',
            '--success-color': '#10b981',
            '--dark-bg': '#1a1a1a',
            '--light-bg': '#f0f9ff',
            '--border-color': '#cbd5e1',
            '--text-dark': '#0f1419',
            '--text-light': '#64748b'
        },
        navbar: 'linear-gradient(135deg, #0088cc 0%, #0066aa 100%)',
        accent: '#0088cc'
    },
    dark: {
        name: 'Dark',
        colors: {
            '--primary-color': '#60a5fa',
            '--secondary-color': '#93c5fd',
            '--danger-color': '#ef4444',
            '--warning-color': '#fbbf24',
            '--success-color': '#34d399',
            '--dark-bg': '#111827',
            '--light-bg': '#1f2937',
            '--border-color': '#374151',
            '--text-dark': '#f3f4f6',
            '--text-light': '#d1d5db'
        },
        navbar: 'linear-gradient(135deg, #1f2937 0%, #111827 100%)',
        accent: '#60a5fa'
    },
    green: {
        name: 'Green',
        colors: {
            '--primary-color': '#10b981',
            '--secondary-color': '#34d399',
            '--danger-color': '#ef4444',
            '--warning-color': '#fbbf24',
            '--success-color': '#059669',
            '--dark-bg': '#1a1a1a',
            '--light-bg': '#f0fdf4',
            '--border-color': '#bbf7d0',
            '--text-dark': '#064e3b',
            '--text-light': '#047857'
        },
        navbar: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
        accent: '#10b981'
    },
    purple: {
        name: 'Purple',
        colors: {
            '--primary-color': '#8b5cf6',
            '--secondary-color': '#a78bfa',
            '--danger-color': '#ef4444',
            '--warning-color': '#fbbf24',
            '--success-color': '#8b5cf6',
            '--dark-bg': '#1a1a1a',
            '--light-bg': '#faf5ff',
            '--border-color': '#e9d5ff',
            '--text-dark': '#4c1d95',
            '--text-light': '#6d28d9'
        },
        navbar: 'linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)',
        accent: '#8b5cf6'
    },
    orange: {
        name: 'Orange',
        colors: {
            '--primary-color': '#f97316',
            '--secondary-color': '#fb923c',
            '--danger-color': '#ef4444',
            '--warning-color': '#f97316',
            '--success-color': '#ea580c',
            '--dark-bg': '#1a1a1a',
            '--light-bg': '#fff7ed',
            '--border-color': '#fed7aa',
            '--text-dark': '#7c2d12',
            '--text-light': '#9a3412'
        },
        navbar: 'linear-gradient(135deg, #f97316 0%, #ea580c 100%)',
        accent: '#f97316'
    }
};

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', function() {
    // Load saved theme or default to blue
    const savedTheme = localStorage.getItem('selectedTheme') || 'blue';
    applyTheme(savedTheme);
    
    // Set theme selector to saved theme
    const themeSelect = document.getElementById('themeSelect');
    if (themeSelect) {
        themeSelect.value = savedTheme;
        themeSelect.addEventListener('change', function(e) {
            applyTheme(e.target.value);
            localStorage.setItem('selectedTheme', e.target.value);
        });
    }
});

// Apply theme colors to CSS variables
function applyTheme(themeName) {
    const theme = themes[themeName];
    if (!theme) {
        console.error('Theme not found:', themeName);
        return;
    }
    
    const root = document.documentElement;
    
    // Apply all color variables
    Object.entries(theme.colors).forEach(([key, value]) => {
        root.style.setProperty(key, value);
    });
    
    // Apply navbar gradient
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        navbar.style.background = theme.navbar;
    }
    
    // Update theme selector if it exists
    const themeSelect = document.getElementById('themeSelect');
    if (themeSelect && themeSelect.value !== themeName) {
        themeSelect.value = themeName;
    }
    
    console.log('Theme applied:', themeName);
}
