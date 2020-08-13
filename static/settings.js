// Radio buttons PIC and FO
document.querySelector("#pic").onclick = function()
{
	if (document.querySelector("#fo").checked == true)
	{document.querySelector("#fo").checked = false;}
}
document.querySelector("#fo").onclick = function()
{
	if (document.querySelector("#pic").checked == true)
	{document.querySelector("#pic").checked = false;}
}

// Display RED warning message
function settings_msg_red(x)
{
	document.querySelector("#msg_settings").style.color = 'red';
	document.querySelector("#msg_settings").innerHTML = x;	
}
// Display RED warning message
function pass_msg_red(x)
{
	document.querySelector("#msg_password").style.color = 'red';
	document.querySelector("#msg_password").innerHTML = x;	
}
// Display RED warning message
function prevexp_msg_red(x)
{
	document.querySelector("#msg_prevexp").style.color = 'red';
	document.querySelector("#msg_prevexp").innerHTML = x;	
}

// Save new settings
function save_settings()
{
	// Check name
	if (document.querySelector("#pil_name").value == "") 
		{ settings_msg_red("Enter your name"); return;}

	// Save role
	let role;
	if (document.querySelector("#pic").checked) 
		{ role = "pic"; }
	else if (document.querySelector("#fo").checked) 
		{ role = "fo"; }
	else 
		{ settings_msg_red("Select either PIC or FO"); return;}

	// Display response from server
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
	    if (this.readyState == 4 && this.status == 200) {
	       // If ERROR is returned
			if (xhttp.responseText[0] == "E"){
				document.querySelector("#msg_settings").style.color = 'red';
				document.getElementById("msg_settings").innerHTML = xhttp.responseText; }
			else{
				document.querySelector("#msg_settings").style.color = 'green';
				document.getElementById("msg_settings").innerHTML = xhttp.responseText; }
	    }
	};
	// Send data to server	
	xhttp.open("POST", "/settings", true);
	xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xhttp.send("todo=settings&role=" + role + "&name=" + document.querySelector("#pil_name").value);
}

// Change password
function change_pass()
{
	// Check password entries
	if (document.querySelector("#old_pass").value == '')
		{pass_msg_red("Old password is missing"); return;}
	else if (document.querySelector("#new_pass").value == '')
		{pass_msg_red("Provide new password"); return;}
	else if (document.querySelector("#new_pass").value != document.querySelector("#conf_new_pass").value)
		{pass_msg_red("New password does not match New password confirmation"); return;}

	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
	    if (this.readyState == 4 && this.status == 200) {
	       // ERROR
			if (xhttp.responseText[0] == "E"){
				document.querySelector("#msg_password").style.color = 'red';
				document.getElementById("msg_password").innerHTML = xhttp.responseText; }
			else{
				document.querySelector("#msg_password").style.color = 'green';
				document.getElementById("msg_password").innerHTML = xhttp.responseText; 
				document.querySelector("#old_pass").value = "";
				document.querySelector("#new_pass").value = "";
				document.querySelector("#conf_new_pass").value = ""; }
	    }
	};
	
	xhttp.open("POST", "/settings", true);
	xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xhttp.send("todo=password&old_pass=" + document.querySelector("#old_pass").value + "&new_pass=" + document.querySelector("#new_pass").value + "&conf_new_pass=" + document.querySelector("#conf_new_pass").value);
}

// Add prevexp
function add_prevexp()
{
	if (document.querySelector("#tot_time").value == '')
		{prevexp_msg_red("Operating time is missing. Enter PIC/FO/Exam/Instr/DUAL"); 
		document.querySelector("#pic_time").focus(); return;}

	let x="";
	x = document.querySelector("#pic_time").value;
	for (let i=0; i < x.length; i++)
	{
		if (x[i] >= 0 && x[i] <= 9){continue;}
		else if (x[i] == ':'){continue;}
		else{prevexp_msg_red("PIC time is of invalid format");
		document.querySelector("#pic_time").focus(); return;}
	}
	x = document.querySelector("#fo_time").value;
	for (let i=0; i < x.length; i++)
	{
		if (x[i] >= 0 && x[i] <= 9){continue;}
		else if (x[i] == ':'){continue;}
		else{prevexp_msg_red("FO time is of invalid format");
		document.querySelector("#fo_time").focus(); return;}
	}
	x = document.querySelector("#me_fan").value;
	for (let i=0; i < x.length; i++)
	{
		if (x[i] >= 0 && x[i] <= 9){continue;}
		else if (x[i] == ':'){continue;}
		else{prevexp_msg_red("ME Turbofan time is of invalid format");
		document.querySelector("#me_fan").focus(); return;}
	}
	x = document.querySelector("#me_prop").value;
	for (let i=0; i < x.length; i++)
	{
		if (x[i] >= 0 && x[i] <= 9){continue;}
		else if (x[i] == ':'){continue;}
		else{prevexp_msg_red("Me Turboprop time is of invalid format");
		document.querySelector("#me_prop").focus(); return;}
	}
	x = document.querySelector("#me_pist").value;
	for (let i=0; i < x.length; i++)
	{
		if (x[i] >= 0 && x[i] <= 9){continue;}
		else if (x[i] == ':'){continue;}
		else{prevexp_msg_red("ME Piston time is of invalid format");
		document.querySelector("#me_pist").focus(); return;}
	}
	x = document.querySelector("#se_fan").value;
	for (let i=0; i < x.length; i++)
	{
		if (x[i] >= 0 && x[i] <= 9){continue;}
		else if (x[i] == ':'){continue;}
		else{prevexp_msg_red("SE Turbofan time is of invalid format");
		document.querySelector("#se_fan").focus(); return;}
	}
	x = document.querySelector("#se_prop").value;
	for (let i=0; i < x.length; i++)
	{
		if (x[i] >= 0 && x[i] <= 9){continue;}
		else if (x[i] == ':'){continue;}
		else{prevexp_msg_red("SE Turboprop time is of invalid format");
		document.querySelector("#se_prop").focus(); return;}
	}
	x = document.querySelector("#se_pist").value;
	for (let i=0; i < x.length; i++)
	{
		if (x[i] >= 0 && x[i] <= 9){continue;}
		else if (x[i] == ':'){continue;}
		else{prevexp_msg_red("SE Piston time is of invalid format");
		document.querySelector("#se_pist").focus(); return;}
	}
	x = document.querySelector("#ifr").value;
	for (let i=0; i < x.length; i++)
	{
		if (x[i] >= 0 && x[i] <= 9){continue;}
		else if (x[i] == ':'){continue;}
		else{prevexp_msg_red("IFR time is of invalid format");
		document.querySelector("#ifr").focus(); return;}
	}
	x = document.querySelector("#vfr").value;
	for (let i=0; i < x.length; i++)
	{
		if (x[i] >= 0 && x[i] <= 9){continue;}
		else if (x[i] == ':'){continue;}
		else{prevexp_msg_red("VFR time is of invalid format");
		document.querySelector("#vfr").focus(); return;}
	}
	x = document.querySelector("#night").value;
	for (let i=0; i < x.length; i++)
	{
		if (x[i] >= 0 && x[i] <= 9){continue;}
		else if (x[i] == ':'){continue;}
		else{prevexp_msg_red("Night time is of invalid format");
		document.querySelector("#night").focus(); return;}
	}
	x = document.querySelector("#instr").value;
	for (let i=0; i < x.length; i++)
	{
		if (x[i] >= 0 && x[i] <= 9){continue;}
		else if (x[i] == ':'){continue;}
		else{prevexp_msg_red("Instructor time is of invalid format");
		document.querySelector("#instr").focus(); return;}
	}
	x = document.querySelector("#exam").value;
	for (let i=0; i < x.length; i++)
	{
		if (x[i] >= 0 && x[i] <= 9){continue;}
		else if (x[i] == ':'){continue;}
		else{prevexp_msg_red("Examiner time is of invalid format");
		document.querySelector("#exam").focus(); return;}
	}
	x = document.querySelector("#dual").value;
	for (let i=0; i < x.length; i++)
	{
		if (x[i] >= 0 && x[i] <= 9){continue;}
		else if (x[i] == ':'){continue;}
		else{prevexp_msg_red("DUAL (training) time is of invalid format");
		document.querySelector("#dual").focus(); return;}
	}
	document.querySelector("#key").value = ran_key();
	document.getElementById("f_prevexp").submit();
}


// Calculate TOTAL PREVIOUS TIME
function calc_tot_time()
{	
  var tot_time = [ 0, 0 ]
  var max = tot_time.length

  var a = (document.querySelector("#pic_time").value || '').split(':')
  var b = (document.querySelector("#fo_time").value || '').split(':')
  var c = (document.querySelector("#exam").value || '').split(':')
  var d = (document.querySelector("#instr").value || '').split(':')
  var e = (document.querySelector("#dual").value || '').split(':')

  // normalize time values
  for (var i = 0; i < max; i++) {
    a[i] = isNaN(parseInt(a[i])) ? 0 : parseInt(a[i])
    b[i] = isNaN(parseInt(b[i])) ? 0 : parseInt(b[i])
    c[i] = isNaN(parseInt(c[i])) ? 0 : parseInt(c[i])
    d[i] = isNaN(parseInt(d[i])) ? 0 : parseInt(d[i])
    e[i] = isNaN(parseInt(e[i])) ? 0 : parseInt(e[i])
  }

  // store time values
  for (var i = 0; i < max; i++) {
    tot_time[i] = a[i] + b[i] + c[i] + d[i] + e[i]
  }

  var hours = tot_time[0]
  var minutes = tot_time[1]

  if (minutes >= 60) {
    var h = (minutes / 60) << 0
    hours += h
    minutes -= 60 * h
  }
	document.querySelector("#tot_time").value = hours + ':' + ('0' + minutes).slice(-2)
}
