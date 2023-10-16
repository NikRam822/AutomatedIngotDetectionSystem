const server = 'http://127.0.0.1:5000'
const messageTimeout = 3000

var currentIdImg = '';

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

function capturePhoto() {
    const selectedCamera = document.getElementById('cameraSelect').value;
    fetch(server + `/photo/${selectedCamera}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            alert(`Photo saved along the way: ${data.photo_path}`);
            changeCamera();
            location.reload(true);
        })
        .catch(error => console.error('Error:', error));
}

function nextImage() {
    $('#success_message').text('');
    $('#decisionInput').val('');
    currentIdImg = '';

    $.ajax({
        url: server + '/image_next',
        type: 'GET',
        xhrFields: {
            withCredentials: true
        },
        success: function(data) {
            currentIdImg = data.id;
            $('#displayed_image').attr('src', data.source);
            $('#current_id').text('Current ID: ' + currentIdImg);
        },
        error: function(error) {
            console.log(error.responseText);
        }
    });
}

function getDecisionsList() {
    // TODO: Здесь надо запрашивать мапу допустимых значений дефектов
    const decisions = new Map([
        ['OK', ['#393', 'OK']], ['DROSS', ['#933', 'Dross']], ['COLOR', ['#933', 'Discolorage']], ['EMPTY', ['#993', 'No ingot']], ['BAD_IMAGE', ['#993', 'Bad image']]
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
        data: JSON.stringify({id: currentIdImg, text: key}),
        xhrFields: {
            withCredentials: true
        },
        success: function(data) {
            console.log('Submit successful');
            $('#success_message').text('Submit successful');
            setTimeout(function() { $('#success_message').text(''); }, messageTimeout);
        },
        error: function(error) {
            console.log(error.responseText);
        }
    });
}
