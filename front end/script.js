// Prevent default form submission behavior
document.getElementById("uploadForm").addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent the form from submitting and refreshing the page
    await uploadImage();
});

// Function to upload the image to the backend and handle the response
async function uploadImage() {
    const fileInput = document.getElementById("imageInput"); // Get file input element
    const file = fileInput.files[0]; // Get the uploaded file

    if (!file) {
        alert("Please select a file first.");
        return;
    }

    const formData = new FormData();
    formData.append("image", file);

    try {
        // Sending the image to the backend via POST request
        const response = await fetch("http://127.0.0.1:5000/upload", {
            method: "POST",
            body: formData,
        });

        const result = await response.json();

        if (response.ok) {
            console.log("Response from backend:", result);

            // Build HTML for extracted text
            let extractedTextHTML = `
                <h2>Extracted Text</h2>
                <p style="background-color: #f9f9f9; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                    ${result.extracted_text}
                </p>
            `;

            // Display the name after the extracted text
            let nameHTML = `
                <h3>Patient Name: ${result.name}</h3>
            `;

            // Build HTML for recognized entities
            let entitiesHTML = `
                <h2>Recognized Entities</h2>
                <table border="1" style="border-collapse: collapse; width: 100%; margin-top: 20px;">
                    <thead>
                        <tr>
                            <th style="padding: 8px; text-align: left;">Entity</th>
                            <th style="padding: 8px; text-align: left;">Label</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            // Add each entity and its label to the table
            result.entities.forEach(entity => {
                entitiesHTML += `
                    <tr>
                        <td style="padding: 8px;">${entity.text}</td>
                        <td style="padding: 8px;">${entity.label}</td>
                    </tr>
                `;
            });

            entitiesHTML += `
                    </tbody>
                </table>
            `;

            // Set the output sections to the generated HTML (including extractedTextHTML, nameHTML, and entitiesHTML)
            document.getElementById("output").innerHTML = extractedTextHTML + nameHTML + entitiesHTML;

        } else {
            console.error("Error:", result.error);
            document.getElementById("output").innerHTML = `<p>Error: ${result.error}</p>`;
        }
    } catch (error) {
        console.error("Error uploading image:", error);
        document.getElementById("output").innerHTML = `<p>Error: ${error.message}</p>`;
    }
}
