function getRandomFromArray(ranNum, array) {
    return array[Math.floor(ranNum * (array.length) )];
}
function removeElement(elementId) {
    // Removes an element from the document
    var element = document.getElementById(elementId);
    element.parentNode.removeChild(element);
}

function generateError(error) {
    let data={
        members:{
            "daniel":{
                name:"Daniel",
                normal:"static/img/team/dani.jpg",
                scare:"static/img/team/scared/dani.jpg"
            },
            "juanmi":{
                name:"Juan Miguel",
                normal:"static/img/team/juanmi.jpg",
                scare:"static/img/team/scared/juanmi.png"
            },
            "manu":{
                name:"Manuel Jesús",
                normal:"static/img/team/manu.jpg",
                scare:"static/img/team/scared/manu.png"
            },
            "ale":{
                name:"Alejandro",
                normal:"static/img/team/ale.jpg",
                scare:"static/img/team/scared/ale.png"
            },
            "luis":{
                name:"Luis",
                normal:"static/img/team/luis.jpg",
                scare:"static/img/team/scared/luis.png"
            },
            "camila":{
                name:"Camila",
                normal:"static/img/team/camila.jpg",
                scare:"static/img/team/scared/camila.png"
            },
            "antonio":{
                name:"Antonio",
                normal:"static/img/team/antonio.jpg",
                scare:"static/img/team/scared/antonio.png"
            },
            "eva":{
                name:"Eva",
                normal:"static/img/team/eva.jpg",
                scare:"static/img/team/eva.png"
            },
            "jorge":{
                name:"Jorge",
                normal:"static/img/team/jorge.jpg",
                scare:"static/img/team/scared/jorge.png"
            },
            "claudia":{
                name:"Claudia",
                normal:"static/img/team/claudia.jpg",
                scare:"static/img/team/scared/claudia.png"
            }
        },
        sides:{
          "left":["daniel","camila","luis","jorge","antonio","manu","ale"], "center":["daniel","claudia","claudia","camila","luis","juanmi","jorge","antonio","manu","ale"],"right":["daniel","camila","juanmi","jorge","antonio","manu","ale"]
        },
        phrases:{
            employee:[
                {en:"team of highly trained monkeys",es:"nuestro equipo de monos altamente cualificados"},
                {en:"dysfunctional family",es:"nuestra familia disfuncional"},
                {en:"mindless slaves",es:"nuestros esclavos descerebrados"},
                {en:"poorly trained workers",es:"nuestros trabajadores sin titular"},
                {en:"stackoverflow copy team",es:"nuestro equipo de copiadores de stackoverflow"},
                {en:"underpaid interns",es:"nuestros becarios malpagados"},
            ],
            fired:[
                {en:"promoted to customer",es:"ser ascendido a cliente"},
                {en:"expelled from this dimension",es:"ser expulsado de esta dimensión"},
                {en:"jobn't",es:"estar distrabajando"},
                {en:"sacrificed to our god, Jon Skeet",es:"ser sacrificado a nuestro dios, Jon Skeet"},
                {en:"gone for a long time",es:"irse fuera por mucho tiempo"},
                {en:"sent to the ranch",es:"ser enviado al rancho"},
                {en:"removed from existence",es:"ser eliminado de la existencia"},
                {en:"uninstalled from the company",es:"ser desinstalado de esta empresa"},
            ]
        },
        errors:{
            "404":[
                {en:"Hey, you're not supposed to be here!",es:"Eh! ¿Qué crees que estás haciendo aquí?"},
                {en:"How did you even get here?",es:"¿Cómo has llegado hasta aquí?"},
                {en:"I think the compass broke...",es:"Creo que se nos ha roto la brújula..."},
                {en:"Where are you?",es:"¿Dónde estás?"},
                {en:"OMG, lost again...",es:"Oh dios mío, otra vez nos hemos perdido..."},
                {en:"I think we were supposed to go the third one to the right.",es:"Creo que era la tercera a la derecha."},
                {en:"I think you're not in the right neighbourhood, pal.",es:"Este no es tu barrio, amigo."},
            ],
            "500":[
                {en:"OOPSIE WOOPSIE!! Uwu We made a fucky wucky!!",es:"Uchi wuchi!! Uwu la hemows linyado!!"},
                {en:"This wasn't supposed to happen!",es:"Puff, pues esto no debería de pasar!"},
                {en:"Oh no, the server died!",es:"Oh no, el servidor ha petado!"},
                {en:"I smell a bit of fire on the server room...",es:"¿No huele como a humo en la habitación de los servidores?"},
                {en:"I think the server is drinking bleach...",es:"Me parece que el servidor está bebiendo lejía..."},
                {en:"Maybe one of the web designers tried to do a bit of backend?",es:"Igual uno de los diseñadores ha tocado el backend y pasa lo que pasa..."},
            ]
        }
    }
    let language=getLanguageToUse();
    let error_message="Error "+error+": "+getRandomFromArray(Math.random(),data.errors[error])[language];
    let apology;
    if(language==="es"){
        apology="¡Lo sentimos por este inconveniente! Para castigar a "+getRandomFromArray(Math.random(),data.phrases.employee)[language]+", uno de ellos debería "+getRandomFromArray(Math.random(),data.phrases.fired)[language]+":";
    }else{
        apology="We are sorry for this inconvenience! To punish our "+getRandomFromArray(Math.random(),data.phrases.employee)[language]+", one of them should be "+getRandomFromArray(Math.random(),data.phrases.fired)[language]+":";
    }
    let members={
        left:data.members[getRandomFromArray(Math.random(),data.sides.left)]
    }
    function getMemberCenter() {
        members.center=data.members[getRandomFromArray(Math.random(),data.sides.center)];
        if(members.left.name===members.center.name){
            getMemberCenter();
        }
    }
    getMemberCenter();
    function getMemberRight() {
        members.right=data.members[getRandomFromArray(Math.random(),data.sides.right)];
        if(members.left.name===members.right.name||members.center.name===members.right.name){
            getMemberRight();
        }
    }
    getMemberRight();
    return {error_message,apology,members};
}


let error=generateError(document.getElementById("error").innerHTML);

removeElement("error");
document.getElementById("error_message").innerHTML=error.error_message;
document.getElementById("apology").innerHTML=error.apology;
document.getElementById("error_container").hidden=false;
for (const key in error.members) {
    if (error.members.hasOwnProperty(key)) {
        const element = error.members[key];
        const keyIn= key+"_employee";
        let div=document.getElementById(keyIn);
        let image=document.getElementById("image_"+keyIn);
        let button=document.getElementById("button_"+keyIn);
        button.innerHTML=element.name;
        button.onclick=function () {
            document.getElementById("punish_screen").classList.add("is-active");
        }
        image.src=element.normal;
        div.onmouseover=function (image,element) {
            return function () {
                image.src=element.scare;
            }
        }(image,element);
        div.onmouseout=function (image,element) {
            return function () {
                image.src=element.normal;
            }
        }(image,element);
    }
}