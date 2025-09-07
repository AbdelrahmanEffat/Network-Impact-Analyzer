document.addEventListener('DOMContentLoaded', function() {
    // Set up tab functionality
    setupTabs();
    
    // Initialize table filtering
    initializeFiltering();
    
    // Initialize pagination
    initializePagination();
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
    const filterInputs = document.querySelectorAll('.filter-input');
    
    filterInputs.forEach(input => {
        input.addEventListener('input', function() {
            const columnIndex = parseInt(this.getAttribute('data-column'));
            const filterValue = this.value.toLowerCase();
            const table = this.closest('.section').querySelector('.data-table');
            
            if (!table) return;
            
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const cell = row.cells[columnIndex];
                if (cell) {
                    const cellValue = cell.textContent.toLowerCase();
                    const matches = cellValue.includes(filterValue);
                    row.style.display = matches ? '' : 'none';
                }
            });
        });
    });
}

function initializePagination() {
    const tables = document.querySelectorAll('.data-table');
    
    tables.forEach(table => {
        const rows = table.querySelectorAll('tbody tr');
        const pageSize = 50;
        const pageCount = Math.ceil(rows.length / pageSize);
        let currentPage = 1;
        
        // Create pagination controls if they don't exist
        let paginationControls = table.nextElementSibling;
        if (!paginationControls || !paginationControls.classList.contains('pagination-controls')) {
            paginationControls = document.createElement('div');
            paginationControls.className = 'pagination-controls';
            paginationControls.innerHTML = `
                <button class="prev-page">Previous</button>
                <span class="page-info">Page 1 of ${pageCount}</span>
                <button class="next-page">Next</button>
            `;
            table.parentNode.insertBefore(paginationControls, table.nextSibling);
        }
        
        const prevButton = paginationControls.querySelector('.prev-page');
        const nextButton = paginationControls.querySelector('.next-page');
        const pageInfo = paginationControls.querySelector('.page-info');
        
        function showPage(page) {
            currentPage = page;
            const start = (page - 1) * pageSize;
            const end = start + pageSize;
            
            rows.forEach((row, index) => {
                row.style.display = (index >= start && index < end) ? '' : 'none';
            });
            
            pageInfo.textContent = `Page ${page} of ${pageCount}`;
            
            // Enable/disable buttons
            prevButton.disabled = currentPage === 1;
            nextButton.disabled = currentPage === pageCount;
        }
        
        prevButton.addEventListener('click', () => {
            if (currentPage > 1) showPage(currentPage - 1);
        });
        
        nextButton.addEventListener('click', () => {
            if (currentPage < pageCount) showPage(currentPage + 1);
        });
        
        showPage(1);
    });
}