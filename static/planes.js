// Display RED warning message
function pln_msg_red(x)
{
	document.querySelector("#plane_msg").style.color = 'red';
	document.querySelector("#plane_msg").innerHTML = x;	
}

// Check required inputs for adding flight are present
function submit_planes()
{
	if (document.querySelector("#tail").value == '')
		{pln_msg_red("Aircraft registration is missing");}
	else if (document.querySelector("#type").value == '')
		{pln_msg_red("Aircraft type is missing");}
	else if (document.querySelector("#class").value == '')
		{pln_msg_red("Please select JET/PROP/PISTON");}
	else
        {
			document.querySelector("#key").value = ran_key();
			document.getElementById("f_addpln").submit();
		}
}

function set_id(x)
{	
	document.querySelector("#pln_id").value = x;
	document.querySelector("#todo").value = "display";
	document.getElementById("f_addpln").submit();
}

function col_selected(x)
{
	x = "#row" + x;
	document.querySelector(x).style.color = 'blue';	
}
function col_norm(x)
{
	x = "#row" + x;
	document.querySelector(x).style.color = 'black';	
}

function update_plane()
{
	document.querySelector("#todo").value = "update";
	submit_planes();
}

function add_plane()
{
	document.querySelector("#todo").value = "add";
	submit_planes();
}
