document.querySelector(".summarize-btn").addEventListener("click", () => {
    console.log("Button clicked");
  
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const url = tabs[0].url;
      console.log("Active tab URL:", url);  // Log the URL
  
      fetch("http://localhost:5000/search_privacy_policy", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: url }),
      })
        .then((response) => response.json())
        .then((data) => {
          console.log("Data received from server:", data); // Log the response
          const summaryContainer = document.getElementById("summary");
          if (data.privacy_policy_url) {
            summaryContainer.textContent = `Privacy Policy URL: ${data.privacy_policy_url}`;
          } else {
            summaryContainer.textContent = "Privacy policy not found.";
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          const summaryContainer = document.getElementById("summary");
          summaryContainer.textContent = "Error fetching privacy policy.";
        });
    });
  });
  