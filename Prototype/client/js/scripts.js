// const server = 'http://217.18.62.231:5000';
const server = 'http://127.0.0.1:5000';
const messageTimeout = 5000;

// Use localStorage to store currentIdImg
var currentIdImg = localStorage.getItem('currentIdImg') || '';
var experiments = [];
var decisions = [];

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

function getDecisionsList() {
    sendEvent('get_decisions_list')

    const select = document.getElementById('decision_panel');
    fetch(server + '/decisions')
        .then(response => response.json())
        .then(values => {
            decisions = values;
            decisions.forEach(value => {
                const label = document.createTextNode(value['label']);
                const option = document.createElement('button');
                option.className = 'decision_' + value['type'].toLowerCase();
                option.disabled = true;
                option.onclick = () => { submitMark(value['key']); };
                option.appendChild(label);
                select.appendChild(option);
            })
        })
        .catch(error => console.error('Error:', error));
}

function disableDecisions(disabled) {
    $.each($('[class^="decision_"]'), function(index, element) {
        element.disabled = disabled;
    });
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
        disableDecisions(true)
        var message = data.message
        if (data.success) {
            console.log('Photo successful');
            $('#success_message_photo').text(message);
            setTimeout(function () { $('#success_message_photo').text(''); }, messageTimeout);
        } else {
            console.log('Photo failed');
            $('#success_message_photo').text(message);
            setTimeout(function () { $('#success_message_photo').text(''); }, messageTimeout);
        }
        nextImage()
    })
    .catch(error => {
        console.error('There was an error:', error);
    });
}

function nextImage() {
    sendEvent('get_next_image')

    $('#decisionInput').val('');
    $('#prediction').text('');

    $.ajax({
        url: server + '/image_next',
        type: 'GET',
        xhrFields: {
            withCredentials: true
        },
        success: function (data) {
            currentIdImg = data.id;
            localStorage.setItem('currentIdImg', currentIdImg);
            $('#displayed_image').attr('src', data.source);
            $('#ingotId').text(currentIdImg);
            $('#prediction').text(data.decision);
            disableDecisions(false)
        },
        error: function (error) {
            currentIdImg = 0;
            localStorage.setItem('currentIdImg', currentIdImg);
            $('#displayed_image').attr('src', "images/not_found.jpg");
            $('#ingotId').text('No ingot');
            disableDecisions(true)
        }
    });
}

function submitMark(key, is_hotkey = false) {
    sendEvent('submit_mark', {'mark': key, 'hotkey': is_hotkey})

    disableDecisions(true)

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
            nextImage()
        },
        error: function (error) {
            console.log(error.responseText);
            disableDecisions(false)
        }
    });
}

function doc_keyUp(event) {
    console.log('Key pressed: ' + event.key);
    switch (event.key) {
        case ' ':
            saveFrame();
            break;

        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
            const decision = decisions[event.key - '1'];
            console.log('Decision is ' + decision['label']);
            submitMark(decision['key'], true);
            break;

        default:
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
