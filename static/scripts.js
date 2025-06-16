// scripts.js

document.addEventListener('DOMContentLoaded', function() {
    setupConfirmationModals();
    setupTableFilters();
    // (other setup functions...)
});

function setupConfirmationModals() {
    // Confirmation for clear stock
    const clearStockForm = document.getElementById('clearStockForm');
    if (clearStockForm) {
        clearStockForm.addEventListener('submit', function(event) {
            if (!confirm('คุณแน่ใจหรือไม่ว่าต้องการล้างสต็อกทั้งหมด? การกระทำนี้ไม่สามารถย้อนกลับได้!')) {
                event.preventDefault();
            }
        });
    }
    // (other confirmations...)
}

function setupTableFilters() {
    // (existing filter logic is the same)
}

// No new JS is strictly needed for the export button,
// as it's a simple link. The logic is handled by Flask.
// Keep other functions like setupImagePreview, setupSerialNumberCounter, etc.
