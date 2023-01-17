const sio = io();

sio.on('connect',() =>{
    console.log('client connected '+ sio.id);
});

sio.on('disconnect',() =>{
    console.log('client disconnected')
});


sio.on('status', (data)=>{
    console.log(data)
})
sio.on('receive', (data)=>{
    let content = ''
    console.log(data)
    sio.emit('decrypt', {sid: sio.id, datas: [data['signature'], data['msg_content'],data['author_id'],data['destination_id']]}, (result) =>{
        console.log(result)
        let element =
        `
        <div class="row">
            <div class="col-5">
                <div class="card wa-card-chat wa-card-default">`+
                    result +` 
                    <div style="text-align: right">
                        <span>`+data['msg_date']+`</span>
                    </div>
                </div>
            </div>
        </div>
        `
    document.getElementById('message_test').innerHTML +=element;
    });

})
sio.on('i_send_message', (data)=>{
    let element =
        `
        <div class="row">
            <div class="offset-6 col-5">
                <div class="card wa-card-chat wa-card-green">`+
                   data['msg_content'] + `
                
                    <div style="text-align: right">
                        <span>`+data['msg_date']+` </span>
                        <i class="large material-icons wa-icon wa-chat-icon">done_all</i>
                    </div>
                </div>
            </div>
        </div>
        `
    document.getElementById('message_test').innerHTML +=element;
})


sio.on('client_count', (count)=>{
    console.log('There are '+ count + ' connected clients.');
})

sio.on('room_count', (count)=>{
    console.log('There are '+ count + ' clients in my room.');
})

const send= document.getElementById("ContenuMessage");
function send_message() {
    var text= document.getElementById("ContenuMessage").value;
    var author= document.getElementById("author").value;
    var dest = document.getElementById("dest").value;
    var dest_pseudo = document.getElementById("dest_pseudo").value;
    document.getElementById("ContenuMessage").value='';
    sio.emit('text', {msg: text, from: author, dest:dest, room:dest_pseudo});
}

function  contact(pseudo){
    let form = document.createElement("form");
    let element1 = document.createElement("input");
    form.method = "POST";
    form.action = "/search_discussion";

    element1.value=pseudo;
    element1.name="choice";
    element1.type="hidden"
    form.appendChild(element1);
    document.body.appendChild(form);

    form.submit();
}