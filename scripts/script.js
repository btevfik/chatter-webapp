//update how many characters left
function limitText(limitField, limitCount, limitNum) {
		limitCount.value = limitNum - limitField.value.length;
}

//scroll bottom of the page to see the last comment
function scrollBottom()
{
var box = document.getElementById("outputBox");
box.scrollTop = box.scrollHeight; 
}

//on window load run this
window.onload=scrollBottom(); 