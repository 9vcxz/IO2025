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


// HTML5QRCODESCANNER TEST
function onScanSuccess(decodedText, decodedResult) {
    html5QrcodeScanner.clear()
    // const video = document.querySelector('#video_element');
    // const canvas = document.createElement('canvas');
    // canvas.getContext('2d').drawImage(video, 0, 0);
    
    console.log(`QR code scanned successfuly: ${decodedText}`);

    fetch('/api/verify_qr', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            qr_code: decodedText
        })
    })
    .then(response => response.json())
    .then(data => {
        alert("Status: " + data.message);
        location.reload();
    })
}

let config = {
  fps: 10,
  qrbox: {width: 300, height: 300},
  rememberLastUsedCamera: true,
  // Only support camera scan type.
  supportedScanTypes: [Html5QrcodeScanType.SCAN_TYPE_CAMERA]
};

let html5QrcodeScanner = new Html5QrcodeScanner(
  "reader", config, /* verbose= */ false);
html5QrcodeScanner.render(onScanSuccess);
