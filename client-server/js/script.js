var socket = new WebSocket("ws://localhost:9000");

var output = '';

var name_sent = false;

socket.onopen = function (event) {
    output += '<div class="line system">Ansluten till servern. Skriv in ditt namn.</div>';
    render();
};

socket.onmessage = function(event) {
    console.log(event.data);
    var data = JSON.parse(event.data);
    handle_message(data);
}

function send(data) {
    console.log("Sending message:", data);
    socket.send(JSON.stringify(data));
}

function send_message() {
    var message_box = document.getElementById('chat-text');
    var value = message_box.value;
    console.log("Value:", value);
    if(name_sent) {
        send({
            type: 'message',
            message: value
        })
    } else {
        send({
            type: 'set_name',
            name: value
        })
        name_sent = true;
    }
    message_box.value = '';

    return false;
}

function handle_message(data) {
    switch(data.type) {
        case 'userlist':
            if (data.new) {
                output += '<div class="line info">Användaren <span class="user">'+data.new+'</span> har anslutit till chatten.</div>';
                render();
            }
            if (data.left) {
                output += '<div class="line info">Användaren <span class="user">'+data.new+'</span> har lämnat chatten.</div>';
                render();
            }

            update_userlist(data.users);
        break;
        case 'message':
            output += '<div class="line message"><span class="user">'+data.user+'</span><span class="content">'+data.message+'</span></div>'
            render();
        break;
        case 'error':
            output += '<div class="line error">Ett fel uppstod: '+data.error+'</div>';
            render();
        break;
    }
}

function render() {
    var chat_window = document.getElementById('chat-window');
    chat_window.innerHTML = output;
}

function update_userlist(users) {
    var userlist = document.getElementById('userlist');
    var html = '<ul>';
    for(var i in users) {
        var username = users[i];
        html += '<li>'+username+'</li>'
    }
    html += '<ul>';
    userlist.innerHTML = html;
}
