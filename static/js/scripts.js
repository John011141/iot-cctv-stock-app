// static/scripts.js

document.addEventListener('DOMContentLoaded', function() {
    setupConfirmationModals();
    setupTableFilters();
    setupImagePreview();
    setupSerialNumberCounter();
    setupDefaultDate();
    setupInlineEditForm();
});

function setupConfirmationModals() {
    const clearStockForm = document.getElementById('clearStockForm');
    if (clearStockForm) {
        clearStockForm.addEventListener('submit', function(event) {
            if (!confirm('คุณแน่ใจหรือไม่ว่าต้องการล้างสต็อกทั้งหมด? การกระทำนี้ไม่สามารถย้อนกลับได้!')) {
                event.preventDefault();
            }
        });
    }
    document.body.addEventListener('submit', function(event) {
        if (event.target.matches('.delete-product-form')) {
            if (!confirm('คุณแน่ใจหรือไม่ว่าต้องการลบสินค้านี้?')) {
                event.preventDefault();
            }
        }
    });
}

function setupTableFilters() {
    const tableBody = document.getElementById('inventoryTableBody');
    const filterInputs = document.querySelectorAll('.column-filter');
    const summaryFooter = document.getElementById('summaryFooter');
    const filteredTechCount = document.getElementById('filteredTechCount');
    const techColumnFilter = document.getElementById('technicianColumnFilter');

    if (!tableBody || filterInputs.length === 0) return;

    const applyFilters = () => {
        const filters = {};
        filterInputs.forEach(input => {
            const colIndex = input.dataset.colIndex;
            const value = input.value.toUpperCase();
            if (value) filters[colIndex] = value;
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
            if (isRowVisible && techColumnFilter && techColumnFilter.value) {
                visibleCountForTech++;
            }
        }
        
        if (techColumnFilter && techColumnFilter.value) {
            summaryFooter.style.display = 'table-footer-group';
            filteredTechCount.textContent = `${visibleCountForTech} ชิ้น`;
        } else {
            summaryFooter.style.display = 'none';
        }
    };

    filterInputs.forEach(input => input.addEventListener('keyup', applyFilters));
}

function setupImagePreview() {
    const imageInput = document.getElementById('product_image_input');
    const imagePreview = document.getElementById('image_preview_container');
    if (!imageInput || !imagePreview) return;

    imageInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) { imagePreview.src = e.target.result; }
            reader.readAsDataURL(file);
        }
    });
}

function setupSerialNumberCounter() {
    const textarea = document.getElementById('serial_numbers_bulk');
    const counter = document.getElementById('sn_counter');
    if (!textarea || !counter) return;

    const updateCounter = () => {
        const lines = textarea.value.split('\n').filter(line => line.trim() !== '');
        counter.textContent = `${lines.length} รายการ`;
    };
    textarea.addEventListener('input', updateCounter);
    updateCounter();
}

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

function setupInlineEditForm() {
    const formCard = document.getElementById('product-form-card');
    if (!formCard) return;

    const form = document.getElementById('productForm');
    const formTitle = document.getElementById('form-title');
    const actionInput = document.getElementById('form_action');
    const productIdInput = document.getElementById('product_id');
    const submitBtn = document.getElementById('submit-btn');
    const cancelBtn = document.getElementById('cancel-edit-btn');
    
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

    document.querySelectorAll('.edit-product-btn').forEach(button => {
        button.addEventListener('click', function() {
            formTitle.textContent = 'แก้ไขสินค้า';
            submitBtn.textContent = 'บันทึกการแก้ไข';
            submitBtn.className = 'btn btn-warning';
            cancelBtn.style.display = 'inline-block';

            actionInput.value = 'edit';
            productIdInput.value = this.dataset.id;
            document.getElementById('name').value = this.dataset.name;
            document.getElementById('mat_code').value = this.dataset.mat_code;
            document.getElementById('image_preview_container').src = this.dataset.image_url || 'https://placehold.co/200x200/eeeeee/aaaaaa?text=Preview';
            document.getElementById('product_image_input').value = '';

            formCard.scrollIntoView({ behavior: 'smooth' });
        });
    });

    if (cancelBtn) cancelBtn.addEventListener('click', resetFormToAddMode);
}
