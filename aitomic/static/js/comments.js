(function( w, d ) {
    let page=1;
    function getComments(page) {
       let xhttp = new XMLHttpRequest();
       xhttp.onreadystatechange = function (page) {
           return function () {
               if (this.readyState == 4 && this.status == 200) {
                   printComment(JSON.parse(this.responseText),page);
               }
           }
       }(page);
      xhttp.open("GET", "list_comments/?pagination="+page, true);
      xhttp.send();
    }

    function printComment(comments,page) {
        let containerDiv=document.createElement("div");
        containerDiv.id="comment_page_"+page;
        if(comments.length===0){
            let stopDiv=document.createElement("div");
            stopDiv.id="comment_stop_scroll";
            containerDiv.appendChild(stopDiv);
        }
        for(let index=0;index<comments.length;index++){
            const comment=comments[index];
            let commentElement=document.getElementById("comment_example").cloneNode(true);
            commentElement.hidden=false;
            commentElement.id=undefined;
            commentElement.querySelector(".comment_body").innerHTML=comment.text.replace(/</g, "&lt;").replace(/>/g, "&gt;");

            if (comment['username'] != 'Removed account'){
                commentElement.querySelector(".user_link").href="/profile/"+comment["user_id"];
            }

            commentElement.querySelector(".user_link").innerHTML=comment["username"];
                
            let xhttp = new XMLHttpRequest();
            xhttp.onreadystatechange = function (comment,commentElement) {
               return function () {
                   if (this.readyState == 4 && this.status == 200) {
                    commentElement.querySelector(".user_image").src="/profile/"+comment["user_id"]+"/photo";
                   }
               }
            }(comment,commentElement);
            xhttp.open("GET", "/profile/"+comment["user_id"]+"/photo", true);
            xhttp.send();
            commentElement.querySelector(".user_badge").hidden=!comment["badge"];
            containerDiv.appendChild(commentElement);
        }
        document.getElementById("comment_container").appendChild(containerDiv);
    }
  w.addEventListener( 'scroll', function() {
      if(!document.getElementById("comment_stop_scroll")){
          if ( w.innerHeight + w.scrollY > d.body.clientHeight - 300 ) {
            if(document.getElementById("comment_page_"+(page-1))){
                getComments(page);
                page++;
            }
          }
      }
  });
})( window, document );
