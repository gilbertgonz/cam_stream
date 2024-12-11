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
        let response = await fetch("http://0.0.0.0:5000/upload", {
            method: "POST",
            body: data,
        });

        // Result
        let result = await response.json();

        // Output data
        const codeBlock = document.getElementById('output');
        if (output == 'calibrate') { // calibration
            if (result.matrix) {
                // Format the camera matrix
                let matrixString = "Camera matrix:\n";
                matrixString += result.matrix.map(row => row.join('\t')).join('\n');

                // Format the reprojection error
                let reprojString = "\n\nReprojection error:\n" + result.reproj_error.toFixed(4);

                // Combine both strings
                codeBlock.textContent = matrixString + reprojString;
            }
        }
        
        // Alert user of finished process
        console.log(result);
        alert(result.message);

        // Remove loading
        loadingIndicator.style.display = 'none';        
    }
});