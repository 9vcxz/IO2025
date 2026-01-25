// QR Scanner Configuration
let video = document.querySelector('#video_element');
let uid = 0;
let isqrScanned = false;
let feedback = document.getElementById('scan_feedback')
let scannerOptions = {
    continuous: true,
    video: video,
    mirror: false,
    scanPeriod: 5,
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
        feedback.textContent = data.message || 'cos poszlo mocno nie tak';

        if(status===200){
            uid = data.employee_id;
            isqrScanned = true;

            setTimeout(() => {
                startFaceScan();
            }, 2000);
        }else{
            setTimeout(() => {
                resetScanner();
            }, 2000);
        }
    })
    .catch((err) => {
        console.error(err);
        isqrScanned = false; 
    });
})

function startFaceScan() {
    console.log(`start scanowania twarzy`);
    let imgData = captureImageFromVideo(); // base64
    console.log("Długość Base64:", imgData.length);

    if (imgData.length < 2000) {
        console.error("Błąd: Przechwycony obraz wydaje się być pusty (czarny).");
        feedback.textContent = 'Błąd kamery - spróbuj ponownie';
        resetScanner();
        return;
    }
    
    console.log("Wysyłanie żądania do /api/verify_photo z uid:", uid);
    
    fetch('/api/verify_photo', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            img_data: imgData,
            employee_id: uid
        })
    })
    .then(res => {
        console.log("Response status:", res.status);
        return res.json();
    })
    .then(data => {
        console.log("Odpowiedź verify_photo:", data);
        console.log("uid:", uid);
        if (data.status === 'success') {
            feedback.textContent = 'Poprawnie zeskanowano twarz - przekierowanie...';
            console.log(`Przekierowanie do /employee/${uid}/`);
            setTimeout(() => {
                window.location.href = `/employee/${uid}/`;
            }, 1500);
        } else {
            feedback.textContent = 'Nie rozpoznano twarzy';
            setTimeout(() => {
                resetScanner();
            }, 2000);
        }
    })
    .catch(err => {
        console.error("Błąd przy weryfikacji twarzy:", err);
        feedback.textContent = 'Błąd podczas weryfikacji twarzy';
        setTimeout(() => {
            resetScanner();
        }, 2000);
    });
}

function captureImageFromVideo() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    const ctx = canvas.getContext('2d');
    console.log(`Przechwytywanie obrazu: ${canvas.width}x${canvas.height}`);

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