const optionsSelect = document.getElementById('options');

optionsSelect.addEventListener("change", () => {
    const scanParams = document.getElementById("scanParams");
    if (optionsSelect.value === "scan") {
        scanParams.style.display = "block";
    } else {
        scanParams.style.display = "none";
    }
});

const form = document.getElementById("fileUploadForm");
form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = new FormData(form);
    
    output = optionsSelect.value;
    console.log("option: " + output);

    if (output == 'select') {
        alert("Select an option");
    } else {
        // Loading
        const loadingIndicator = document.getElementById("loading");
        loadingIndicator.style.display = 'block';

        // Send data to backened
        let response1 = await fetch("http://0.0.0.0:5000/option", {
            method: "POST",
            body: output,
        });

        // Result
        let result1 = await response1.json();

        let response2 = await fetch("http://0.0.0.0:5000/upload", {
            method: "POST",
            body: data,
        });

        // Result
        let result2 = await response2.json();

        // Output data
        const codeBlock = document.getElementById('code_output');
        if (output == 'calibrate') { // calibration
            // Format the camera matrix
            let matrixString = "Camera matrix:\n";
            matrixString += result2.matrix.map(row => row.join('\t')).join('\n');

            // Format the reprojection error
            let reprojString = "\n\nReprojection error:\n" + result2.reproj_error.toFixed(4);

            // Combine both strings
            codeBlock.textContent = matrixString + reprojString;
            console.log(codeBlock.textContent)
        }
        if (output == 'face') { // face detection
            codeBlock.textContent = "Detected faces";
        }
        
        // Alert user of finished process
        console.log(result2);
        alert(result2.message);

        // Remove loading
        loadingIndicator.style.display = 'none';        
    }
});

async function streamImages() {
    while (true) {
        let imagesResponse = await fetch("http://0.0.0.0:5000/stream_images");
        let base64Image = await imagesResponse.json();

        // Create an image display area if it doesn't exist
        let imageContainer = document.getElementById('image-container');
        if (!imageContainer) {
            imageContainer = document.createElement('div');
            imageContainer.id = 'image-container';
            document.body.appendChild(imageContainer);
        }

        // Clear previous image
        imageContainer.innerHTML = '';

        // Display new image
        const img = document.createElement('img');
        img.src = `data:image/jpeg;base64,${base64Image}`;
        img.alt = 'Real-time Processed Image';
        img.style.maxWidth = '300px';
        img.style.margin = '10px';
        imageContainer.appendChild(img);

        // Delay
        await new Promise(resolve => setTimeout(resolve, 250));
    }
}
document.addEventListener("DOMContentLoaded", () => {
    streamImages();
});