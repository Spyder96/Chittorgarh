document.addEventListener('DOMContentLoaded', function () {
    const transactionForm = document.getElementById('transaction-form');
    const ipoNameSelect = document.getElementById('ipo-name');
    const priceField = document.getElementById('price');
    const dateField = document.getElementById('date');
    const eventTypeSelect = document.getElementById('event-type');
    console.log('DOMContentLoaded event fired.');

    // Auto-populate price and date based on selected IPO
    ipoNameSelect.addEventListener('change', async function () {
        const selectedIpoName = ipoNameSelect.value;
        const response = await fetch(`/get_ipo_details/${selectedIpoName}`);
        const ipoDetails = await response.json();
        console.log('Fetched IPO Details:', ipoDetails);

        priceField.value = ipoDetails['Retail_(Min)'];
        dateField.value = ipoDetails['Closing_Date'];
    });

    // Form submission handling
    transactionForm.addEventListener('submit', async function (event) {
        event.preventDefault();

        const formData = new FormData(transactionForm);
        const data = {};

        formData.forEach((value, key) => {
            data[key] = value;
        });

        const response = await fetch('/save_transaction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const responseData = await response.json();
        alert(responseData.message);
        transactionForm.reset();
    });
});
