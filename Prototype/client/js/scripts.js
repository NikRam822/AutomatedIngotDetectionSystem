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

function debounce(func, timeout = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => { func.apply(this, args); }, timeout);
    };
}

function initialize() {
    getExperiments()
    getAllCameras();
    getDecisionsList();
    nextImage();
}

function sendEvent(name, attributes = null) {
    $.ajax({
        url: server + '/event',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ 'name': name, 'attributes': attributes })
    });
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
    const container = document.getElementById('cameraSettings');

    if (isCameraSetupPanelShown) {
        panel.style = "display: none;";
        button.textContent = "Setup";
        isCameraSetupPanelShown = false;

        var children = [];
        Array.prototype.forEach.call(container.getElementsByTagName('div'), function(el) {
            children.push(el);
        });
        children.forEach((el) => container.removeChild(el));

    } else {
        const selectedCamera = document.getElementById('cameraSelect').value;
        fetch(server + `/camera_settings/${selectedCamera}`, {
            method: 'GET'
        })
        .then(response => response.json())
        .then(settings => {
            settings.forEach(object => {
                const key = object['key'];
                const row = document.createElement('div');
                row.className = 'row';
                const label = document.createElement('label');
                label.setAttribute('for', key);
                label.innerHTML = object['label'];
                const input = document.createElement('input');
                input.setAttribute('id', key);
                input.setAttribute('type', 'range');
                input.setAttribute('min', object['from']);
                input.setAttribute('max', object['to']);
                input.setAttribute('value', object['value']);
                if (object['step'] != null) {
                    input.setAttribute('step', object['step']);
                }
                const debounceHandle = debounce(changeCameraSettings);
                input.addEventListener('input', debounceHandle);
                row.appendChild(label);
                row.appendChild(input);
                container.appendChild(row);
            });
        })
        .catch(error => {
            console.error('There was an error:', error);
        });

        panel.style = "display: grid; gap: 20px;";
        button.textContent = "Apply";
        isCameraSetupPanelShown = true;
    }

    sendEvent('toggle_setup_panel', {'is_shown': isCameraSetupPanelShown})
}

function changeCameraSettings(e) {
    const selectedCamera = document.getElementById('cameraSelect').value;
    const { id, value } = e.target;

    if (selectedCamera == '' || id == '' || value == '') {
        console.log(`Missing values: camera=${selectedCamera}, key=${id}, value=${value}`);
        return;
    }

    sendEvent('adjust_camera', { 'camera': selectedCamera, id: value });

    $.ajax({
        url: server + '/camera_settings/' + selectedCamera,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ key: id, value: value }),
        xhrFields: {
            withCredentials: true
        },
        success: function (_) {},
        error: function (error) {
            console.log(error.responseText);
        }
    });
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
    const formData = new FormData();
    fetch(server + `/save_frame/${selectedCamera}`, {
        method: 'POST',
        body: formData,
        credentials: 'include'
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error while executing the query.');
            }
            return response.json();
        })
        .then(data => {
            disableDecisions(true);
            var message = data.message;
            if (data.success) {
                console.log('Photo successful');
                $('#success_message_photo').text(message);
                setTimeout(function () { $('#success_message_photo').text(''); }, messageTimeout);
            } else {
                console.log('Photo failed');
                $('#success_message_photo').text(message);
                setTimeout(function () { $('#success_message_photo').text('');}, messageTimeout);
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

    fetch(server + '/image_next', {
        method: 'GET',
        headers: {
            'Content-Type': 'image/jpeg',
        },
        credentials: 'include'
    })
        .then(response => {
            currentIdImg = response.headers.get('image_id');
            decision = response.headers.get('decision')
            localStorage.setItem('currentIdImg', currentIdImg);
            $('#ingotId').text(currentIdImg);
            $('#prediction').text(decision);
            disableDecisions(false)
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.blob();
        })
        .then(blob => {
            const imageUrl = URL.createObjectURL(blob);
            $('#displayed_image').attr('src', imageUrl);
            disableDecisions(false)})
        .catch(error => {
            console.error('Error fetching image:', error);
            currentIdImg = 0;
            localStorage.setItem('currentIdImg', currentIdImg);
            $('#displayed_image').attr('src', "images/not_found.jpg");
            $('#ingotId').text('No ingot');
            disableDecisions(true);
        });
}

function submitMark(key, is_hotkey = false) {
    sendEvent('submit_mark', {'mark': key, 'hotkey': is_hotkey});

    disableDecisions(true);

    const formData = new FormData();
    formData.append('id', currentIdImg);
    formData.append('text', key);

    fetch(server + '/submit', {
        method: 'POST',
        body: formData,
        credentials: 'include'
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            console.log('Submit successful');
            $('#success_message').text('Submit successful');
            setTimeout(function () {$('#success_message').text('');}, messageTimeout);
            nextImage();
        })
        .catch(error => {
            console.error('Error submitting mark:', error);
            disableDecisions(false);
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
