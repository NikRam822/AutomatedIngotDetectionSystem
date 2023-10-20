// const server = 'http://217.18.62.231:5000';
const server = 'http://127.0.0.1:5000';
const messageTimeout = 3000;

// Use localStorage to store currentIdImg
var currentIdImg = localStorage.getItem('currentIdImg') || '';

function showId(id) {
    $('#ingotId').text(id);
}

function initialize() {
    getAllCameras();
    getDecisionsList();
}

function getAllCameras() {
    fetch(server + '/camera_detection')
        .then(response => response.json())
        .then(cameras => {
            const select = document.getElementById('cameraSelect');
            cameras.forEach(camera => {
                const option = document.createElement('option');
                option.value = camera.id_camera;
                option.text = `Camera ${camera.id_camera}`;
                select.add(option);
            });

            const selectedCamera = localStorage.getItem('selectedCamera');
            if (selectedCamera) {
                select.value = selectedCamera;
            }
            changeCamera();
        })
        .catch(error => console.error('Error:', error));
}

function changeCamera() {
    const selectedCamera = document.getElementById('cameraSelect').value;
    const videoFeed = document.getElementById('videoFeed');

    if (selectedCamera != '') {
        document.getElementById('captureButton').disabled = false;
        videoFeed.src = server + `/video_feed/${selectedCamera}`;
        localStorage.setItem('selectedCamera', selectedCamera);
    }
}

function saveFrame() {
    $('#success_message_photo').text('');
    const selectedCamera = document.getElementById('cameraSelect').value;
    const brightness = document.getElementById('brightness').value;
    const contrast = document.getElementById('contrast').value;

    fetch(server + `/save_frame/${selectedCamera}?brightness=${brightness}&contrast=${contrast}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error while executing the query.');
        }
        return response.json();
    })
    .then(data => {
        console.log('Photo successful');
        $('#success_message_photo').text('Photo successful');
        setTimeout(function () { $('#success_message_photo').text(''); }, messageTimeout);
        nextImage(true);
    })
    .catch(error => {
        console.error('There was an error:', error);
    });
}


function nextImage(last) {
    $('#success_message').text('');
    $('#decisionInput').val('');

    // Параметр last
    var queryParam = last ? '?last=true' : '';

    $.ajax({
        url: server + '/image_next' + queryParam,
        type: 'GET',
        xhrFields: {
            withCredentials: true
        },
        success: function (data) {
            currentIdImg = data.id;
            localStorage.setItem('currentIdImg', currentIdImg);
            $('#displayed_image').attr('src', data.source);
            $('#ingotId').text('Ingot ID: ' + currentIdImg);
        },
        error: function (error) {
            console.log(error.responseText);
        }
    });
}

function getDecisionsList() {
    // TODO: Здесь надо запрашивать мапу допустимых значений дефектов
    const decisions = new Map([
        ['OK', ['#0c9', 'OK']], ['DROSS', ['#ff3e41', 'Dross']], ['COLOR', ['#ff3e41', 'Discolorage']], ['EMPTY', ['#36558F', 'No ingot']], ['BAD_IMAGE', ['#36558F', 'Bad image']]
    ]);
    const select = document.getElementById('decisionPanel');
    decisions.forEach((value, key) => {
        const label = document.createTextNode(value[1]);
        const option = document.createElement('button');
        option.className = 'decision';
        option.style = 'background-color: ' + value[0] + ';';
        option.onclick = () => { submitMark(key); };
        option.appendChild(label);
        select.appendChild(option);
    });
}

function submitMark(key) {
    $.ajax({
        url: server + '/submit',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ id: currentIdImg, text: key }),
        xhrFields: {
            withCredentials: true
        },
        success: function (data) {
            console.log('Submit successful');
            $('#success_message').text('Submit successful');
            setTimeout(function () { $('#success_message').text(''); }, messageTimeout);
        },
        error: function (error) {
            console.log(error.responseText);
        }
    });
}

// Function to update brightness and contrast
function updateBrightnessContrast() {
    const brightness = document.getElementById('brightness').value;
    const contrast = document.getElementById('contrast').value;
    const videoFeed = document.getElementById('videoFeed');

    videoFeed.style.filter = `brightness(${parseInt(brightness)}%) contrast(${parseFloat(contrast)})`;
}

// Call the updateBrightnessContrast function when sliders are moved
document.getElementById('brightness').addEventListener('input', updateBrightnessContrast);
document.getElementById('contrast').addEventListener('input', updateBrightnessContrast);

