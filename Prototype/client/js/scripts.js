// const server = 'http://217.18.62.231:5000';
const server = 'http://127.0.0.1:5000';
const messageTimeout = 5000;

// Use localStorage to store currentIdImg
var currentIdImg = localStorage.getItem('currentIdImg') || '';
var experiments = [];

// TODO: We need to request available defects values from back-end here
const decisions = new Map([
    ['OK', ['#0c9', 'OK']], ['DROSS', ['#ff3e41', 'Dross']], ['COLOR', ['#ff3e41', 'Discolorage']], ['EMPTY', ['#36558F', 'No ingot']], ['BAD_IMAGE', ['#36558F', 'Bad image']]
]);

function showId(id) {
    $('#ingotId').text(id);
}

function initialize() {
    getExperiments()
    getAllCameras();
    getDecisionsList();
    registerListeners();
}

function sendEvent(name, attributes = null) {
    $.ajax({
        url: server + '/event',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ 'name': name, 'attributes': attributes })
    });
}

function registerListeners() {
    document.getElementById('brightness').addEventListener('input', updateBrightnessContrast);
    document.getElementById('contrast').addEventListener('input', updateBrightnessContrast);
}

function applyExperiments(values) {
    experiments = values;
    console.log("Enabled experiments: " + experiments);
    toggleHotkeys(experiments.includes('use_hotkeys'))
}

function toggleHotkeys(is_enabled) {
    var els = document.getElementsByClassName('hotkeyHint');
    var style = "display: none;";
    if (is_enabled) {
        document.addEventListener('keyup', doc_keyUp, false);
        style = "";
    }
    Array.prototype.forEach.call(els, function(el) {
        el.style = style;
    });
}

function getExperiments() {
    fetch(server + '/experiments')
        .then(response => response.json())
        .then(values => applyExperiments(values))
        .catch(error => console.error('Error:', error));
}

function getAllCameras() {
    sendEvent('get_camera_list')

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

var isCameraSetupPanelShown = false;

function toggleCameraSetup() {
    const panel = document.getElementById('cameraSetupPanel');
    const button = document.getElementById('cameraSetupButton');

    if (isCameraSetupPanelShown) {
        panel.style = "display: none;";
        button.textContent = "Setup";
        isCameraSetupPanelShown = false;
    } else {
        panel.style = "display: grid; gap: 20px;";
        button.textContent = "Apply";
        isCameraSetupPanelShown = true;
    }

    sendEvent('toggle_setup_panel', {'is_shown': isCameraSetupPanelShown})
}

function changeCamera() {
    const selectedCamera = document.getElementById('cameraSelect').value;
    const videoFeed = document.getElementById('videoFeed');

    sendEvent('change_camera', {'camera': selectedCamera})

    if (selectedCamera != '') {
        document.getElementById('captureButton').disabled = false;
        videoFeed.src = server + `/video_feed/${selectedCamera}`;
        localStorage.setItem('selectedCamera', selectedCamera);
    }
}

function saveFrame() {
    sendEvent('save_frame')

    $('#success_message_photo').text('');
    const selectedCamera = document.getElementById('cameraSelect').value;
    const brightness = document.getElementById('brightness').value;
    const contrast = document.getElementById('contrast').value;

    fetch(server + `/save_frame/${selectedCamera}?brightness=${brightness}&contrast=${contrast}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error while executing the query.');
        }
        return response.json();
    })
    .then(data => {
        var message = data.message
        if (data.success) {
            console.log('Photo successful');
            $('#success_message_photo').text(message);
            setTimeout(function () { $('#success_message_photo').text(''); }, messageTimeout);
            nextImage(true);
        } else {
            console.log('Photo failed');
            $('#success_message_photo').text(message);
            setTimeout(function () { $('#success_message_photo').text(''); }, messageTimeout);
        }
    })
    .catch(error => {
        console.error('There was an error:', error);
    });
}

function nextImage(last) {
    sendEvent('get_next_image')

    $('#success_message').text('');
    $('#decisionInput').val('');

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
    sendEvent('get_decisions_list')

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
    sendEvent('submit_mark', {'mark': key})

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

function doc_keyUp(event) {
    switch (event.key) {
        case ' ':
            saveFrame();
            break;

        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
            submitMark(Array.from(decisions.keys())[event.key - '1']);
            break;

        default:
            console.log('Key pressed: ' + event.key);
            break;
    } 
}

// Function to update brightness and contrast
function updateBrightnessContrast() {
    const brightness = document.getElementById('brightness').value;
    const contrast = document.getElementById('contrast').value;
    const videoFeed = document.getElementById('videoFeed');

    sendEvent('adjust_camera', {'brightness': brightness, 'contrast': contrast})

    videoFeed.style.filter = `brightness(${parseInt(brightness)}%) contrast(${parseFloat(contrast)})`;
}
