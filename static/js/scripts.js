// scripts.js - อัปเดตล่าสุดสำหรับแอปพลิเคชันสต็อกสินค้า

document.addEventListener('DOMContentLoaded', function() {
    setupConfirmationModals();
    setupTableFilters();
    setupImagePreview();
    setupSerialNumberCounter();
    setupDefaultDate();
    setupInlineEditForm();
});


/**
 * 1. ฟังก์ชันสำหรับสร้างกล่องข้อความยืนยันก่อนการลบข้อมูล
 */
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


/**
 * 2. ฟังก์ชันจัดการการกรองตารางตามคอลัมน์
 */
function setupTableFilters() {
    const tableBody = document.getElementById('inventoryTableBody');
    const filterInputs = document.querySelectorAll('.column-filter');
    const summaryFooter = document.getElementById('summaryFooter');
    const filteredTechCount = document.getElementById('filteredTechCount');
    const techColumnFilter = document.getElementById('technicianColumnFilter');

    if (!tableBody || filterInputs.length === 0) {
        return;
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

            if (isRowVisible && techColumnFilter.value) {
                visibleCountForTech++;
            }
        }
        
        if (techColumnFilter && techColumnFilter.value) {
            summaryFooter.style.display = '';
            filteredTechCount.textContent = `${visibleCountForTech} ชิ้น`;
        } else {
            summaryFooter.style.display = 'none';
        }
    };

    filterInputs.forEach(input => {
        input.addEventListener('keyup', applyFilters);
    });
}


/**
 * 3. ฟังก์ชันสำหรับแสดงภาพตัวอย่าง (Preview) ก่อนอัปโหลด
 */
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

/**
 * 4. ฟังก์ชันสำหรับนับจำนวน Serial Number ที่กรอกใน Textarea
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
    updateCounter();
}

/**
 * 5. ฟังก์ชันสำหรับตั้งค่าวันที่ปัจจุบันเป็นค่าเริ่มต้น
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
 * 6. ฟังก์ชันสำหรับจัดการฟอร์มสำหรับ เพิ่ม/แก้ไข
 */
function setupInlineEditForm() {
    const formCard = document.getElementById('product-form-card');
    if (!formCard) return;

    const form = document.getElementById('productForm');
    const formTitle = document.getElementById('form-title');
    const actionInput = document.getElementById('form_action');
    const productIdInput = document.getElementById('product_id');
    const nameInput = document.getElementById('name');
    const matCodeInput = document.getElementById('mat_code');
    const imagePreview = document.getElementById('image_preview_container');
    const submitBtn = document.getElementById('submit-btn');
    const cancelBtn = document.getElementById('cancel-edit-btn');
    const imageInput = document.getElementById('product_image_input');

    const resetFormToAddMode = () => {
        formTitle.textContent = 'เพิ่มสินค้าใหม่';
        submitBtn.textContent = 'เพิ่มสินค้า';
        submitBtn.className = 'btn btn-primary';
        form.reset();
        actionInput.value = 'add';
        productIdInput.value = '';
        imagePreview.src = 'https://placehold.co/200x200/eeeeee/aaaaaa?text=Preview';
        cancelBtn.style.display = 'none';
    };

    document.querySelectorAll('.edit-product-btn').forEach(button => {
        button.addEventListener('click', function() {
            const id = this.dataset.id;
            const name = this.dataset.name;
            const mat_code = this.dataset.mat_code;
            const image_url = this.dataset.image_url;

            formTitle.textContent = 'แก้ไขสินค้า';
            submitBtn.textContent = 'บันทึกการแก้ไข';
            submitBtn.className = 'btn btn-warning';
            cancelBtn.style.display = 'inline-block';

            actionInput.value = 'edit';
            productIdInput.value = id;
            nameInput.value = name;
            matCodeInput.value = mat_code;
            imagePreview.src = image_url || 'https://placehold.co/200x200/eeeeee/aaaaaa?text=Preview';
            imageInput.value = '';

            formCard.scrollIntoView({ behavior: 'smooth' });
        });
    });

    cancelBtn.addEventListener('click', resetFormToAddMode);
}
