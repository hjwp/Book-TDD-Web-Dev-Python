// common js code for network

//random number for dc
var ord = (ord != null ? ord : Math.random()*10000000000000000 );

//var ord = Math.round(Math.random() * 10000000000);
//var abc = Math.random() + "";
//var ord = abc.substring(2,abc.length);

//get stylesheet regardless of browser
//document.write('<link rel="STYLESHEET" type="text/css" href="http://oreillynet.com/styles/main.css">');

//Shared Functions

// Pop-Up Embedder Script by David Battino, www.batmosphere.com
function PlayerOpen(soundfiledesc,soundfilepath, width, height) {
   winPadding = 130;//for the header and caption
   if (!width){
      winWidth=320;
      width   =300;
   }
   else{
   winWidth   = winPadding  + Number(width);
   }

   if(!height){
      winHeight=190;
      height = 42;
   }
   else{
      winHeight   = winPadding  + Number(height);                              
   }


	PlayWin = window.open('','Player','width=' + winWidth + ',height=' + winHeight + ',top=0,left=0,resizable=0,scrollbars=0,titlebar=0,toolbar=0,menubar=0,status=0,directories=0');

    PlayWin.focus();

    PlayWin.document.write("<html><head><title>" + soundfiledesc + "</title>");
	PlayWin.document.write("<link rel='STYLESHEET' type='text/css' href='http://www.oreillynet.com/styles/main.css' /></head>");
	PlayWin.document.write("<body bgcolor='#ffffff'>");
    PlayWin.document.write("<b style ='font-size:18px;font-family:Verdana,sans-serif;line-height:1.5'>" + soundfiledesc + "</b>");
    PlayWin.document.write("<div align='center'><object width='" + width + "' height='" + height + "' >");
    PlayWin.document.write("<param name='SRC' value='" +  soundfilepath + "'>");
    PlayWin.document.write("<param name='AUTOPLAY' VALUE='true'>");
    PlayWin.document.write("<param name='CONTROLLER' VALUE='true'>");
    PlayWin.document.write("<embed src ='" + soundfilepath + "' autostart='true' loop='false' width='" + width + "' height='" + height + "' controller='true' bgcolor='#ffffff' >");
    PlayWin.document.write("</embed></object></div>");

    PlayWin.document.write("<p style='font-size:12px;font-family:Verdana,sans-serif;text-align:center'><a href='" + soundfilepath +"'>Download this file</a> <span style='font-size:10px'>(right-click or Option-click)</span></p>");
	PlayWin.document.write("<form><div align='center'><input type='button' value='Close this window' OnClick='javascript:window.close();'></div></form>");

    PlayWin.document.write("</body></html>");

    PlayWin.document.close(); // "Finalizes" new window
}

// Pop-Up Embedder by David Battino, www.batmosphere.com
function PopImage(filedesc,filepath,origwidth,origheight,caption) {
	winPadding = 100;//for the header and caption
	winWidth   = winPadding  + Number(origwidth);
   winHeight  = winPadding  + Number(origheight);
	
    PlayWin = window.open('','Image','width=' + winWidth + ',height=' + winHeight + ',resizable=1,scrollbars=1,titlebar=0,toolbar=0,menubar=0,status=0,directories=0');
	PlayWin.document.write("<html><head><title>" + filedesc + "</title>");
	PlayWin.document.write("<link rel='STYLESHEET' type='text/css' href='http://www.oreillynet.com/styles/main.css' /></head>");
    PlayWin.document.write("<body bgcolor='#ffffff'>");
    PlayWin.document.write("<div align='center' >");
    PlayWin.document.write("<h3>" + filedesc + "</h3>");
    PlayWin.document.write("<div style='width:" + origwidth + "px;text-align:left; '>");
    PlayWin.document.write("<img src='" + filepath + "' id='image1' name='image1' alt='" + filedesc + "' width='" + origwidth + "' height='" + origheight + "'title='" +filedesc + "' />");
    PlayWin.document.write("<p class='secondary'>" + caption + "</p>");
    PlayWin.document.write("</div>");
    PlayWin.document.write("<form><input type='button' value='Close this window' onclick='javascript:window.close()'><br /><br />");
    PlayWin.document.write("</div>");
    PlayWin.document.write("</form>");
    PlayWin.document.write("</body></html>");

    PlayWin.document.close(); // "Finalizes" new window
}

// JavaScript Document
// Pop-Up Embedder Script by David Battino, www.batmosphere.com
// v 2005-05-02a

function MediaPop(popuptitle,imgpath,imgwidth,imgheight,caption,soundpath,UniqueID) { // CONSIDER ADDING ERROR HANDLING

     var winWidth = Number(imgwidth) + 100; // imgwidth should be <651; shoot for 600
     var rawHeight = Number(imgheight) + 168 + caption.length/7; // calculate window height based on caption length
     var winHeight = Math.round(rawHeight * Math.pow(10,0))/Math.pow(10,0); // round to integer
MediaWin = window.open('',UniqueID,'width=' + winWidth + ',height=' + winHeight + ',top=0,left=0,resizable=1,scrollbars=0,titlebar=0,toolbar=0,menubar=0,status=0,directories=0,personalbar=0');
     MediaWin.focus();
     var winContent = "<html><head><title>" + popuptitle + "</title>";
     winContent += "<link rel='STYLESHEET' type='text/css' href='http://www.oreillynet.com/styles/main.css' /></head>";
     winContent += "<body style='background-color:#fff; text-align:center;padding-top:1em;'>";
     
      winContent += "<div align='center'>";
      winContent += "<div style='width: " + imgwidth + "px; margin: 0px; padding: 0px; text-align:left;'>"; // restrict width
     winContent += "<img src='" + imgpath + "' id='image1' border='0' alt='" + popuptitle + "' width='" + imgwidth + "' height='" + imgheight + " 'title='" + popuptitle + "' style='border: 2px solid #000;'/>";
     winContent += "<object width='" + imgwidth + "' height='42' >"; // add 4 to width to align controller with img border?
     winContent += "<param name='SRC' value='" +  soundpath + "'>";
     winContent += "<param name='AUTOPLAY' VALUE='true'>";
     winContent += "<param name='CONTROLLER' VALUE='true'>";
     winContent += "<param name='BGCOLOR' VALUE='#ffffff'>";
     winContent += "<embed src ='" + soundpath + "' autostart='true' loop='false' width='" + imgwidth + "' height='42' controller='true' bgcolor='#ffffff'>";
     winContent += "</embed></object>";

         winContent += "<p class='secondary'>" + caption + "</p>";
         winContent += "</div>";

     winContent += "<div style = 'font-size: 12px;font-family: Verdana,sans-serif'><a href = '" + soundpath +"'>Download audio file</a> <span style='font-size:10px'>(right-click or Option-click)</span>";
    //winContent += "<form><input type='button' value='Close this window' OnClick='javascript:window.close();'></form>"; // Close button
     winContent += " &#8226; <a href='#' OnClick='javascript:window.close();'>Close this window</a></p>";

	

     winContent += "</div></div>";
      winContent += "</body></html>";
     MediaWin.document.write(winContent); 
     MediaWin.document.close(); // "Finalizes" new window
}

//Atomz Search Code

function searchverif() { 
   if (document.searchForm.query.value.length < 1) {
       alert("Your search query is blank. Please enter a search term.");
       return false;
   } 
   return true;
}

function processQuery() {

var d = document.searchForm;
var q = d.elements['query'].value;
q = q.replace(/&quot;/g, "%22");

// set collection
d.elements['c'].value = d.elements['sp-q-1'].value; 
// set sp-q
d.elements['sp-q'].value = d.elements['query'].value;

var pat = /C\+\+/gi;
test = q.match(pat);
if (test != null) {
   d.elements['sp-q'].value = d.elements['sp-q'].value.replace(pat, "CPLUSPLUS");
   }

var pat = /C#/i;
test = q.match(pat);
if (test != null) {
   d.elements['sp-q'].value = d.elements['sp-q'].value.replace(pat, "CNUM");
   }

}

