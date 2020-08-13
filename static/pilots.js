
// Check required inputs for adding flight are present
function submit_pilots()
{
	if (document.querySelector("#name").value == '')
		{alert("Name of the pilot is missing");}
	else
        {
			document.querySelector("#key").value = ran_key();
			document.getElementById("f_addpil").submit();
		}
}

function set_id(x)
{	
	document.querySelector("#pil_id").value = x;
	document.querySelector("#todo").value = "display";
	document.getElementById("f_addpil").submit();
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

function update_pilot()
{
	document.querySelector("#todo").value = "update";
	submit_pilots();
}

function add_pilot()
{
	document.querySelector("#todo").value = "add";
	submit_pilots();
}
