$(document).ready(function () {
  // Show error alert with custom message
  function showError(message, title = "Error") {
    const alert = document.getElementById("errorAlert");
    const alertTitle = alert.querySelector(".alert-title");
    const alertMessage = alert.querySelector(".alert-message");

    alertTitle.textContent = title;
    alertMessage.textContent = message;
    alert.classList.add("show");
  }

  // Close error alert
  function closeAlert() {
    const alert = document.getElementById("errorAlert");
    alert.classList.remove("show");
  }

  // Add click handler for close button using jQuery
  $(".alert-close").on("click", function () {
    closeAlert();
  });

  $("#sum-btn").on("click", async function (event) {
    event.preventDefault();
    console.log("Button clicked");

    try {
      // Get the current tab URL
      const tabs = await chrome.tabs.query({
        active: true,
        currentWindow: true,
      });

      if (!tabs || !tabs[0] || !tabs[0].url) {
        throw new Error("Could not get current URL");
      }

      const url = tabs[0].url;
      $("#summary").text("Analyzing URL...");

      // Make the AJAX call to backend
      $.ajax({
        url: "http://localhost:8000/search_privacy_policy",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({
          website_url: url,
        }),
        success: function (response) {
          if (response.error) {
            // FLask-specific errors
            showError("Error: " + response.error);
            $("#summary").text("...");
          } else {
            $("#summary").text(response.success);
          }
        },
        // AJAX-specific errors (network issues, server problems, etc.)
        error: function (jqXHR, textStatus, errorThrown) {
          // jqXHR: jQuery XMLHttpRequest object with details about the failed request
          // textStatus: String describing the type of error (timeout, error, abort, etc)
          // errorThrown: The actual error message from the server

          console.error("AJAX Error Details:", {
            status: jqXHR.status,
            statusText: jqXHR.statusText,
            responseText: jqXHR.responseText,
            errorType: textStatus,
            errorMessage: errorThrown,
          });

          // Show user-friendly error based on the status code
          let userMessage;
          switch (jqXHR.status) {
            case 404:
              userMessage = "Server endpoint not found";
              break;
            case 500:
              userMessage = "Server error occurred";
              break;
            case 0:
              userMessage = "Could not connect to the server";
              break;
            default:
              userMessage = "An error occurred while processing your request";
          }
          showError("Error: " + userMessage);
          $("#summary").text("...");
        },
      });
    } catch (error) {
      console.error("JavaScript Error:", {
        name: error.name,
        message: error.message,
        stack: error.stack,
      });
      showError("Error: " + error.message);
      $("#summary").text("...");
    }
  });
});
