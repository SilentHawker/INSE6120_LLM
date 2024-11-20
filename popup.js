$(document).ready(function () {
  function formatSummary(summaryText) {
    // Define valid sections to filter
    const validSections = new Set([
      "Data Collection",
      "Third-Party Sharing",
      "User Control",
      "Data Retention",
      "Security Measures",
    ]);

    // Split the text into sections and overall summary
    const parts = summaryText.split("Overall,");
    const sectionsText = parts[0];
    const overallSummary = parts[1];

    console.log("sectionsText :" + sectionsText);
    // Regular expression to capture each section: title, score, details
    const sectionRegex =
      /(?:-\s*)?\*?\*?(.*?):?\s*(\d(?:\.\d+)?)(?:\/5)?\*?\*?\s*([\s\S]*?)(?=(?:\n(?:-\s*)?\*?\*?|$))/g;

    const sections = [];
    let match;

    while ((match = sectionRegex.exec(sectionsText)) !== null) {
      // Strip the ** at the end of the title if present
      let title = match[1].trim();
      title = title.replace(/\*\*$/, ""); // Removes any trailing **

      if (validSections.has(title)) {
        // Normalize the score to X/5 format
        const rawScore = parseFloat(match[2]);
        const normalizedScore = isNaN(rawScore)
          ? "0"
          : Math.min(Math.max(rawScore, 0), 5).toString();

        // Trim the details and remove any extra whitespace/indentation
        const details = match[3].replace(/^\s+/gm, "").trim();

        sections.push({
          title,
          score: normalizedScore,
          details,
        });
      } else {
        console.log(title + " is not a valid title");
      }
    }
    console.log("Sections: " + sections);
    // Clear existing content
    const summaryContainer = document.getElementById("summary");
    summaryContainer.innerHTML = '<div class="summary-container"></div>';
    const container = summaryContainer.querySelector(".summary-container");

    sections.forEach((section) => {
      const sectionElement = document.createElement("div");
      sectionElement.className = "summary-section";

      // Determine score class
      let scoreClass = "score-medium";
      const numScore = parseFloat(section.score);
      if (!isNaN(numScore)) {
        if (numScore >= 4) scoreClass = "score-high";
        else if (numScore <= 2) scoreClass = "score-low";
      }

      sectionElement.innerHTML = `
            <div class="section-header">
                <h3 class="section-title">${section.title}</h3>
                <span class="score-badge ${scoreClass}">${section.score}/5</span>
            </div>
            <p class="section-details">${section.details}</p>
        `;
      container.appendChild(sectionElement);
    });

    // Add overall summary if it exists
    if (overallSummary) {
      const overallElement = document.createElement("div");
      overallElement.className = "overall-summary";
      overallElement.innerHTML = `
            <div class="overall-title">Overall Summary</div>
            <div class="overall-content">${overallSummary.trim()}</div>
        `;
      container.appendChild(overallElement);
    }
  }
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
      $("#summary").html(`
    <div class="loading-message">
      Analyzing URL... <span class="dot-animate">do not close the extension</span>
    </div>
  `);

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
            // $("#summary").text(response.success);
            formatSummary(response.success);
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
