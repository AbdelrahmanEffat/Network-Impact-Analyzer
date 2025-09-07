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

// Add these functions at the end of the file
function setupPagination(tableId, pageSize = 50) {
    const table = document.getElementById(tableId);
    const rows = table.querySelectorAll('tbody tr');
    const pageCount = Math.ceil(rows.length / pageSize);
    let currentPage = 1;
    
    function showPage(page) {
        const start = (page - 1) * pageSize;
        const end = start + pageSize;
        
        rows.forEach((row, index) => {
            row.style.display = (index >= start && index < end) ? '' : 'none';
        });
        
        document.getElementById('pageInfo').textContent = `Page ${page} of ${pageCount}`;
        currentPage = page;
    }
    
    document.getElementById('prevPage').addEventListener('click', () => {
        if (currentPage > 1) showPage(currentPage - 1);
    });
    
    document.getElementById('nextPage').addEventListener('click', () => {
        if (currentPage < pageCount) showPage(currentPage + 1);
    });
    
    showPage(1);
}

function initializeFiltering() {
    const tables = document.querySelectorAll('.data-table');
    
    tables.forEach(table => {
        const filters = table.previousElementSibling.querySelectorAll('input');
        const rows = table.querySelectorAll('tbody tr');
        
        filters.forEach(filter => {
            filter.addEventListener('input', function() {
                const columnIndex = parseInt(this.dataset.column);
                const filterValue = this.value.toLowerCase();
                
                rows.forEach(row => {
                    const cell = row.cells[columnIndex];
                    const cellValue = cell.textContent.toLowerCase();
                    const matches = cellValue.includes(filterValue);
                    row.style.display = matches ? '' : 'none';
                });
            });
        });
    });
}