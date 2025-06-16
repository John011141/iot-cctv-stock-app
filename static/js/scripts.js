// static/scripts.js - Final and corrected version

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functions on page load
    setupConfirmationModals();
    setupTableFilters();
    setupImagePreview();
    setupSerialNumberCounter();
    setupDefaultDate();
    setupInlineEditForm();
});

/**
 * Sets up confirmation dialogs for destructive actions.
 */
function setupConfirmationModals() {
    // Confirmation for clearing the entire stock
    const clearStockForm = document.getElementById('clearStockForm');
    if (clearStockForm) {
        clearStockForm.addEventListener('submit', function(event) {
            if (!confirm('คุณแน่ใจหรือไม่ว่าต้องการล้างสต็อกทั้งหมด? การกระทำนี้ไม่สามารถย้อนกลับได้!')) {
                event.preventDefault(); // Stop form submission if user cancels
            }
        });
    }

    // Confirmation for deleting a single product using event delegation
    document.body.addEventListener('submit', function(event) {
        if (event.target.matches('.delete-product-form')) {
            if (!confirm('คุณแน่ใจหรือไม่ว่าต้องการลบสินค้านี้?')) {
                event.preventDefault();
            }
        }
    });
}

/**
 * Sets up per-column filters for the main inventory table.
 */
function setupTableFilters() {
    const tableBody = document.getElementById('inventoryTableBody');
    const filterInputs = document.querySelectorAll('.column-filter');
    const summaryFooter = document.getElementById('summaryFooter');
    const filteredTechCount = document.getElementById('filteredTechCount');
    const techColumnFilter = document.getElementById('technicianColumnFilter');

    if (!tableBody || filterInputs.length === 0) {
        return; // Exit if necessary elements are not on the page
    }

    const applyFilters = () => {
        const filters = {};
        filterInputs.forEach(input => {
            const colIndex = input.dataset.colIndex;
            const value = input.value.toUpperCase();
            if (value) {
                filters[colIndex] = value;
            }
        });

        const rows = tableBody.getElementsByTagName('tr');
        let visibleCountForTech = 0;

        for (const row of rows) {
            let isRowVisible = true;
            for (const colIndex in filters) {
                const cell = row.cells[colIndex];
                const cellValue = cell ? cell.textContent.toUpperCase() : '';
                if (!cellValue.includes(filters[colIndex])) {
                    isRowVisible = false;
                    break;
                }
            }
            row.style.display = isRowVisible ? '' : 'none';

            // Count visible rows for the filtered technician
            if (isRowVisible && techColumnFilter && techColumnFilter.value) {
                const techCell = row.cells[6]; // Technician column
                if (techCell && techCell.textContent.toUpperCase().includes(techColumnFilter.value.toUpperCase())) {
                   visibleCountForTech++;
                }
            }
        }
        
        // Show/hide and update the summary footer
        if (techColumnFilter && techColumnFilter.value) {
            summaryFooter.style.display = 'table-footer-group'; // Show the footer
            filteredTechCount.textContent = `${visibleCountForTech} ชิ้น`;
        } else {
            summaryFooter.style.display = 'none'; // Hide the footer
        }
    };

    filterInputs.forEach(input => {
        input.addEventListener('keyup', applyFilters);
    });
}

/**
 * Sets up the image preview functionality on the product management page.
 */
function setupImagePreview() {
    const imageInput = document.getElementById('product_image_input');
    const imagePreview = document.getElementById('image_preview_container');
    
    if (!imageInput || !imagePreview) {
        return; // Exit if the elements are not on the current page
    }

    imageInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                // Set the src of the <img> tag to the selected file's data URL
                imagePreview.src = e.target.result;
            }
            reader.readAsDataURL(file); // Read the file to trigger the onload event
        }
    });
}

/**
 * Sets up a real-time counter for serial numbers in textareas.
 */
function setupSerialNumberCounter() {
    const textarea = document.getElementById('serial_numbers_bulk');
    const counter = document.getElementById('sn_counter');
    if (!textarea || !counter) return;

    const updateCounter = () => {
        const lines = textarea.value.split('\n').filter(line => line.trim() !== '');
        counter.textContent = `${lines.length} รายการ`;
    };
    textarea.addEventListener('input', updateCounter);
    updateCounter(); // Initial count on page load
}

/**
 * Sets the default value of date inputs to today.
 */
function setupDefaultDate() {
    const dateInputs = [
        document.getElementById('date_received'),
        document.getElementById('date_issued')
    ];
    dateInputs.forEach(dateInput => {
        if (dateInput && !dateInput.value) {
            dateInput.value = new Date().toISOString().split('T')[0];
        }
    });
}

/**
 * Handles the logic for the inline "Add/Edit Product" form.
 */
function setupInlineEditForm() {
    const formCard = document.getElementById('product-form-card');
    if (!formCard) return;

    const form = document.getElementById('productForm');
    const formTitle = document.getElementById('form-title');
    const actionInput = document.getElementById('form_action');
    const productIdInput = document.getElementById('product_id');
    const submitBtn = document.getElementById('submit-btn');
    const cancelBtn = document.getElementById('cancel-edit-btn');
    
    // Function to reset the form to "Add New" mode
    const resetFormToAddMode = () => {
        formTitle.textContent = 'เพิ่มสินค้าใหม่';
        submitBtn.textContent = 'เพิ่มสินค้า';
        submitBtn.className = 'btn btn-primary';
        form.reset();
        actionInput.value = 'add';
        productIdInput.value = '';
        document.getElementById('image_preview_container').src = 'https://placehold.co/200x200/eeeeee/aaaaaa?text=Preview';
        cancelBtn.style.display = 'none';
    };

    // Add event listeners to all "Edit" buttons
    document.querySelectorAll('.edit-product-btn').forEach(button => {
        button.addEventListener('click', function() {
            // Switch form to "Edit" mode
            formTitle.textContent = 'แก้ไขสินค้า';
            submitBtn.textContent = 'บันทึกการแก้ไข';
            submitBtn.className = 'btn btn-warning';
            cancelBtn.style.display = 'inline-block';

            // Populate form with data from the button's data-* attributes
            actionInput.value = 'edit';
            productIdInput.value = this.dataset.id;
            document.getElementById('name').value = this.dataset.name;
            document.getElementById('mat_code').value = this.dataset.mat_code;
            document.getElementById('image_preview_container').src = this.dataset.image_url || 'https://placehold.co/200x200/eeeeee/aaaaaa?text=Preview';
            document.getElementById('product_image_input').value = ''; // Clear file input

            // Scroll to the form for better user experience
            formCard.scrollIntoView({ behavior: 'smooth' });
        });
    });

    // Add event listener to the "Cancel Edit" button
    if (cancelBtn) cancelBtn.addEventListener('click', resetFormToAddMode);
}
