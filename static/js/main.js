// if (navigator.mediaDevices.getUserMedia) {
//   navigator.mediaDevices.getUserMedia( {video: true} )
//   .then(function (stream) {
//     video.srcObject = stream;
//     console.log('poprawnie znaleziono kamere');
//   })
//   .catch (function (erro){
//     console.log('Something went wrong');
//   })
// } else {
//   console.log("getUserMedia not supported");
// }

// let feedback = document.getElementById('scan_feedback')
// let test = document.getElementById('test-button')///////////////
// test.addEventListener("click",()=>{
//     feedback.textContent='test'
// });

// QR
let video = document.querySelector('#video_element');
let uid = 0;
let isqrScanned = false;
let feedback = document.getElementById('scan_feedback')
let scannerOptions = {
    continuous: true,
    video: video,
    mirror: false,
    scanPeriod: 5,
    // captureImage: true,
    refractoryPeriod: 5000
}

let scanner = new Instascan.Scanner(scannerOptions);

Instascan.Camera.getCameras().then(cameras => {
    if (cameras.length > 0) {
        scanner.start(cameras[0]);
        console.log('Skaner QR uruchomiony');
    } else {
        feedback.textContent = 'Brak kamery!';
    }
}).catch(err => console.error('Błąd kamery:', err));


scanner.addListener("scan", (content, _b64img) => {
    console.log(`start scanowania qr kodu`);
    if (isqrScanned) return;

    console.log(`QR DETECTED: ${content}`);
    // console.log(`QR DETECTED: ${_b64img}`);          // for logging purposes 
    
    fetch('/api/verify_qr', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            qr_code: content
        })
    })
    .then(async response => {

        if (!response.ok) {
            console.warn(`Błąd serwera: ${response.status}`);
        }
        
        return response.json().then(data => {
            return { status: response.status, data: data };
        });
    })
    .then(({ status, data }) => {
        console.log("Status: " + data.message);
        if(status===200){
            uid = data.employee_id;
            isqrScanned = true;
            feedback.textContent='QR zeskanowany pomyslnie';

            scanner.stop();
            startFaceScan();

        }else if(status===400){
            feedback.textContent='QR kod zle zeskanowany prosze sprobowac ponownie';
        }else if (status===404) {
            feedback.textContent='brak QR kodu w bazie';
        }else if (status===403) {
            feedback.textContent='QR kod wygasl';
        }else{
            feedback.textContent='cos poszlo mocno nie tak'
        }
    })
    .catch((err) => {
        console.error(err);
        isqrScanned = false; 
    });
})

function startFaceScan() {
    console.log(`start scanowania twarzy`);
    setTimeout(() => {
        let imgData = captureImageFromVideo(); // base64

        fetch('/api/verify_photo', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                img_data: imgData,
                employee_id: uid
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                feedback.textContent = 'Poprawnie zeskanowano twarz';
                resetAfterSuccess();
            } else {
                feedback.textContent = 'Nie rozpoznano twarzy';
                resetScanner();
            }
        });
    }, 2000);
}

function captureImageFromVideo() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg'); // Zwraca base64
}

function resetScanner() {
    isqrScanned = false;
    uid = null;
    feedback.textContent = 'Proszę pokazać kod QR';

    scanner.start();
}

function resetAfterSuccess() {
    setTimeout(() => {
        resetScanner();
    }, 5000);
}

// cameras = [];
// Instascan.Camera.getCameras()
//     .then((availableCameras) => {
//         cameras = availableCameras;

//         if (cameras.length === 0) {
//             alert("no cameras found");
//             return; 
//         }
//         scanner.start(cameras[0])
//     })
// .catch((err) => {
//     console.error("Camera error:", err);
//     alert("Could not access camera. Please check permissions.");
// });

// // PHOTO
// button = document.getElementById("send-pic-button");
// button.addEventListener("click", sendPhoto); 
// function sendPhoto() {
//     console.log("Send pic button clicked");
//     button.removeEventListener("click", sendPhoto);     // inaczej button klika 2 razy

//     const canvas = document.createElement("canvas");
//     canvas.setAttribute("width", video.videoWidth);
//     canvas.setAttribute("height", video.videoHeight);

//     canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
//     const imgData = canvas.toDataURL('image/jpeg');

//     // uid = 9;  // test
//     if (uid !== 0) {
//         fetch('/api/verify_photo', {
//             method: 'POST',
//             headers: {'Content-Type': 'application/json'},
//             body: JSON.stringify({
//                 employee_id: uid,
//                 img_data: imgData
//             })
//         })
//         .then(response => response.json())
//         .then(data => {
//             alert("Status: " + data.message);
//             uid = 0;
//         })
//     } else {
//         alert("Scan QR code first");
//     }

//     button.addEventListener("click", sendPhoto); 
// }
//////////////////////////////////////////////////////////////////
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
