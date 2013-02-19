// Copyright (c) Baris Tevfik
// refer to License.txt

//update how many characters left
function limitText(limitNum) {
		document.getElementById('countdown').value = limitNum - document.getElementById('messageBox').value.length;
}

//call after load
function afterLoad()
{
	//scroll to the bottom of the page
    var box = document.getElementById('outputBox');
    box.scrollTop = box.scrollHeight;
    //focus to the text area and clear it 
	var mBox = document.getElementById('messageBox');
	mBox.focus();
	mBox.value="";
	//reset the character counter
	var count = document.getElementById('countdown');
	count.value = "140";
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
window.onload=afterLoad(); 