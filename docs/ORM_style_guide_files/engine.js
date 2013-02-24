// JavaScript Document
/* <![CDATA[ */
function getCookie(name) {
  var dc = document.cookie;
  var prefix = name + "=";
  var begin = dc.indexOf("; " + prefix);
  if (begin == -1) {
    begin = dc.indexOf(prefix);
    if (begin != 0) return null;
  } else
    begin += 2;
  var end = document.cookie.indexOf(";", begin);
  if (end == -1)
    end = dc.length;
  return unescape(dc.substring(begin + prefix.length, end));
}

// list all show/hide element IDs here
menus_array = new Array ('mac', 'business','training','databases','design','audiovideo','photography','hardware','homeoffice','microsoft','mobile','sysadmin','os','programming','science','security','softwareengineering','web','partnertopics','companies','showcases','fulldesc','reviews');
menus_status_array = new Array ();// remember switches
img_close = 'rollup';
img_open = 'rolldown';

function toggleSheet(theid) {
  if (document.getElementById) {
    var switch_id = document.getElementById(theid);
    var imgid = theid+'Button';
    var button_id = document.getElementById(imgid);
    if (menus_status_array[theid] != 'show') {
      button_id.className = 'rolldown';
      switch_id.className = 'showSwitch';
	  menus_status_array[theid] = 'show';
	  document.cookie = theid+'=show';
    } else {
      button_id.className = 'rollup';
      switch_id.className = 'hideSwitch';
	  menus_status_array[theid] = 'hide';
	  document.cookie = theid+'=hide';
    }
  }
}

function setMenu() { // read cookies and set menus to last visited state
  if (document.getElementById) {
    for (var i=0; i < menus_array.length; i++) {
      var idname = menus_array[i];
      if (document.getElementById(idname)) {
		var switch_id = document.getElementById(idname);
		var imgid = idname+'Button';
		var button_id = document.getElementById(imgid);
		// alert(imgid);
		if (getCookie(idname) == 'show') {
		  button_id.className = 'rolldown';
		  switch_id.className = 'showSwitch';
		  menus_status_array [idname] = 'show';
		} else {
		  button_id.className = 'rollup';
		  switch_id.className = 'hideSwitch';
		  menus_status_array [idname] = 'hide';
		}
	  } // else { alert("Switch '"+idname+"' is not present on this page."); }
    }
  }
}
/* ]]> */
