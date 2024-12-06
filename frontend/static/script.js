document
  .getElementById("uploadForm")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = new FormData();
    formData.append("file", document.getElementById("csvFile").files[0]);
    formData.append(
      "investment_amount",
      document.getElementById("investmentAmount").value
    );
    formData.append("start_date", document.getElementById("startDate").value);
    formData.append("end_date", document.getElementById("endDate").value);

    const messageDiv = document.getElementById("message");
    messageDiv.textContent = "Processing...";

    try {
      // Update the URL to match the correct endpoint in the backend
      const response = await fetch("http://127.0.0.1:8000/upload-stocks/", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      console.log(result);

      if (response.ok) {
        // Display success message
        messageDiv.textContent = "Investment summary is ready!";
        document.getElementById("downloadSummary").style.display = "block"; // Show the download button
      } else {
        // If response is not OK, display the error message returned from the backend
        messageDiv.textContent = `Error: ${
          result.error || result.message || "Unknown error"
        }`;
      }
    } catch (error) {
      // Handle any errors that occur during the fetch process
      messageDiv.textContent =
        "An error occurred while processing the request.";
      console.error(error);
    }
  });

// Handle download button click
document
  .getElementById("downloadSummary")
  .addEventListener("click", function () {
    window.location.href = "http://127.0.0.1:8000/download-summary/";
  });
