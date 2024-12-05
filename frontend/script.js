document.getElementById("uploadForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = new FormData();
    formData.append("file", document.getElementById("csvFile").files[0]);
    formData.append("investment_amount", document.getElementById("investmentAmount").value);
    formData.append("start_date", document.getElementById("startDate").value);
    formData.append("end_date", document.getElementById("endDate").value);

    const messageDiv = document.getElementById("message");
    messageDiv.textContent = "Processing...";

    try {
        const response = await fetch("http://127.0.0.1:8000/upload-stocks/", {
            method: "POST",
            body: formData
        });

        const result = await response.json();
        if (response.ok) {
            messageDiv.textContent = result.message;
            document.getElementById("downloadSummary").style.display = "block";
        } else {
            messageDiv.textContent = `Error: ${result.detail}`;
        }
    } catch (error) {
        messageDiv.textContent = "An error occurred while processing the request.";
    }
});

document.getElementById("downloadSummary").addEventListener("click", function () {
    window.location.href = "http://127.0.0.1:8000/download-summary/";
});
