// Handles dynamic formset for schema columns:
// - Add new column
// - Toggle parameter blocks depending on column type
// - Soft delete columns
// - Collect parameter inputs into JSON on submit
(function () {
    // Get references to main controls
    const addBtn = document.getElementById('add-column');
    const totalInput = document.getElementById('id_form-TOTAL_FORMS');
    const columnsBlock = document.getElementById('columns');
    const emptyTpl = document.getElementById('empty-form').innerHTML;

    addBtn.addEventListener('click', function () {
        const idx = +totalInput.value;
        const newRow = emptyTpl.replace(/__prefix__/g, idx);
        columnsBlock.insertAdjacentHTML('beforeend', newRow);
        totalInput.value = idx + 1;

        const newForm = columnsBlock.querySelectorAll('.column-form')[columnsBlock.querySelectorAll('.column-form').length - 1];
        const orderInput = newForm.querySelector('input[name$="-order"]');
        if (orderInput) {
            let maxOrder = 0;
            document.querySelectorAll('.column-form input[name$="-order"]').forEach(input => {
                const val = parseInt(input.value, 10);
                if (!isNaN(val) && val > maxOrder) maxOrder = val;
            });
            orderInput.value = maxOrder + 1;
        }

        initColumnForm(newForm);
    });

    document.querySelectorAll('.column-form').forEach(initColumnForm);

    function initColumnForm(row) {
        if (!row) return;

        const typeSelect = row.querySelector('select[name$="-type"]');
        if (typeSelect) {
            const paramBlocks = {
                integer: row.querySelector('.param-integer'),
                text: row.querySelector('.param-text'),
                date: row.querySelector('.param-date'),
            };
            const toggleParams = function () {
                Object.entries(paramBlocks).forEach(([key, el]) => {
                    if (el) el.style.display = typeSelect.value === key ? 'flex' : 'none';
                });
            };
            typeSelect.addEventListener('change', toggleParams);
            toggleParams();
        }

        const delBtn = row.querySelector('.delete-btn');
        const delCheckbox = row.querySelector('input[type="checkbox"][name$="-DELETE"]');
        if (delBtn) {
            delBtn.addEventListener('click', function () {
                if (delCheckbox) {
                    delCheckbox.checked = true;
                    row.style.display = 'none';
                } else {
                    row.remove();
                    totalInput.value = document.querySelectorAll('.column-form').length;
                }
            });
        }

        const formEl = row.closest('form');
        if (formEl && !formEl.__bindParams) {
            formEl.__bindParams = true;
            formEl.addEventListener('submit', function () {
                columnsBlock.querySelectorAll('.column-form').forEach(block => {
                    const paramsInput = block.querySelector('input[name$="-params"]');
                    if (paramsInput) {
                        const data = {};
                        block.querySelectorAll('.param-input').forEach(i => {
                            if (i.value) data[i.dataset.key] = isNaN(i.value) ? i.value : +i.value;
                        });
                        paramsInput.value = JSON.stringify(data);
                    }
                });
            });
        }
    }
})();
