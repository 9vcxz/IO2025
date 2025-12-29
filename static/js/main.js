let video = document.querySelector('#video_element');

if (navigator.mediaDevices.getUserMedia) {
  navigator.mediaDevices.getUserMedia( {video: true} )
  .then(function (stream) {
    video.srcObject = stream;
  })
  .catch (function (erro){
    console.log('Something went wrong');
  })
} else {
  console.log("getUserMedia not supported");
}


// QR
let uid = 0;
let scannerOptions = {
    continuous: true,
    video: video,
    mirror: false,
    scanPeriod: 5,
    captureImage: true,
    refractoryPeriod: 5000
}

let scanner = new Instascan.Scanner(scannerOptions);

scanner.addListener("scan", (content, _b64img) => {
    console.log(`QR DETECTED: ${content}`);
    // console.log(`QR DETECTED: ${_b64img}`);          // for logging purposes 

    fetch('/api/verify_qr', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            qr_code: content
        })
    })
    .then(response => response.json())
    .then(data => {
        alert("Status: " + data.message);
        uid = data.employee_id;
    })
})

cameras = [];
Instascan.Camera.getCameras()
    .then((availableCameras) => {
        cameras = availableCameras;

        if (cameras.length === 0) {
            alert("no cameras found");
            return; 
        }
        scanner.start(cameras[0])
    })
.catch((err) => {
    console.error("Camera error:", err);
    alert("Could not access camera. Please check permissions.");
});

// PHOTO
button = document.getElementById("send-pic-button");
button.addEventListener("click", sendPhoto); 
function sendPhoto() {
    console.log("Send pic button clicked");
    button.removeEventListener("click", sendPhoto);     // inaczej button klika 2 razy

    const canvas = document.createElement("canvas");
    canvas.setAttribute("width", video.videoWidth);
    canvas.setAttribute("height", video.videoHeight);

    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    const imgData = canvas.toDataURL('image/jpeg');

    // uid = 9;  // test
    if (uid !== 0) {
        fetch('/api/verify_photo', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                employee_id: uid,
                img_data: imgData
            })
        })
        .then(response => response.json())
        .then(data => {
            alert("Status: " + data.message);
            uid = 0;
        })
    } else {
        alert("Scan QR code first");
    }

    button.addEventListener("click", sendPhoto); 
}

// HTML5QRCODESCANNER TEST
// function onScanSuccess(decodedText, decodedResult) {
//     html5QrcodeScanner.clear()
//     // const video = document.querySelector('#video_element');
//     // const canvas = document.createElement('canvas');
//     // canvas.getContext('2d').drawImage(video, 0, 0);
    
//     console.log(`QR code scanned successfuly: ${decodedText}`);

//     fetch('/api/verify_qr', {
//         method: 'POST',
//         headers: {'Content-Type': 'application/json'},
//         body: JSON.stringify({
//             qr_code: decodedText
//         })
//     })
//     .then(response => response.json())
//     .then(data => {
//         alert("Status: " + data.message);
//         location.reload();
//     })
// }

// let config = {
//   fps: 10,
//   qrbox: {width: 300, height: 300},
//   rememberLastUsedCamera: true,
//   // Only support camera scan type.
//   supportedScanTypes: [Html5QrcodeScanType.SCAN_TYPE_CAMERA]
// };

// let html5QrcodeScanner = new Html5QrcodeScanner(
//   "reader", config, /* verbose= */ false);
// html5QrcodeScanner.render(onScanSuccess);
