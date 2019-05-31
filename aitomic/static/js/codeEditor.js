var modelId = "{{modelid}}"
function updatePreprocess() {

    var data1 = {"file": "process/preprocess.py", "content": preprocessInput, "type":"py", "op": "updateFile"}
    makeAPIRequest("/fileOp/"+modelId+"/", data1).then(x=>{fullTrace()})
    
}

function readFile(file, toInput){
    var Input = document.getElementById(toInput)
    var data1 = {"file": file, "op": "readFile"}
     makeAPIRequest("/fileOp/"+modelId+"/", data1).then(x=>{Input.value = x})
}

function updatePostprocess() {
    fullTrace()
}

function makeAPIRequest(url, data){

    var miInit = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        mode: 'cors',
        body: JSON.stringify(data),
        cache: 'default'
    };

    return fetch(url, miInit)
        .then(function (response) {
            return response.text();
        })
}

function updateData() {
  fullTrace()

}

function fullTrace(){
    var inputText = document.getElementById("inputData").value
    var data1 = {"data": inputText, "until": "preprocess", "type":"any"}
    var data2 = {"data": inputText, "until": "process", "type":"any"}
    var data3 = {"data": inputText, "type":"any"}
 makeAPIRequest("/fileOp/"+modelId+"/", data1).then(x=>{document.getElementById("preprocessResult").innerHTML = x})
 makeAPIRequest("/fileOp/"+modelId+"/", data2).then(x=>{document.getElementById("modelResult").innerHTML = x})
 makeAPIRequest("/fileOp/"+modelId+"/", data3).then(x=>{document.getElementById("finalResult").innerHTML = x})
}
window.onload = function () { 
readFile("process/preprocess.py", "preprocessCode")
readFile("process/postprocess.py", "postprocessCode")
}