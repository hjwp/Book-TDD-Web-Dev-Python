var httpRequest = new XMLHttpRequest();
httpRequest.onreadystatechange = function() {
  if (httpRequest.readyState === XMLHttpRequest.DONE) {
    if (httpRequest.status === 200) {
      document.getElementById('header').innerHTML += httpRequest.responseText;
    }
  }
};
httpRequest.open('GET', 'toc.html');
httpRequest.send();

