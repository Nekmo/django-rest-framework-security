function b64enc(buf) {
    return base64js.fromByteArray(buf)
        .replace(/\+/g, "-")
        .replace(/\//g, "_")
        .replace(/=/g, "");
}


function b64RawEnc(buf) {
    return base64js.fromByteArray(buf)
        .replace(/\+/g, "-")
        .replace(/\//g, "_");
}


function hexEncode(buf) {
    return Array.from(buf)
                .map(function(x) {
                    return ("0" + x.toString(16)).substr(-2);
				})
                .join("");
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');


function httpRequest(method, url, data, success) {
    let xmlhttp = new XMLHttpRequest();

    xmlhttp.open(method, url, true);
    xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState === XMLHttpRequest.DONE && xmlhttp.status === 200) {   // XMLHttpRequest.DONE == 4
            let response = xmlhttp.responseText;
            if(response) {
                response = JSON.parse(response);
            }
            return success(response);
        }
    };

    xmlhttp.setRequestHeader("Accept", "application/json");
    if (!csrfSafeMethod(method)) {
        xmlhttp.setRequestHeader("Content-Type", "application/json");
        xmlhttp.setRequestHeader("X-CSRFToken", csrftoken);
    }

    if(data) {
        data = JSON.stringify(data);
    }
    xmlhttp.send(data);
}


const transformCredentialCreateOptions = (credentialCreateOptionsFromServer) => {
    let {challenge, user} = credentialCreateOptionsFromServer;
    user.id = Uint8Array.from(
        atob(credentialCreateOptionsFromServer.user.id
            .replace(/\_/g, "/")
            .replace(/\-/g, "+")
        ),
        c => c.charCodeAt(0));

    challenge = Uint8Array.from(
        atob(credentialCreateOptionsFromServer.challenge
            .replace(/\_/g, "/")
            .replace(/\-/g, "+")
        ),
        c => c.charCodeAt(0));

    const transformedCredentialCreateOptions = Object.assign(
        {}, credentialCreateOptionsFromServer,
        {challenge, user});

    return transformedCredentialCreateOptions;
}


const transformNewAssertionForServer = (newAssertion) => {
    const attObj = new Uint8Array(
        newAssertion.response.attestationObject);
    const clientDataJSON = new Uint8Array(
        newAssertion.response.clientDataJSON);
    const rawId = new Uint8Array(
        newAssertion.rawId);

    const registrationClientExtensions = newAssertion.getClientExtensionResults();

    return {
        id: newAssertion.id,
        rawId: b64enc(rawId),
        type: newAssertion.type,
        attObj: b64enc(attObj),
        clientData: b64enc(clientDataJSON),
        registrationClientExtensions: JSON.stringify(registrationClientExtensions)
    };
}


const transformCredentialRequestOptions = (credentialRequestOptionsFromServer) => {
    let {challenge, allowCredentials} = credentialRequestOptionsFromServer;

    challenge = Uint8Array.from(
        atob(challenge.replace(/\_/g, "/").replace(/\-/g, "+")), c => c.charCodeAt(0));

    allowCredentials = allowCredentials.map(credentialDescriptor => {
        let {id} = credentialDescriptor;
        id = id.replace(/\_/g, "/").replace(/\-/g, "+");
        id = Uint8Array.from(atob(id), c => c.charCodeAt(0));
        return Object.assign({}, credentialDescriptor, {id});
    });

    const transformedCredentialRequestOptions = Object.assign(
        {},
        credentialRequestOptionsFromServer,
        {challenge, allowCredentials});

    return transformedCredentialRequestOptions;
};


const transformAssertionForServer = (newAssertion) => {
    const authData = new Uint8Array(newAssertion.response.authenticatorData);
    const clientDataJSON = new Uint8Array(newAssertion.response.clientDataJSON);
    const rawId = new Uint8Array(newAssertion.rawId);
    const sig = new Uint8Array(newAssertion.response.signature);
    const assertionClientExtensions = newAssertion.getClientExtensionResults();

    return {
        id: newAssertion.id,
        rawId: b64enc(rawId),
        type: newAssertion.type,
        authData: b64RawEnc(authData),
        clientData: b64RawEnc(clientDataJSON),
        signature: hexEncode(sig),
        assertionClientExtensions: JSON.stringify(assertionClientExtensions)
    };
};


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}


const webAuthnBeginRegister = function() {

    httpRequest(
        'post',
        OTP_DEVICES_API_URL + 'begin_register/',
        {
            "otp_type": 'webauthn',
            "destination_type": "device"
        },
        function (data) {
            navigator.credentials
                .create({publicKey: transformCredentialCreateOptions(data)})
                .then(res => {
                    const newAssertionForServer = transformNewAssertionForServer(res);
                    let requestData = {
                        'title': $("#device_name").val(),
                        'otp_type': 'webauthn',
                        'destination_type': 'device',
                        'data': newAssertionForServer,
                    }
                    httpRequest(
                        'post',
                        OTP_DEVICES_API_URL,
                        requestData,
                        function() {
                            alert('Verified');
                        });
                })
                .catch(console.error);
        });
}

const webAuthnAuthenticate = function (device_id) {
    httpRequest(
        'get',
        OTP_DEVICES_API_URL + device_id + '/challenge/',
        null,
        function (challenge) {
            const credencialsRequest = transformCredentialRequestOptions(challenge);
            navigator.credentials.get({
                publicKey: credencialsRequest,
            }).then(function(assertion) {
                const transformedAssertionForServer = transformAssertionForServer(assertion);
                httpRequest(
                    'post',
                    OTP_DEVICES_API_URL + device_id + '/verify/',
                    transformedAssertionForServer,
                    function () {
                        alert('Authenticated');
                    }
                );
            });
        });
}
