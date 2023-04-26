function updateContent(contentDiv, href=null){
  var hash = window.location.hash;
  if (href){
    hash = href;
  }
  console.log(hash);
  url = "";
  switch (hash) {
    case "#Accueil":
      url = "static/accueil.html"
      break;
    case "#Camera":
      url = "/camera.html"
      break;
    case "#Mode":
      url = "static/mode.html"
      break;
    case "#Controlleur":
      url = "static/controlleur.html"
      break;
    default:
      url = "static/accueil.html"
  }
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.open( "GET", url, true );
  xmlHttp.onreadystatechange= function() {
    if (this.readyState!==4) return;
    if (this.status!==200) return; // or whatever error handling you want
    contentDiv.innerHTML = this.responseText;
    // recharge les scripts
    var scripts = contentDiv.getElementsByTagName("script");
    for (var i = 0; i < scripts.length; i++) {
      var script = scripts[i];
      var scriptClone = document.createElement("script");
      scriptClone.type = script.type;
      if (script.innerHTML) scriptClone.innerHTML = script.innerHTML;
      else if (script.src) scriptClone.src = script.src;
      script.parentNode.replaceChild(scriptClone, script);
    }
  };
  xmlHttp.send();
}

contentDiv = document.getElementById("content").children[0]
updateContent(contentDiv)
if(window.matchMedia("(any-hover: none)").matches) {
  document.getElementById("menu").setAttribute("autohide","false")
}
for(a of document.getElementById("menu").getElementsByTagName("a")){
  a.addEventListener("click", function(event){
     updateContent(contentDiv,href=event.target.hash)
  }, false);
}
