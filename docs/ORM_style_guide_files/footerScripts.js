/*
(C) Copyright MarketLive. 2006. All rights reserved.
MarketLive is a trademark of MarketLive, Inc.
Warning: This computer program is protected by copyright law and international treaties.
Unauthorized reproduction or distribution of this program, or any portion of it, may result
in severe civil and criminal penalties, and will be prosecuted to the maximum extent
possible under the law.
*/

/* ************************************************************************************************** */
/* common.js */
/* ************************************************************************************************** */

// global AJAX_TILE object, which holds the request object ("req")
// and the dom pointer to the tile's container object ("tileContainer")
var AJAX_TILE = new Object();

/**
 * An ajax request handler that swaps out the current AJAX_TILE's HTML with the HTML returned
 */
function tileChangeReq(){
	// only continue if the req is "loaded"
  if (AJAX_TILE.req.readyState == 4) {
  	// only continue if the status is "OK"
    if (AJAX_TILE.req.status == 200) {
    	// swap out the html
			AJAX_TILE.tileContainer.innerHTML = AJAX_TILE.req.responseText;
    }
  }
}

/**
 * Initialize an ajax request to update a tile's display.
 * @param {String} sTileContainerID A DOM object ID string.
 * @param {String} sURL A requst url.
 */
function updateTileDisplay(sTileContainerID, sURL){
	// clean up the old AJAX_TILE object
	AJAX_TILE = new Object();
	AJAX_TILE.req = false;
	AJAX_TILE.tileContainer = null;

	// first try for the native XMLHttpRequest
  if(window.XMLHttpRequest) {
  	try {
			AJAX_TILE.req = new XMLHttpRequest();
    } catch(e) {
			AJAX_TILE.req = false;
    }

  // try for IE/Windows ActiveX XMLHTTP
  } else if(window.ActiveXObject) {
  	try {
    	AJAX_TILE.req = new ActiveXObject("Msxml2.XMLHTTP");
    } catch(e) {
    	try {
      	AJAX_TILE.req = new ActiveXObject("Microsoft.XMLHTTP");
      } catch(e) {
      	AJAX_TILE.req = false;
      }
		}
  }

  // continue if we've managed to set up a request object
	if(AJAX_TILE.req) {
		// set the dom pointer object
		AJAX_TILE.tileContainer = document.getElementById(sTileContainerID);
		// set up the onreadystatechange event handle
		AJAX_TILE.req.onreadystatechange = tileChangeReq;
		AJAX_TILE.req.open("GET", sURL, true);
		AJAX_TILE.req.send("");
	}

}

// returns an object if it exists in the current DOM displayed, or null if it doesn't
function buildObj(sObject){
	// if netscape build the correct path to the element in the DOM
	if (!document.all){
		var aObjTree = sObject.split("."); // split and store the ie version of the DOM tree
		var sTree = "";

		// when the tree is long, construct a new tree out of the split apart ie tree
		if (aObjTree.length > 1){
			for (var i=0; i<aObjTree.length; i++){
				if ((i+1)%2 == 0) sTree += ".document."; // inserts ref to the DOM document
				if (i < aObjTree.length -1) sTree += aObjTree[i]; // skips the last element
			}

		// just start a basic NS tree
		} else sTree += "document.";

		// reconstruct the sObject for a correct NS path to the element
		sObject = (sTree + "getElementById('"+ aObjTree[aObjTree.length -1] +"')");
	}

	// return the element or null if it doesn't exist
	return oCreatedObj = (eval("typeof("+sObject+")") != "undefined")? (eval(sObject)):null;
}

//  Legacy Javascript for enforcing maxlength
function maxlengthCheck(txt, maxlength){
    if(txt.value.length > maxlength){
        txt.value = txt.value.substring(0,maxlength);
    }
}

/* ************************************************************************************************** */
/* flyopen.js */
/* ************************************************************************************************** */

function flyopen(width, height){
    width = (width && !isNaN(width))? width:null;
    height = (height && !isNaN(height))? height:null;
    var winURL = (arguments[2])? arguments[2]:null;
    var winName = (arguments[3])? arguments[3]:"generic";
    var noFocus = (arguments[4])? true:false;

	//only launch the window if we've got a width, height and url
	if (width && height && winURL){
        var ieIncrement = ((navigator.appName+"").indexOf("Netscape") == -1)? 15:0;
        eval(winName+"=window.open('"+ winURL +"','"+ winName +"','resizable=yes,scrollbars=yes,width="+ (width + ieIncrement) +",height="+ (height + ieIncrement) +",top=5,left=75')");
        if (!noFocus) eval("window."+ winName +".focus()");
	}
}

/**
 * Opens a DHTML window near the source element that spawned the window.  
 * @param {event} event The event object responsible for spawning the window.
 * @param {Object or String} This can either be a DOM element or a simple string.
 * @param {String} sID An optional string id that can be used to ID the window.
 * @param {String} sTitle An optional string that can be used for title bar text.
 * @param {Int} iWidth An optional Int used to specify the width of the window.
 * @param {Int} iHeight An optional Int used to specify the height of the window.
 * @param {String} sScrolling An optional string used to specify the scrolling type (auto, scroll, hidden).
 *
 * example calls:
 * A DOM element is passed along with an ID and a Title. The width and height are based on the content passed in. 
 * dhtmlFlyopen(event, document.getElementById('priceBreakDisplay'), 'priceBreakWindow', 'Price Breaks:')
 * 
 * A string is passed in along with an ID, Title, Width, Height, and Scrolling preference. 
 * dhtmlFlyopen(event, 'this is some test text this is some test text', 'infoWindow', 'Test Title', 200, 100, 'auto')
 */
function dhtmlFlyopen(event, content, sID, sTitle, iWidth, iHeight, sScrolling){
	// check for ie running on a mac
	var bMacIE = (navigator.appName.indexOf("Microsoft") != -1 && navigator.platform.indexOf("Mac") != -1)? true:false;
	// check for Opera
	var bOpera = (navigator.appName.indexOf("Opera") != -1 && document.all)? true:false;
	// get a DOM pointer to the body element
	var oBody = document.getElementsByTagName("body");
	// if they've provided an id use that for the new DHTML window id, otherwise use a gerneric id
	var sWindowID = (sID && sID.length>0)? sID:"divWindow";
	// check to see if this DHTML window element already exists
	var bWindowAlreadyExists = (document.getElementById(sWindowID))? true:false;
	// use the old DHTML window element, or make a new one
	var dhtmlWindow = (bWindowAlreadyExists)? document.getElementById(sWindowID):document.createElement("div");
	// get the event src element, so we can position the window later 
	var srcElement = (event.srcElement)? event.srcElement:event.target;
	// if the srcElement is a text node, get it's parent/container node 
	srcElement = (srcElement.nodeType == 3)? srcElement.parentNode:srcElement;
	// set content as a string, if there's innerHTML use that, otherwise assume content is already a string	
	content = (content.innerHTML)? content.innerHTML:content;
	// place holder for the windows total content
	var sWindowContent = "";
	// if they've provided a title for the window use that
	var sWindowTitle =  (sTitle)? sTitle:"";
	
	// if they've provided width's and heights, 
	// reset the width and height to account for scrollbars
	iWidth = (iWidth && document.all)? iWidth:(iWidth-25);
	iHeight = (iHeight && document.all)? iHeight:(iHeight-25);
	
	// build the local style, used for the window's content section,
	// if they've provied width, height, or scrolling options
	var sWidth = (iWidth)? "width:"+iWidth+"px;":"";
	var sHeight = (iHeight)? "height:"+iHeight+"px;":"";
	var sOverflow = (sScrolling)? "overflow:"+sScrolling+";":"";
	var sLocalStyle = (iWidth || iHeight || sScrolling)? "style='"+sWidth + sHeight + sOverflow+"'":"";
	
	// build the window's title bar, close button, and content area 
	sWindowContent += "<div class='divWindowTitleBar'><button class='divWindowCloseButton' onclick='closeDhtmlFlyopen(this)'>X</button></div>"
	sWindowContent += "<div class='divWindowTitleBarText'>"+ sWindowTitle +"</div>";
	sWindowContent += "<div class='divWindowContent' "+ sLocalStyle +"><table cellpadding=0 cellspacing=0 border=0><tr><td>"+ content +"</td></tr></table></div>"
	sWindowContent += (document.all && !bMacIE && !bOpera)? "<iframe class='divWindowShieldFrame'></iframe>":"";
	
	// only set the window's id and className if it's a new window
	if (!bWindowAlreadyExists) dhtmlWindow.id= sWindowID;
	if (!bWindowAlreadyExists) dhtmlWindow.className="divWindow";
	
	// set the rest of the generic properties for the window
	dhtmlWindow.innerHTML = sWindowContent;
	dhtmlWindow.display = "block";
	dhtmlWindow.style.visibility="visible";
	dhtmlWindow.style.position = "absolute";
	dhtmlWindow.style.top = srcElement.offsetTop;
	dhtmlWindow.style.left = srcElement.offsetLeft;
	dhtmlWindow.style.zIndex = 10;
	
	// only append the window element to the body element if it's a new window
	if (!bWindowAlreadyExists) oBody[0].appendChild(dhtmlWindow);
}

/**
 * Closes a DHTML window called by the window's close button element.  
 * @param {Object} oSrcElement The close button element contained within the window.
 */
function closeDhtmlFlyopen(oSrcElement){
	// get a pointer to the DHTML window based on the close button
	var dhtmlWindow = oSrcElement.parentNode.parentNode;
	
	// hide the DHTML window
	dhtmlWindow.display = "none";
	dhtmlWindow.style.visibility="hidden";
	dhtmlWindow.innerHTML = "";
}

/* ************************************************************************************************** */
/* cleartext.js */
/* ************************************************************************************************** */

/* clears text of passed in object */
function clearIt(txt) {
    txt.value = "";
}
