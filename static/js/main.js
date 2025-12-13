console.log("tests")


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