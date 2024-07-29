document.getElementById('sendEmailsButton').addEventListener('click', function() {
    const csvFile = document.getElementById('csvFile').files[0];
    if (csvFile) {
        const formData = new FormData();
        formData.append('csvFile', csvFile);

        fetch('http://localhost:5000/send-emails', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.text())  // Get the response as text
        .then(text => {
            console.log('Response text:', text);  // Log the response text
            try {
                const data = JSON.parse(text);  // Attempt to parse the response text as JSON
                document.getElementById('status').textContent = data.message;
            } catch (error) {
                console.error('Error parsing JSON:', error);
                document.getElementById('status').textContent = 'Error parsing JSON: ' + error.message;
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
            document.getElementById('status').textContent = 'Error sending emails: ' + error.message;
        });
    } else {
        document.getElementById('status').textContent = 'Please upload a CSV file.';
    }
});
