document.addEventListener('DOMContentLoaded', function() {
    // Set up tab functionality
    setupTabs();
    
    // Initialize table filtering
    initializeFiltering();
});

function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            this.classList.add('active');
            const tabId = this.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
}

function initializeFiltering() {
    const tables = document.querySelectorAll('.data-table');
    
    tables.forEach(table => {
        const filters = table.previousElementSibling.querySelectorAll('input');
        
        filters.forEach(filter => {
            filter.addEventListener('input', function() {
                filterTable(table, filters);
            });
        });
    });
}

function filterTable(table, filters) {
    const rows = table.querySelectorAll('tbody tr');
    const headerCells = table.querySelectorAll('thead th');
    
    rows.forEach(row => {
        let showRow = true;
        
        filters.forEach((filter, index) => {
            if (filter.value) {
                const cell = row.cells[index];
                const cellValue = cell.textContent.toLowerCase();
                const filterValue = filter.value.toLowerCase();
                
                if (!cellValue.includes(filterValue)) {
                    showRow = false;
                }
            }
        });
        
        row.style.display = showRow ? '' : 'none';
    });
}