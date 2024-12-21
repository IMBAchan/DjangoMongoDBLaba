function deleteSupplier(event, supplierId, csrfToken) {
    event.preventDefault();  // Зупиняємо стандартну поведінку форми

    fetch('', {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'supplier_id': supplierId
        })
    })
    .then(response => {
        if (response.ok) {
            location.reload();
        } else {
            alert('Помилка при видаленні постачальника.');
        }
    });
}
