let mediaStream;
const socket = io('http://127.0.0.1:5000');

async function startMedia() {
    try {
        mediaStream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false
        });
        const videoElement = document.getElementById('video');
        videoElement.srcObject = mediaStream;
        // Start streaming frames
        streamFrames(videoElement);
    } catch (error) {
        console.error('Error accessing media devices.', error);
    }
}

function streamFrames(videoElement) {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    
    // Set canvas size to a reasonable resolution to reduce data transfer
    canvas.width = 640; //videoElement.videoWidth;
    canvas.height = 480; //videoElement.videoHeight;

    function captureFrame() {
        // Draw the video frame onto the canvas with scaled size
        context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
        
        // Compress to JPEG with lower quality to reduce size
        const frameData = canvas.toDataURL('image/jpeg', 0.5);
        
        // Send the frame to the server
        socket.emit('frame', frameData);
        
        // Continue capturing frames
        requestAnimationFrame(captureFrame);
    }

    // Start capturing frames when video is ready
    videoElement.addEventListener('loadedmetadata', () => {
        captureFrame();
    });
}

// Ensure the function is called when page loads
window.onload = startMedia;