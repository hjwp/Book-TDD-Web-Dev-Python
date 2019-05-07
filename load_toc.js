var httpRequest = new XMLHttpRequest();
httpRequest.onreadystatechange = function() {
  if (httpRequest.readyState === XMLHttpRequest.DONE) {
    if (httpRequest.status === 200) {
      document.getElementById('header').innerHTML += httpRequest.responseText;
      var subheaders = document.getElementsByClassName('sectlevel2');
      var section;
      for (var i=0; i<subheaders.length; i++) {
        section = subheaders[i];
        if (section.innerHTML.indexOf(window.location.pathname) === -1) {
          section.style.display = 'none';
        } else {
          section.scrollIntoView && section.scrollIntoView();
        }
      }

    }
  }
};
httpRequest.open('GET', 'toc.html');
httpRequest.send();

