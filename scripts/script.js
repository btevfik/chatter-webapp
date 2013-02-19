//update how many characters left
function limitText(limitNum) {
		document.getElementById('countdown').value = limitNum - document.getElementById('messageBox').value.length;
}

//scroll bottom of the page to see the last comment
function afterSubmit()
{
    var box = document.getElementById('outputBox');
    box.scrollTop = box.scrollHeight; 
	var mBox = document.getElementById('messageBox');
	mBox.focus();
	mBox.value="";
}

/* next two jquery handlers achieve the effect of clicking the chatter button when enter is pressed */

//if enter is pressed, trigger button click
$("#messageBox").keydown(function(event){
    if(event.keyCode == 13){
        $("#submitButton").click();
        $("#submitButton").addClass('activate');
    }
});

//if enter is released, remove class
$("#messageBox").keyup(function(event){
    if(event.keyCode == 13){
        $("#submitButton").removeClass('activate');
    }
});

//on window load run this
window.onload=afterSubmit(); 